from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User, Post


@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@api.route('/users/<int:id>/timeline/')
def get_user_following_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.following_posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['MUDAWEN_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return jsonify({
        'user_url': url_for('api.get_user', id=id, _external=True),
        'page': page,
        'following_posts': [post.to_json() for post in posts],
        'total_timeline_posts': pagination.total
    })
