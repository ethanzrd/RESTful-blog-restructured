from flask_login import current_user
from models import Reply, Notification
from html2text import html2text
from utils import generate_date
from extensions import db
from flask import redirect, url_for, flash, abort, render_template
from maintenance import clean_notifications


def add_reply(requested_comment, reply, current_page=1):
    if requested_comment:
        comment_id = requested_comment.id
        if current_user.is_authenticated:
            new_reply = Reply(author=current_user,
                              parent_comment=requested_comment,
                              reply=html2text(reply),
                              date=generate_date())
            new_notification = Notification(user=requested_comment.author, by_user=current_user.email,
                                            user_name=current_user.name,
                                            body=f"{current_user.name} replied to your comment on"
                                                 f" {requested_comment.parent_post.title}", parent_reply=new_reply,
                                            date=generate_date(), category='reply')
            db.session.add(new_reply, new_notification)
            db.session.commit()
            return redirect(url_for('comment.show_comment', comment_id=comment_id, c_page=current_page))
        else:
            flash("User is not logged in.")
            return redirect(url_for('comment.show_comment', comment_id=comment_id))
    else:
        return abort(404)


def reply_deletion(requested_reply, current_page=1):
    if current_user.is_authenticated:
        if requested_reply.parent_comment.parent_post.author.email == current_user.email \
                or current_user.email == requested_reply.author.email:
            db.session.delete(requested_reply)
            clean_notifications('reply')
            db.session.commit()
            return redirect(url_for('comment.show_comment', comment_id=requested_reply.comment_id, c_page=current_page))
        else:
            return abort(403)
    else:
        return abort(401)


def reply_edition(requested_reply, form, current_page=1, request='GET'):
    if current_user.is_authenticated:
        if requested_reply.author.email == current_user.email:
            if request == 'POST':
                requested_reply.reply = html2text(form.reply.data)
                db.session.commit()
                return redirect(
                    url_for('comment.show_comment', comment_id=requested_reply.comment_id, c_page=current_page))
            else:
                return render_template('config.html', config_title="Edit Your Reply",
                                       config_desc="Here, you'll be able to edit your replies.", form=form,
                                       config_func="reply.edit_reply", reply_id=requested_reply.id,
                                       c_page=current_page)
        else:
            return abort(403)
    else:
        return abort(401)


def get_comment_replies(comment):
    return [{"reply_author": reply.author.name, "reply": reply.reply.strip(),
             "replied_on": reply.date} for reply in comment.replies]


def get_full_comment_replies(comment):
    return [{"author_id": reply.author_id, "author_email": reply.author.email, "author": reply.author.name,
             "comment_id": reply.comment_id, "reply": reply.reply, "date": reply.date}
            for reply in comment.replies]
