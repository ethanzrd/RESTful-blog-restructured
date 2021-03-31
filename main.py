# TODO ------------------ TODO BLOCK ------------------

# TODO - Verify contact support email before usage using confirmation links

# ------------------ END BLOCK ------------------


# ------------------ IMPORTS BLOCK ------------------

from flask import Flask, render_template, redirect, url_for, request, flash, abort, jsonify
from functools import wraps
from flask_msearch import Search
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy.orm import relationship
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField
from wtforms_components import ColorField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditor, CKEditorField
import datetime as dt
from flask_mail import Mail, Message
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy_json import mutable_json_type
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_gravatar import Gravatar
import os
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from html2text import html2text
from sqlalchemy.dialects.postgresql import JSON
import random
import string


# @app.route('/page/<int:page_id>')
# def page(page_id):
#     deleted = request.args.get('deleted')
#     user_id = request.args.get('user_id')
#     current_mode = request.args.get('current_mode')
#     table_page = request.args.get('table_page')
#     view_filter = request.args.get('view_filter')
#     settings_view = request.args.get('settings')
#     mode = request.args.get('mode')
#     count = 0
#     data = get_data(homepage=True)
#     if deleted == 'True':
#         blog_posts = get_deleted()
#         if page_id == 1:
#             return redirect(url_for('deleted_posts'))
#         result = page_id * 3
#         posts = blog_posts[result - 3:result]
#         count = 0
#         for _ in posts:
#             count += 1
#         return render_template('index.html', deleted_posts=posts, deleted='True',
#                                posts_count=count, current_id=page_id,
#                                title="Deleted Posts",
#                                subtitle="View and recover deleted posts!")
#     elif user_id is not None and User.query.get(user_id) is not None:
#         user = User.query.get(user_id)
#         posts = get_user_posts(user_id)
#         comments = get_user_comments(user_id)
#         if current_mode in ['posts', 'comments', 'api']:
#             if current_mode == 'posts':
#                 blog_posts = posts
#                 if page_id == 1:
#                     return redirect(url_for('user_page', user_id=user_id))
#                 result = page_id * 3
#                 posts = blog_posts[result - 3:result]
#                 count = 0
#                 for _ in posts:
#                     count += 1
#                 return render_template("user.html", all_posts=posts, posts_count=count, current_id=page_id,
#                                        title=f"{user.name}'s Profile", subtitle=f"{user.name}'s Posts",
#                                        current_mode='posts',
#                                        user=user)
#             elif current_mode == 'comments':
#                 blog_posts = comments
#                 if page_id == 1:
#                     return redirect(url_for('user_page', user_id=user_id, current_mode='comments'))
#                 result = page_id * 3
#                 posts = blog_posts[result - 3:result]
#                 count = 0
#                 for _ in posts:
#                     count += 1
#                 return render_template("user.html", comments=posts, posts_count=count,
#                                        current_id=page_id,
#                                        title=f"{user.name}'s Profile", subtitle=f"{user.name}'s Comments",
#                                        current_mode='comments', user=user)
#             elif current_mode == 'api':
#                 requested_api = get_user_api(user_id)
#                 if page_id == 1:
#                     return redirect(url_for('user_page', user_id=user_id, current_mode='api'))
#                 if requested_api is not None:
#                     if current_user.email == ApiKey.query.filter_by(developer_id=user_id).first().developer.email \
#                             or current_user.admin is True:
#                         try:
#                             return render_template("user.html", all_posts=requested_api[page_id],
#                                                    current_id=page_id,
#                                                    title=f"{user.name}'s Profile", subtitle=f"{user.name}'s API Key",
#                                                    current_mode='api',
#                                                    user=user, posts_count=len(requested_api[page_id]),
#                                                    admin_count=get_admin_count())
#                         except (KeyError, IndexError):
#                             return render_template("user.html", all_posts={},
#                                                    current_id=page_id,
#                                                    title=f"{user.name}'s Profile", subtitle=f"{user.name}'s API Key",
#                                                    current_mode='api',
#                                                    user=user, posts_count=0,
#                                                    admin_count=get_admin_count())
#                     else:
#                         if current_user.is_authenticated:
#                             return abort(403)
#                         else:
#                             return abort(401)
#                 else:
#                     flash("Could not find an API with the specified ID.")
#                     return redirect(url_for(user_page, user_id=user_id))
#         else:
#             flash("Malformed page request for user profile.")
#             return redirect(url_for('home', category='danger'))
#     elif table_page is not None:
#         users_filter = get_users_filter(view_filter)
#         blog_posts = list(get_user_dict(users_filter).values())
#         if page_id == 1:
#             return redirect(url_for('user_table', view_filter=view_filter))
#         result = page_id * 3
#         posts = blog_posts[result - 3:result]
#         count = 0
#         for _ in posts:
#             count += 1
#         return render_template('index.html', users=posts, user_table="True",
#                                posts_count=count, current_id=page_id, title="User Database Table",
#                                subtitle="Visualize your user database effortlessly.",
#                                unconfirmed=any(User.query.filter_by(confirmed_email=False).all()),
#                                current_view=view_filter)
#     elif settings_view is not None:
#         if mode != 'admin':
#             if current_user.is_authenticated:
#                 options = get_options(requested_page=page_id)
#                 errors = {}
#                 title = "Account Settings"
#                 subtitle = 'Here you will be able to configure your account settings.'
#             else:
#                 return abort(401)
#         else:
#             if current_user.is_authenticated and current_user.admin is True:
#                 options = get_options(requested_page=page_id, website=True)
#                 errors = check_errors()
#                 title = "Settings"
#                 subtitle = "Here you will be able to access primary website configurations."
#             else:
#                 return abort(403)
#         count = 0
#         if page_id == 1:
#             return redirect(url_for('settings', mode=mode))
#         for _ in options:
#             count += 1
#         return render_template('index.html', settings="True", options=options,
#                                options_count=len(options),
#                                errors=errors, title=title,
#                                subtitle=subtitle,
#                                current_id=page_id,
#                                posts_count=count, mode=mode)
#     else:
#         blog_posts = get_posts()
#         if page_id == 1:
#             return redirect(url_for('home'))
#         result = page_id * 3
#         posts = blog_posts[result - 3:result]
#         count = 0
#         for _ in posts:
#             count += 1
#     return render_template("index.html", all_posts=posts, posts_count=count, current_id=page_id, title=data[0],
#                            subtitle=data[1])


# ------------------ POST SYSTEM BLOCK ------------------


# @app.route('/comment/<int:comment_id>', methods=['GET', 'POST'])
# def show_comment(comment_id):
#     form = ReplyForm()
#     reply_page = request.args.get('c_page')
#     deleted = request.args.get('deleted')
#     post_id = request.args.get('post_id')
#     if deleted is not None:
#         if post_id is not None:
#             try:
#                 requested_post = (DeletedPost.query.get(post_id).id, DeletedPost.query.get(post_id).json_column)
#                 requested_comment = [comment for comment in requested_post[1]["comments"]
#                                      if comment['comment_id'] == comment_id][0]
#                 replies = requested_comment["replies"]
#                 original_comment = requested_comment
#                 parent_post = requested_post
#                 navbar = requested_post[1]["color"] if requested_post[1]["color"] != '' else get_navbar()
#             except (AttributeError, IndexError, KeyError):
#                 return abort(404)
#         else:
#             flash("Malformed Page Request - Post ID was not provided.")
#             return redirect(url_for('home', category='danger'))
#     else:
#         try:
#             requested_comment = get_comment(comment_id)
#             replies = requested_comment.replies
#             original_comment = requested_comment
#             parent_post = requested_comment.parent_post
#             navbar = parent_post.color if parent_post.color != '' else get_navbar()
#         except AttributeError:
#             return abort(404)
#     if reply_page is not None:
#         current_c = reply_page
#         if reply_page == 1:
#             return redirect(url_for('show_comment', comment_id=comment_id))
#         try:
#             result = int(reply_page) * 3
#         except TypeError:
#             return redirect(url_for('show_comment', comment_id=comment_id))
#         reply_items = replies[result - 3:result]
#     else:
#         current_c = 1
#         reply_items = replies[:3]
#     if form.validate_on_submit():
#         if current_user.is_authenticated:
#             new_reply = Reply(author=current_user,
#                               parent_comment=requested_comment,
#                               reply=html2text(form.reply.data),
#                               date=generate_date())
#             new_notification = Notification(user=requested_comment.author, by_user=current_user.email,
#                                             user_name=current_user.name,
#                                             body=f"{current_user.name} replied to your comment on"
#                                                  f" {requested_comment.parent_post.title}", parent_reply=new_reply,
#                                             date=generate_date(), category='reply')
#             db.session.add(new_reply, new_notification)
#             db.session.commit()
#             return redirect(url_for('show_comment', comment_id=requested_comment.id, c_page=current_c))
#         else:
#             flash("User is not logged in.")
#             return redirect(url_for('show_comment', comment_id=requested_comment.id))
#     return render_template("post.html", c_count=len(reply_items), current_c=int(current_c),
#                            comment=True, original_comment=original_comment,
#                            post=parent_post, comments=[requested_comment], navbar=navbar,
#                            form=form, replies=reply_items, deleted=str(deleted), post_id=post_id)


# ------ COMMENT SYSTEM ------





# ------ END ------


# ------------------ END BLOCK ------------------


# ------------------ NOTIFICATIONS BLOCK ------------------




# ------------------ END BLOCK ------------------


# ------------------ SETTINGS BLOCK ------------------



















# ------------------ DELETION REQUEST BLOCK ------------------










# ------------------ END BLOCK ------------------



# ------------------ SERVER CONFIG ------------------
