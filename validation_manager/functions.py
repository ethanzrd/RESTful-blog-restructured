from data_manager import get_data
from flask_login import current_user
from flask import abort


def get_route_status(route):
    try:
        data = get_data()["api_configuration"]
    except KeyError:
        return "unavailable"
    else:
        try:
            if data[route] is False:
                return "blocked"
            return True
        except KeyError:
            return "unavailable"


def admin_redirect():
    if current_user.is_authenticated is False or current_user.admin is False:
        return abort(403)
