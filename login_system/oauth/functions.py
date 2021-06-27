from flask_login import current_user, login_user

from flask import session, request, redirect, url_for, abort, flash
from sqlalchemy.exc import InterfaceError
from extensions import db
from models import User


def check_if_user_not_linked(provider_identifier, func, *args, **kwargs):
    """check if the current user is not linked to a provider or raises the appropriate error"""

    if current_user.is_authenticated:
        if not getattr(current_user, provider_identifier):
            return func(*args, **kwargs)
        else:
            return abort(403)

    else:
        return abort(401)


def check_if_user_linked(provider_identifier, func, *args, **kwargs):
    """check if the current user is linked to a provider or raises the appropriate error"""

    if current_user.is_authenticated:
        if getattr(current_user, provider_identifier):
            return func(*args, **kwargs)
        else:
            return abort(403)

    else:
        return abort(401)


def check_authorization(blueprint, login_route, func, *args, **kwargs):
    """check if authorized and authenticate if necessary"""

    if not blueprint.session.authorized:
        # store current route before redirecting so we can return after successful auth
        session["next_url"] = request.path
        return redirect(url_for(login_route))
    return func(*args, **kwargs)


def link_provider(user_identifier, provider_identifier, provider):
    setattr(current_user, provider_identifier, user_identifier)
    db.session.commit()
    flash(f"Your {provider} account has been linked.")
    return redirect(url_for('home.home_page', category='success'))


def unlink_provider(provider_identifier, provider):
    setattr(current_user, provider_identifier, None)
    db.session.commit()
    flash(f"Your {provider} account has been unlinked.")
    return redirect(url_for('home.home_page', category='success'))


def login_with_provider(provider_identifier, user_identifier):
    if user_identifier:
        try:
            requested_user = User.query.filter_by(**{provider_identifier: user_identifier}).first()
        except InterfaceError:
            flash("User does not exist.")
            return redirect(url_for('login_system.login', category='danger'))
        if requested_user:
            login_user(requested_user)
            return redirect(url_for('home.home_page'))
        else:
            flash("User does not exist.")
            return redirect(url_for('login_system.login', category='danger'))
    else:
        return abort(400)
