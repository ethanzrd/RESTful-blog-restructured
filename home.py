from flask import Blueprint, request
from sqlalchemy.exc import OperationalError
from data_manager import get_data
from extensions import db
from utils import handle_page
from post_system.post.functions import get_posts

home = Blueprint('home', __name__)


@home.route('/home')
@home.route('/')
@home.route('/<int:page_id>')
def home_page(page_id=1):
    category = request.args.get('category')
    data = None
    try:
        data = get_data(homepage=True)
    except OperationalError:
        db.create_all()
    return handle_page(endpoint="index.html", items_arg='all_posts', items_lst=get_posts(),
                       page_id=page_id, title=data[0], subtitle=data[1], category=category)
