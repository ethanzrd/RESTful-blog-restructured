from flask_login import current_user
from html2text import html2text

from extensions import db
from models import Notification, Comment, DeletedPost, Reply
from flask import redirect, url_for, flash, abort, render_template
from utils import generate_date
from maintenance import clean_notifications
from post_system.reply.functions import get_comment_replies, get_full_comment_replies


def get_comment(comment_id):
    try:
        comment = Comment.query.get(comment_id)
    except AttributeError:
        return None
    if comment is not None:
        return comment
    return None


def add_comment(requested_post, comment):
    if requested_post:
        post_id = requested_post.id
        if current_user.is_authenticated:
            new_comment = Comment(author=current_user,
                                  parent_post=requested_post,
                                  comment=comment,
                                  date=generate_date())
            new_notification = Notification(user=requested_post.author, by_user=current_user.email,
                                            user_name=current_user.name,
                                            parent_comment=new_comment, category='comment',
                                            body=f"{current_user.name} commented on your post.",
                                            date=generate_date())
            db.session.add(new_comment, new_notification)
            db.session.commit()
            return redirect(url_for('post.show_post', post_id=post_id))
        else:
            flash("User is not logged in.")
            return redirect(url_for('post.show_post', post_id=post_id))
    else:
        return abort(404)


def get_comment_elements(comment_id, deleted, post_id):
    if comment_id:
        try:
            if deleted:
                if post_id:
                    requested_post = (DeletedPost.query.get(post_id).id, DeletedPost.query.get(post_id).json_column)
                    requested_comment = [comment for comment in requested_post[1]["comments"]
                                         if comment['comment_id'] == comment_id][0]
                    replies = requested_comment["replies"]
                    parent_post = requested_post
                else:
                    return abort(400)
            else:
                requested_comment = get_comment(comment_id)
                replies = requested_comment.replies
                parent_post = requested_comment.parent_post
            return requested_comment, replies, parent_post
        except (AttributeError, IndexError, KeyError):
            return abort(404)
    else:
        return abort(400)


def comment_edition(requested_comment, form, request='GET'):
    if requested_comment and form:
        if request == 'POST':
            try:
                requested_comment.comment = form.comment.data
            except AttributeError:
                return abort(400)
            db.session.commit()
            return redirect(url_for('comment.show_comment', comment_id=requested_comment.id))
        else:
            return render_template('config.html', config_title="Edit Your Comment",
                                   config_desc="Here, you'll be able to edit your comments.", form=form,
                                   config_func="edit_comment",
                                   comment_id=requested_comment.id)
    else:
        return abort(400)


def comment_deletion(requested_comment):
    if current_user.is_authenticated:
        if requested_comment.parent_post.author.email == current_user.email \
                or current_user.email == requested_comment.author.email:
            try:
                current_post = requested_comment.post_id
            except AttributeError:
                return abort(400)
            replies = Reply.query.filter_by(parent_comment=requested_comment).all()
            [db.session.delete(reply) for reply in replies]
            db.session.delete(requested_comment)
            [clean_notifications(current_category) for current_category in ['comment', 'reply']]
            db.session.commit()
            return redirect(url_for('post.show_post', post_id=current_post))
        else:
            return abort(403)
    else:
        return abort(401)


def get_comment_dict(comment):
    return {"comment_author": comment.author.name, "comment": html2text(comment.comment).strip(),
            "commented_on": comment.date,
            "replies": get_comment_replies(comment)}


def get_full_comment_dict(comment):
    return {"author_id": comment.author_id, "author": comment.author.name,
            "author_email": comment.author.email, "post_id": comment.post_id,
            "comment": comment.comment, "comment_id": comment.id,
            "date": comment.date, "replies": get_full_comment_replies(comment)}
