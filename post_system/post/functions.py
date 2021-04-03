from sqlalchemy.orm.exc import UnmappedInstanceError
from werkzeug.utils import redirect

from models import BlogPost, DeletedPost, Comment, Reply, User
from html2text import html2text
from flask import abort, url_for, render_template
from utils import generate_date
from flask_login import current_user
from extensions import db
from sqlalchemy.exc import OperationalError
from maintenance import clean_notifications
from post_system.comment.functions import get_comment_dict, get_full_comment_dict


def get_deleted_posts():
    return [(post.id, post.json_column) for post in DeletedPost.query.all()]


def get_posts():
    try:
        return BlogPost.query.all()
    except OperationalError:
        return []


def get_post_dict(post):
    post_dict = {"author": post.author.name,
                 "title": post.title,
                 "subtitle": post.subtitle,
                 "published_on": post.date,
                 "contents": html2text(post.body).strip(),
                 "img_url": post.img_url,
                 "comments": get_post_comments(post)}
    return post_dict


def get_post_comments(post):
    return [get_comment_dict(comment) for comment in post.comments]


def get_full_post_dict(requested_post):
    try:
        post_comments = Comment.query.filter_by(post_id=requested_post.id).all()
    except AttributeError:
        return abort(400)
    else:
        post_dict = {
            "post_title": requested_post.title,
            "author_id": requested_post.author.id,
            "author_email": requested_post.author.email,
            "author": requested_post.author.name,
            "subtitle": requested_post.subtitle,
            "img_url": requested_post.img_url,
            "body": requested_post.body,
            "date": requested_post.date,
            "comments": [get_full_comment_dict(comment) for comment in post_comments]
        }
        return post_dict


def get_post_elements(post_id, deleted=None):
    try:
        if not deleted:
            requested_post = BlogPost.query.get(post_id)
            post_comments = BlogPost.query.get(post_id).comments
        else:
            requested_post = (DeletedPost.query.get(post_id).id, DeletedPost.query.get(post_id).json_column)
            post_comments = requested_post[1]["comments"]
    except (AttributeError, IndexError):
        return abort(404)
    return requested_post, post_comments


def post_addition(form):
    new_post = BlogPost(title=form.title.data,
                        subtitle=form.subtitle.data,
                        author=current_user,
                        img_url=form.img_url.data,
                        body=form.body.data,
                        date=generate_date())
    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for('home.home_page'))


def post_edition(requested_post, form, request='GET'):
    try:
        post_id = requested_post.id
    except AttributeError:
        return abort(400)
    if request == 'POST':
        requested_post.title = form.title.data
        requested_post.subtitle = form.subtitle.data
        requested_post.img_url = form.img_url.data
        requested_post.body = form.body.data
        db.session.commit()
        return redirect(url_for('post.show_post', post_id=post_id))
    else:
        return render_template('make-post.html', edit=True, post=requested_post, form=form,
                               background_image=requested_post.img_url)


def post_deletion(requested_post):
    if current_user.is_authenticated and current_user.author is True and \
            requested_post.author.email == current_user.email \
            or current_user.is_authenticated and current_user.admin is True:
        try:
            post_comments = requested_post.comments
        except AttributeError:
            return abort(404)
        new_post = get_full_post_dict(requested_post)
        new_deleted = DeletedPost(json_column=new_post)
        db.session.add(new_deleted)
        [db.session.delete(comment) for comment in post_comments]
        for reply_item in Reply.query.all():
            try:
                reply = reply_item.parent_comment.post_id
            except (AttributeError, TypeError):
                db.session.delete(reply_item)
        db.session.delete(requested_post)
        [clean_notifications(current_category) for current_category in ['comment', 'reply']]
        db.session.commit()
        return redirect(url_for('home.home_page'))
    else:
        return abort(403)


def post_recovery(database_entry, requested_post):
    try:
        if current_user.email != requested_post["author_email"] \
                or current_user.author is False and current_user.admin is False:
            return abort(403)
    except AttributeError:
        return abort(401)
    except KeyError:
        return abort(400)
    comments = requested_post["comments"]
    new_post = BlogPost(author=User.query.filter_by(email=requested_post["author_email"]).first(),
                        title=requested_post["post_title"],
                        subtitle=requested_post["subtitle"],
                        date=requested_post["date"],
                        body=requested_post["body"],
                        img_url=requested_post["img_url"],
                        )
    db.session.add(new_post)
    for comment in comments:
        new_comment = Comment(author=User.query.filter_by(email=comment["author_email"]).first(),
                              parent_post=new_post,
                              comment=comment["comment"], date=comment["date"])
        db.session.add(new_comment)
        for reply in comment["replies"]:
            new_reply = Reply(author=User.query.filter_by(email=reply["author_email"]).first(),
                              parent_comment=new_comment, reply=reply["reply"], date=reply['date'])
            db.session.add(new_reply)
    db.session.delete(database_entry)
    db.session.commit()
    return redirect(url_for('home.home_page'))


def post_permanent_deletion(database_entry):
    if current_user.is_authenticated and current_user.admin:
        try:
            db.session.delete(database_entry)
        except UnmappedInstanceError:
            return abort(404)
        else:
            db.session.commit()
            return redirect(url_for('post.deleted_posts'))
    else:
        return abort(403)
