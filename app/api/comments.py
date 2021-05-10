from flask import jsonify, request, current_app, url_for, g
from . import api
from .errors import bad_request
from .decorators import requires_permission
from ..models import Comment, Post, User, Permission
from app import db


@api.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    if comment.disabled:
        return bad_request('Comment disabled by moderator')
    return jsonify(comment.to_json())


@api.route('/comments/')
def get_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.filter_by(
        disabled=False).order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['MUDAWEN_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return jsonify({
        'page': page,
        'comments': [comment.to_json() for comment in comments],
        'total_comments': pagination.total
    })


@api.route('/posts/<int:id>/comments/')
def get_post_comments(id):
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.filter_by(
        disabled=False).order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['MUDAWEN_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return jsonify({
        'page': page,
        'post_author': url_for('api.get_user', id=post.author_id),
        'comments': [comment.to_json() for comment in comments],
        'total_post_comments': pagination.total
    })


@api.route('/posts/<int:id>/comments/', methods=['POST'])
@requires_permission(Permission.COMMENT)
def post_comment(id):
    post = Post.query.get_or_404(id)
    comment = Comment.from_json(request.get_json())
    comment.author = g.current_user
    comment.post = post
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 201, \
        {'Location': url_for('api.get_comment', id=comment.id)}


@api.route('/users/<int:id>/comments/')
def get_user_comments(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.comments.filter_by(
        disabled=False).order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['MUDAWEN_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return jsonify({
        'page': page,
        'username': user.username,
        'comments': [comment.to_json() for comment in comments],
        'total_user_comments': pagination.total
    })
