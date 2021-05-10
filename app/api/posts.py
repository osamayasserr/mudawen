from flask import request, current_app, url_for, jsonify, g
from . import api
from .decorators import requires_permission
from ..models import Post, Permission, User
from .errors import forbidden
from .. import db


@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['MUDAWEN_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'page': page,
        'posts_per_page': pagination.per_page,
        'total_posts': pagination.total
    })


@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


@api.route('/posts/', methods=['POST'])
@requires_permission(Permission.WRITE)
def add_post():
    post = Post.from_json(request.get_json())
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
        {'Location': url_for('api.get_post', id=post.id)}


@api.route('/posts/<int:id>', methods=['PUT'])
@requires_permission(Permission.WRITE)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if post.author != g.current_user and \
            not g.current_user.can(Permission.ADMIN):
        return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())


@api.route('/users/<int:id>/posts/')
def get_user_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['MUDAWEN_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return jsonify({
        'page': page,
        'posts_per_page': pagination.per_page,
        'total_user_posts': pagination.total,
        'posts': [post.to_json() for post in posts]
    })
