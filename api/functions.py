import datetime
import random
import string
from flask import abort, flash, url_for, jsonify, request, make_response
from jwt import encode
from werkzeug.security import check_password_hash
from werkzeug.utils import redirect

from app_config import SECRET_KEY
from context_manager import newsletter_functionality
from models import ApiKey, Notification, BlogPost, User
from extensions import db
from flask_login import current_user
from html2text import html2text

from newsletter.functions import authors_allowed, validate_newsletter_distribution
from post_system.post.api_validations import validate_post_deletion
from post_system.post.api_validations import validate_post_edition
from users_manager.functions import get_user_information
from utils import generate_date


def generate_new_key():
    def get_new():
        new = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
        return new

    while True:
        new_key = get_new()
        if any([key.api_key for key in ApiKey.query.all() if key == new_key]):
            continue
        else:
            break
    return new_key


def is_key_blocked(api_key):
    try:
        return ApiKey.query.filter_by(api_key=api_key).first().blocked
    except AttributeError:
        return False


def add_key(form):
    try:
        new_key = ApiKey(developer=current_user, occupation=form.occupation.data, application=form.application.data,
                         usage=html2text(form.usage.data), api_key=generate_new_key())
    except AttributeError:
        return abort(400)
    db.session.add(new_key)
    db.session.commit()


def block_api_key(requested_key):
    try:
        if requested_key.blocked is False:
            requested_key.blocked = True
            new_notification = Notification(user=requested_key.developer, by_user=current_user.email,
                                            body=f"Your API Key has been blocked by {current_user.name}.",
                                            date=generate_date(), category='block', user_name=current_user.name)
            db.session.add(new_notification)
            db.session.commit()
            flash("This API Key has been blocked successfully.")
            return redirect(
                url_for('user_operations.user_page', current_mode='api', user_id=requested_key.developer_id))
        else:
            flash("This API Key is already blocked.")
            return redirect(
                url_for('user_operations.user_page', current_mode='api', user_id=requested_key.developer_id))
    except AttributeError:
        return abort(400)


def unblock_api_key(requested_key):
    try:
        if requested_key.blocked is True:
            requested_key.blocked = False
            new_notification = Notification(user=requested_key.developer, by_user=current_user.email,
                                            body=f"Your API Key has been unblocked by {current_user.name}.",
                                            date=generate_date(), category='unblock', user_name=current_user.name)
            db.session.add(new_notification)
            db.session.commit()
            flash("This API Key has been unblocked successfully.")
            return redirect(
                url_for('user_operations.user_page', current_mode='api', user_id=requested_key.developer_id))
        else:
            flash("This API Key is not blocked.")
            return redirect(
                url_for('user_operations.user_page', current_mode='api', user_id=requested_key.developer_id))
    except AttributeError:
        return abort(400)


def handle_token_generation(auth):
    if auth and auth.username and auth.password:
        requested_user = User.query.filter_by(email=auth.username).first()
        if requested_user:
            if check_password_hash(requested_user.password, auth.password):
                token = encode({'user': get_user_information(requested_user),
                                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                               SECRET_KEY, algorithm="HS256")
                return make_response(jsonify(token=token), 200)
            else:
                return make_response(jsonify(message="Incorrect Password."), 401)
        else:
            return make_response(jsonify(message="User not found."), 404)
    else:
        return make_response("Could not verify.", 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


def handle_post_edition(requesting_user, post_id, changes_json):
    if requesting_user.admin or requesting_user.author:
        requested_post = BlogPost.query.get(post_id)
        if requested_post:
            if requested_post.author == requesting_user:
                return validate_post_edition(requested_post=requested_post,
                                             changes_json=changes_json, requesting_user=requesting_user)
            else:
                return make_response(jsonify(response="You're not authorized to edit this post."), 403)
        else:
            return make_response(jsonify(response="Could not find a post with the specified ID."), 404)
    else:
        return make_response(jsonify(response="You're unauthorized to access this route."), 403)


def handle_post_deletion(requesting_user, post_id):
    if requesting_user.admin or requesting_user.author:
        requested_post = BlogPost.query.get(post_id)
        if requested_post:
            if requested_post.author == requesting_user or requesting_user.admin:
                return validate_post_deletion(requested_post=requested_post, requesting_user=requesting_user)
            else:
                return make_response(jsonify(response="You're unauthorized to delete this post."), 403)
        else:
            return make_response(jsonify(response="Could not find a post with the specified ID."), 404)
    else:
        return make_response(jsonify(response="You're unauthorized to access this route."), 403)


def handle_newsletter_sendout(requesting_user, newsletter_json):
    functionality = newsletter_functionality('validation')
    if functionality:
        if requesting_user.admin or requesting_user.author and authors_allowed('validation'):
            return validate_newsletter_distribution(requesting_user=requesting_user, newsletter_json=newsletter_json)
        else:
            return make_response(jsonify(response="You're unauthorized to access this route."), 403)
    else:
        return make_response(jsonify(resposne="The newsletter functionality is disabled."), 409)
