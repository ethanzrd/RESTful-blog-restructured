import random
import string
from flask import abort, flash, url_for
from werkzeug.utils import redirect

from models import ApiKey, Notification
from extensions import db
from flask_login import current_user
from html2text import html2text

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
            return redirect(url_for('user_operations.user_page', current_mode='api', user_id=requested_key.developer_id))
        else:
            flash("This API Key is already blocked.")
            return redirect(url_for('user_operations.user_page', current_mode='api', user_id=requested_key.developer_id))
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
            return redirect(url_for('user_operations.user_page', current_mode='api', user_id=requested_key.developer_id))
        else:
            flash("This API Key is not blocked.")
            return redirect(url_for('user_operations.user_page', current_mode='api', user_id=requested_key.developer_id))
    except AttributeError:
        return abort(400)