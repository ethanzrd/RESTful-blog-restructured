from flask import Blueprint, request, abort, jsonify, url_for, render_template, flash
from flask_login import login_required, current_user
from werkzeug.utils import redirect

from forms import ApiGenerate
from validation_manager.wrappers import validate_api_route, admin_only, validate_api_key
from models import ApiKey
from extensions import db
from post_system.post.functions import get_posts, get_post_dict
import random
from users_manager.functions import get_users_dict
from api.functions import add_key, block_api_key, unblock_api_key

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/generate-key', methods=['GET', 'POST'])
@login_required
def generate_key():
    if ApiKey.query.filter_by(developer=current_user).first() is None:
        form = ApiGenerate()
        if form.validate_on_submit():
            add_key(form)
            return redirect(url_for('user_operations.user_page', user_id=current_user.id, current_mode='api'))
        return render_template('config.html', config_title="API Key Generation",
                               config_desc="Generate an API Key to use our API Service.", form=form,
                               config_func="api.generate_key")
    else:
        flash("You already have an API key.")
        return redirect(url_for('user_operations.user_page', user_id=current_user.id, current_mode='api'))


@api.route('/block-key/<int:key_id>')
@admin_only
def block_key(key_id):
    requested_key = ApiKey.query.get(key_id)
    if requested_key:
        return block_api_key(requested_key)
    else:
        return abort(404)


@api.route('/unblock-key/<int:key_id>')
@admin_only
def unblock_key(key_id):
    requested_key = ApiKey.query.get(key_id)
    if requested_key:
        return unblock_api_key(requested_key)
    else:
        return abort(404)


@api.route('/all-posts')
@validate_api_key
@validate_api_route
def all_posts():
    api_key = request.args.get('api_key')
    try:
        requesting_user = ApiKey.query.filter_by(api_key=api_key).first()
        requesting_user.all_posts += 1
    except AttributeError:
        return abort(500)
    posts = get_posts()
    posts_dict = {posts.index(post) + 1: get_post_dict(post)
                  for post in posts}
    db.session.commit()
    return jsonify(response=posts_dict), 200


@api.route('/random-post')
@validate_api_key
@validate_api_route
def random_post():
    api_key = request.args.get('api_key')
    try:
        requesting_user = ApiKey.query.filter_by(api_key=api_key).first()
        requesting_user.random_post += 1
    except AttributeError:
        return abort(400)
    try:
        post = random.choice(get_posts())
    except IndexError:
        post_dict = {}
    else:
        post_dict = get_post_dict(post)
    db.session.commit()
    return jsonify(response=post_dict), 200


@api.route('/users')
@validate_api_key
@validate_api_route
def all_users():
    api_key = request.args.get('api_key')
    try:
        requesting_user = ApiKey.query.filter_by(api_key=api_key).first()
        requesting_user.all_users += 1
    except AttributeError:
        return abort(500)
    users_dict = get_users_dict()
    db.session.commit()
    return users_dict
