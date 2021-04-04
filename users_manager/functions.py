from flask import flash, url_for, abort
from flask_login import current_user, logout_user, login_required
from werkzeug.utils import redirect

from users_manager.current_user_manager.functions import user_has_api_key, user_has_deletion_request, get_user_api, \
    get_user_deletion_report
from extensions import db
from maintenance import clean_posts
from models import User, DeletionReport, ApiKey, Notification
from notification_system.email_notifications.notifications import set_notification, remove_notification, \
    account_deleted_notification, deletion_request_notification
from post_system.post.functions import get_post_dict
from utils import generate_date, handle_page, get_admin_count
from html2text import html2text

from verification_manager.generate_verification import generate_deletion
from website_settings.functions import get_options


def get_users_by_filter(view_filter=None):
    if view_filter == 'admin':
        users = User.query.filter_by(admin=True).all()
    elif view_filter == 'author':
        users = User.query.filter_by(author=True).all()
    elif view_filter == 'registered':
        users = User.query.filter_by(confirmed_email=True).all()
    elif view_filter == 'unconfirmed':
        users = User.query.filter_by(confirmed_email=False).all()
    elif view_filter == 'pending':
        users = [user for user in User.query.all()
                 if DeletionReport.query.filter_by(user_id=user.id).first() is not None]
    else:
        users = User.query.all()
    return users


def get_users_dict(users=None):
    if not users:
        users = User.query.all()
    try:
        users = list(users)
    except TypeError:
        users = [users]
    users_dict = [{"username": user.name,
                   "permissions": get_user_permissions(user),
                   "is_developer": True if
                   ApiKey.query.filter_by(developer_id=user.id) else False,
                   "posts": [get_post_dict(post) for post
                             in
                             user.posts],
                   "comments": [{
                       "comment": html2text(comment.comment).strip(),
                       "on_post":
                           comment.parent_post
                               .title,
                       "post_author":
                           comment.parent_post
                               .author.name,
                       "commented_on": comment.date}
                       for comment in user.comments],
                   "replies": [{"reply": reply.reply.strip(),
                                "on_comment": html2text(reply.parent_comment.comment).strip(),
                                "on_post": reply.parent_comment.parent_post.title,
                                "replied_on": reply.date,
                                "comment_author": reply.parent_comment.author.name,
                                "post_author": reply.parent_comment.parent_post.author.name} for
                               reply in user.replies]}
                  for user in users if user.confirmed_email is True]
    return users_dict


def if_unconfirmed_users():
    return any(User.query.filter_by(confirmed_email=False).all())


def get_user_information(user):
    try:
        user_dict = {"user_id": user.id,
                     "username": user.name,
                     "permissions": get_user_permissions(user),
                     "is_developer": True if ApiKey.query.filter_by(developer_id=user.id) else False}
        return user_dict
    except AttributeError:
        return abort(400)


def get_user_permissions(user):
    return "Administrator" if user.admin is True else "Author" if user.author is True \
        else "Registered User" if user.confirmed_email is True else None


def delete_unconfirmed_users():
    if current_user.is_authenticated and current_user.admin:
        unconfirmed = User.query.filter_by(confirmed_email=False).all()
        if any(unconfirmed):
            [db.session.delete(user) for user in unconfirmed]
            flash("All unconfirmed users have been deleted from the user database.")
            db.session.commit()
        else:
            flash("No unconfirmed users in the database.")
        return redirect(url_for("website_settings.user_table"))
    else:
        abort(403)


def make_user_author(user, reason):
    try:
        user.author = True
    except AttributeError:
        return abort(400)
    set_notification('author', user.email, user.name, current_user.name, html2text(reason))
    new_notification = Notification(user=user, by_user=current_user.email, user_name=current_user.name,
                                    body=f"You were set as an author by {current_user.name}.",
                                    date=generate_date(), category='new')
    db.session.add(new_notification)
    db.session.commit()
    flash("This user has been set as an author, a notification has been sent to the user.")
    return redirect(url_for('user_operations.user_page', user_id=user.id))


def remove_user_as_author(user, reason):
    try:
        user.author = False
    except AttributeError:
        return abort(400)
    remove_notification('author', user.email, user.name, current_user.name, html2text(reason))
    new_notification = Notification(user=user, by_user=current_user.email, user_name=current_user.name,
                                    body=f"You were removed as an author by {current_user.name}.",
                                    date=generate_date(), category='removal')
    db.session.add(new_notification)
    db.session.commit()
    flash("This user has been removed as an author, a notification has been sent to the user.")
    return redirect(url_for('user_operations.user_page', user_id=user.id))


def user_page_redirect(user_id, current_mode, page_id=1):
    given_mode = current_mode if current_mode != 'delete-report' else 'deletion_report' \
        if current_mode in ['posts', 'comments', 'api', 'delete-report'] else 'posts'
    requested_mode = f"user_operations.user_{given_mode}"
    return redirect(url_for(requested_mode, user_id=user_id, page_id=page_id))


def handle_user_posts(user, page_id=1, **kwargs):
    return handle_page(endpoint='user.html', items_arg='all_posts', items_lst=user.posts, user=user,
                       page_id=page_id, report_exists=user_has_deletion_request(user.id), admin_count=get_admin_count(),
                       api_exists=user_has_api_key(user.id), title=f"{user.name}'s Profile",
                       subtitle=f"{user.name}'s Posts", current_mode='posts')


def handle_user_api(user, page_id=1, **kwargs):
    if current_user.is_authenticated and current_user.email == User.query.get(user.id).email \
            or current_user.admin is True:
        try:
            requested_api = get_user_api(user.id)
        except AttributeError:
            return abort(400)
        if requested_api:
            return handle_page(endpoint='user.html', items_lst=requested_api, items_arg='all_posts', page_id=page_id,
                               pre_defined=True, report_exists=user_has_deletion_request(user.id), current_mode='api',
                               title=f"{user.name}'s Profile", subtitle=f"{user.name}'s API Key", user=user,
                               admin_count=get_admin_count())
        else:
            return abort(404)


def handle_user_comments(user, page_id=1, **kwargs):
    return handle_page(endpoint='user.html', items_lst=user.comments, items_arg='comments', page_id=page_id, user=user,
                       current_mode='comments', title=f"{user.name}'s Profile", subtitle=f"{user.name}'s Comments",
                       api_exists=user_has_api_key(user.id), report_exists=user_has_deletion_request(user.id),
                       admin_count=get_admin_count())


def handle_user_deletion_report(user, **kwargs):
    if current_user.is_authenticated and current_user.email == User.query.get(user.id).email \
            or current_user.admin is True:
        requested_report = get_user_deletion_report(user.id)
        if requested_report:
            return handle_page(endpoint='user.html', items_arg='all_posts', items_lst=requested_report, page_id=1,
                               pre_defined=True, title=f"{user.name}'s Profile", user=user,
                               current_mode='delete-report', admin_count=get_admin_count(),
                               subtitle=f"{user.name}'s Deletion Request Report", api_exists=user_has_api_key(user.id))
        else:
            return abort(404)


def handle_account_deletion(user, title, reason):
    try:
        email = user.email
    except AttributeError:
        return abort(400)
    account_deleted_notification(email=email, name=user.name, action_user=current_user.name,
                                 action_title=title, action_reason=html2text(reason))
    if current_user == user:
        logout_user()
    flash("The user has been deleted, a notification has been sent to the user.")
    db.session.delete(user)
    clean_posts()
    db.session.commit()
    return redirect(url_for('home.home_page', category='success'))


def handle_deletion_request(reason, explanation):
    if get_admin_count() < 1:
        requested_user = User.query.get(current_user.id)
        deletion_request_notification(email=current_user.email, name=current_user.name, decision="approved")
        logout_user()
        db.session.delete(requested_user)
        db.session.commit()
        flash("Your account has been successfully deleted.")
        return redirect(url_for('home.home_page', category='success'))
    else:
        explanation = explanation if any(explanation) \
            else "No additional info provided."
        new_report = DeletionReport(deletion_reason=reason,
                                    deletion_explanation=html2text(explanation), user=current_user)
        db.session.add(new_report)
        db.session.commit()
        return generate_deletion()


def handle_account_settings():
    options = get_options()
    title = "Account Settings"
    subtitle = "Here you will be able to configure your account settings."
    errors = {}
    return handle_page(endpoint='index.html', settings="True", items_lst=options, errors=errors,
                       title=title, subtitle=subtitle, page_id=1, mode='admin', items_arg='options')
