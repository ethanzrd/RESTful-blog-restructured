from functools import wraps

from flask_login import current_user

from flask import session, request, redirect, url_for, abort


def provider_auth_required(provider_object, login_route):
    def decorator(func):
        @wraps(func)
        def check_authorization(*args, **kwargs):
            """check if authorized and authenticate if necessary"""

            if not provider_object.authorized:
                # store current route before redirecting so we can return after successful auth
                session["next_url"] = request.path
                return redirect(url_for(login_route))
            return func(*args, **kwargs)

        return check_authorization

    return decorator


def provider_not_linked(provider_identifier):
    def decorator(func):
        @wraps(func)
        def check_if_user_not_linked(*args, **kwargs):
            """check if the current user is not linked to a provider or raises the appropriate error"""

            if current_user.is_authenticated:
                if not getattr(current_user, provider_identifier):
                    return func(*args, **kwargs)
                else:
                    return abort(403)

            else:
                return abort(401)

        return check_if_user_not_linked

    return decorator


def provider_linked(provider_identifier):
    def decorator(func):
        @wraps(func)
        def check_if_user_linked(*args, **kwargs):
            """check if the current user is linked to a provider or raises the appropriate error"""

            if current_user.is_authenticated:
                if getattr(current_user, provider_identifier):
                    return func(*args, **kwargs)
                else:
                    return abort(403)

            else:
                return abort(401)

        return check_if_user_linked

    return decorator
