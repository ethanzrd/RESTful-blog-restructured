from flask import Blueprint, request, abort, jsonify, url_for, render_template, flash, make_response
from flask_login import login_required, current_user
from werkzeug.utils import redirect
from forms import ApiGenerate
from post_system.post.api_validations import validate_post_addition
from validation_manager.wrappers import api_validation_factory, admin_only, validate_api_key, token_required, \
    post_id_required
from models import ApiKey, User, BlogPost
from extensions import db
from post_system.post.functions import get_posts, get_post_dict
import random
from users_manager.functions import get_users_dict
from api.functions import add_key, block_api_key, unblock_api_key, handle_post_edition, handle_token_generation, \
    handle_post_deletion, handle_newsletter_sendout
from flask_restful import Resource
from extensions import flask_api

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
@api_validation_factory()
def all_posts():
    api_key = request.headers.get('api_key')
    try:
        requesting_user = ApiKey.query.filter_by(api_key=api_key).first()
        requesting_user.all_posts += 1
    except AttributeError:
        return abort(500)
    posts = get_posts()
    posts_dict = [get_post_dict(post) for post in posts]
    db.session.commit()
    return jsonify(response=posts_dict), 200


@api.route('/random-post')
@validate_api_key
@api_validation_factory()
def random_post():
    api_key = request.headers.get('api_key')
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
@api_validation_factory()
def all_users():
    api_key = request.headers.get('api_key')
    try:
        requesting_user = ApiKey.query.filter_by(api_key=api_key).first()
        requesting_user.all_users += 1
    except AttributeError:
        return abort(500)
    users_dict = get_users_dict()
    db.session.commit()
    return jsonify(response=users_dict), 200


@api.route('/random-user')
@validate_api_key
@api_validation_factory()
def random_user():
    api_key = request.headers.get('api_key')
    try:
        requesting_user = ApiKey.query.filter_by(api_key=api_key).first()
        requesting_user.random_user += 1
    except AttributeError:
        return abort(500)
    try:
        selected_user = random.choice(User.query.all())
        user_dict = get_users_dict(selected_user)
    except IndexError:
        user_dict = {}
    db.session.commit()
    return jsonify(response=user_dict)


@api.route('/generate-token')
def generate_token():
    auth = request.authorization
    return handle_token_generation(auth=auth)


class Post(Resource):

    @api_validation_factory()
    @post_id_required
    def get(self, post_id):
        requested_post = BlogPost.query.get(post_id)
        if requested_post:
            return make_response(jsonify(response=get_post_dict(requested_post)), 200)
        return make_response(jsonify(response="Could not find a post with the specified ID."), 404)

    @api_validation_factory()
    @token_required
    def post(self, requesting_user):
        if requesting_user.admin or requesting_user.author:
            new_post_json = request.get_json()
            return validate_post_addition(post_json=new_post_json, requesting_user=requesting_user)
        else:
            return make_response(jsonify(response="You're unauthorized to access this route."), 403)

    @api_validation_factory()
    @token_required
    @post_id_required
    def put(self, requesting_user, post_id):
        return handle_post_edition(requesting_user=requesting_user, post_id=post_id,
                                   changes_json=request.get_json())

    @api_validation_factory()
    @token_required
    @post_id_required
    def delete(self, requesting_user, post_id):
        return handle_post_deletion(requesting_user=requesting_user, post_id=post_id)


class Newsletter(Resource):

    @api_validation_factory(newsletter=True)
    @token_required
    def post(self, requesting_user):
        return handle_newsletter_sendout(requesting_user=requesting_user, newsletter_json=request.get_json())


flask_api.add_resource(Post, '/api/post', '/api/post')
flask_api.add_resource(Newsletter, '/api/newsletter')
