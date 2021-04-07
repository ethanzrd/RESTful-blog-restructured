from models import BlogPost, User
from utils import handle_page


def display_results(search_query, category, page_id=1):
    if category == 'posts':
        posts = BlogPost.query.msearch(search_query).all()
        return handle_page(endpoint="index.html", items_arg='all_posts', items_lst=posts, count_arg='posts_count',
                           page_id=page_id, title="Search Results",
                           subtitle=f"Displaying user search results for: {search_query}",
                           search=True, mode='posts', query=search_query, category=category)
    else:
        users = [user for user in User.query.msearch(search_query).all() if user.confirmed_email is True]
        return handle_page(endpoint="index.html", items_arg='results', items_lst=users, count_arg='posts_count',
                           page_id=page_id, title="Search Results",
                           subtitle=f"Displaying user search results for: {search_query}",
                           search=True, mode='users', query=search_query, category=category)
