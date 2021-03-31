import datetime as dt
from settings import MAX_POSTS_PER_PAGE
from flask import render_template, abort
from models import User


def generate_date():
    months = [(i, dt.date(2008, i, 1).strftime('%B')) for i in range(1, 13)]
    now = dt.datetime.now()
    current_month = [month for month in months if now.month == month[0]][0][1]
    return f'{current_month} {now.day}, {now.year}'


def get_items(items_lst, page_id=1):
    requested_index = page_id * MAX_POSTS_PER_PAGE
    try:
        given_items = items_lst[requested_index - MAX_POSTS_PER_PAGE:requested_index] if page_id > 1 \
            else items_lst[:MAX_POSTS_PER_PAGE]
    except TypeError:
        return abort(400)
    items_count = len(given_items)
    return given_items, items_count


def handle_page(endpoint, items_lst, page_id, items_arg, page_arg='current_id', count_arg='posts_count',
                pre_defined=False, **kwargs):
    try:
        page_id = int(page_id)
    except (TypeError, ValueError):
        return abort(400)
    if not pre_defined:
        given_items, count = get_items(items_lst, page_id)
    else:
        given_items = items_lst.get(page_id, {})
        count = len(given_items)
    return render_template(endpoint, **kwargs, **{items_arg: given_items, count_arg: count, page_arg: page_id})


def get_admin_count():
    return len([user for user in User.query.all() if user.admin is True])
