from flask import abort
from models import User
from users_manager.current_user_manager.functions import get_user_notifications


def get_notifications_dict(user):
    try:
        user_notifications = get_user_notifications(user.id)
    except (AttributeError, TypeError):
        return abort(400)
    else:
        try:
            notifications_dict = [
                {"date": notification.date, "by_user": User.query.filter_by(email=notification.by_user).first(),
                 "user_name": notification.user_name,
                 "user_email": notification.by_user,
                 "parent_comment": notification.parent_comment,
                 "parent_reply": notification.parent_reply,
                 "category": notification.category, "body": notification.body} for
                notification in user_notifications]
            return notifications_dict
        except AttributeError:
            return abort(400)
