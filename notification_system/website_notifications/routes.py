from flask import Blueprint
from flask_login import login_required, current_user
from notification_system.website_notifications.functions import get_notifications_dict
from utils import handle_page

notification_routing = Blueprint('notifications', __name__, url_prefix='/notifications')


@notification_routing.route('/')
@notification_routing.route('/<int:page_id>')
@login_required
def notifications(page_id=1):
    notification_items = get_notifications_dict(current_user)
    return handle_page(endpoint='user.html', notification=True, items_lst=notification_items, page_id=page_id,
                       items_arg='notification_items', title='Notifications',
                       subtitle='View all of your notifications.')
