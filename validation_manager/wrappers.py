from functools import wraps
from flask_login import current_user
from flask import abort, jsonify, request, flash, url_for, make_response
from werkzeug.utils import redirect
from settings import SECRET_KEY
from models import User
import jwt
from api.functions import is_key_blocked
from models import ApiKey
from validation_manager.functions import get_route_status
from context_manager import newsletter_functionality
from newsletter.functions import authors_allowed
from settings import API_METHODS


def logout_required(func):
    """Checks whether user is logged out or raises error 401."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            abort(401)
        return func(*args, **kwargs)

    return wrapper


def admin_only(func):
    """Checks whether user is admin or raises error 403."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated is False or current_user.admin is False:
            abort(403)
        return func(*args, **kwargs)

    return wrapper


def staff_only(func):
    """Checks whether a user is a staff member or raises 403 error."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated is False:
            abort(401)
        if current_user.admin is False and current_user.author is False:
            abort(403)
        return func(*args, **kwargs)

    return wrapper


def api_validation_factory(newsletter=False, *args, **kwargs):
    def validate_api_route(func):
        """Checks whether a route is available or raises the appropriate error."""

        def wrapper(*args, **kwargs):
            func_name = func.__name__
            if func_name in API_METHODS.keys() and not newsletter:
                func_name = API_METHODS[func_name]
            elif newsletter:
                func_name = 'newsletter_sendout'
            route_status = get_route_status(func_name)
            if route_status == 'blocked':
                return make_response(jsonify(response={"Route Blocked": "The requested route is blocked."}), 503)
            elif route_status == 'unavailable':
                return make_response(
                    jsonify(response={"Route Configuration Unavailable": "The requested route configuration"
                                                                         " is unavailable."}), 503)
            else:
                return func(*args, **kwargs)

        wrapper.__name__ = func.__name__
        return wrapper

    return validate_api_route


def validate_api_key(func):
    """Checks whether an api key is valid or raises the appropriate error."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('api_key')
        requested_key = ApiKey.query.filter_by(api_key=api_key).first()
        if requested_key:
            if is_key_blocked(api_key):
                return jsonify(response={"Forbidden": "Blocked API Key."}), 403
            return func(*args, **kwargs)
        else:
            return jsonify(response={"Malformed API Request": "Invalid API Key."}), 401

    return wrapper


def newsletter_route(func):
    """Checks whether the newsletter functionality is enabled or redirects the user to the home page."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        functionality = newsletter_functionality('validation')
        if functionality:
            return func(*args, **kwargs)
        else:
            flash("The newsletter functionality is currently disabled.")
            return redirect(url_for('home.home_page', category='danger'))

    return wrapper


def newsletter_staff(func):
    """Checks whether the current user matches the permission criteria of sending out newsletters or raises 403."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        allow_authors = authors_allowed('validation')
        if current_user.is_authenticated:
            if current_user.admin or current_user.author and allow_authors:
                return func(*args, **kwargs)
            else:
                return abort(403)
        else:
            return abort(403)

    return wrapper


def token_required(func):
    """Checks whether the given token is valid or raises the appropriate error."""

    def wrapper(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return make_response(jsonify(response="Missing token."), 401)
        data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        requesting_user = User.query.get(data['user']['user_id'])

        if requesting_user:
            requested_key = ApiKey.query.filter_by(developer=requesting_user).first()
            if requested_key:
                return func(*args, **kwargs, requesting_user=requesting_user)
            else:
                return make_response(
                    jsonify(response="Your account must be set as a developer account to make API requests."), 403)
        else:
            return make_response(jsonify(response="Could not find the requested user."), 404)

    wrapper.__name__ = func.__name__
    return wrapper


def post_id_required(func):
    """Checks whether a post id was provided when making a request to a route, or raises 400."""

    def wrapper(*args, **kwargs):
        post_id = request.args.get('post_id')
        if post_id:
            return func(*args, **kwargs, post_id=post_id)
        else:
            return make_response(jsonify(response="No Post ID specified."), 400)

    wrapper.__name__ = func.__name__
    return wrapper
