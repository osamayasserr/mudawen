from flask import render_template, flash, redirect, url_for, request, current_app, abort, make_response
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from ..models import User, Role, Post, Permission, Comment
from .. import db
from ..decorators import admin_required, requires_permission


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['MUDAWEN_QUERY_TIME_LIMIT']:
            current_app.logger.warning('Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n' %
                                       (query.statement, query.parameters, query.duration, query.context))
    return response


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    show_following = False
    if current_user.is_authenticated:
        show_following = bool(request.cookies.get('show_following', ''))
    if show_following:
        query = current_user.following_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['MUDAWEN_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           show_following=show_following, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['MUDAWEN_POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts, pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('main.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('main.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/posts/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm(post=post)
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('Comment added successfully')
        return redirect(url_for('main.post', id=id))
    comments = post.comments.order_by(Comment.timestamp.asc()).all()
    return render_template('post.html', posts=[post], comments=comments, form=form)


@main.route('/edit-post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('Post has been updated.')
        return redirect(url_for('main.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/delete-post/<int:id>')
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    user = post.author
    if current_user != post.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post has been deleted.')
    return redirect(url_for('main.user', username=user.username))


@main.route('/follow/<username>')
@login_required
@requires_permission(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('main.index'))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are now following {username}')
    return redirect(url_for('main.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@requires_permission(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('main.index'))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are not following {username} anymore.')
    return redirect(url_for('main.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['MUDAWEN_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title='Followers of',
                           endpoint='main.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.following.paginate(
        page, per_page=current_app.config['MUDAWEN_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    response = make_response(redirect(url_for('main.index')))
    response.set_cookie('show_following', '', max_age=30*24*60*60)
    return response


@main.route('/following')
@login_required
def show_following():
    response = make_response(redirect(url_for('main.index')))
    response.set_cookie('show_following', '1',  max_age=30*24*60*60)
    return response


@main.route('/moderate')
@login_required
@requires_permission(Permission.MODERATE)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['MUDAWEN_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', pagination=pagination,
                           comments=comments, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@requires_permission(Permission.MODERATE)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@requires_permission(Permission.MODERATE)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))
