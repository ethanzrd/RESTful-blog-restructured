from models import *
from flask import abort


def clean_posts():
    [db.session.delete(post) for post in DeletedPost.query.all()
     if User.query.filter_by(email=post.json_column["author_email"]).first() is None]
    for post in BlogPost.query.all():
        try:
            user = User.query.filter_by(email=post.author.email).first()
            if user is None:
                db.session.delete(post)
        except AttributeError:
            db.session.delete(post)
    for comment in Comment.query.all():
        try:
            comment = comment.author.email
        except (AttributeError, TypeError):
            db.session.delete(comment)
    for api_key in ApiKey.query.all():
        try:
            key = api_key.developer.email
        except (AttributeError, TypeError):
            db.session.delete(api_key)
    for deletion_report in DeletionReport.query.all():
        try:
            report = deletion_report.user.email
        except (AttributeError, TypeError):
            db.session.delete(deletion_report)
    for reply_item in Reply.query.all():
        try:
            reply = reply_item.parent_comment.post_id
        except (AttributeError, TypeError):
            db.session.delete(reply_item)
    for post in DeletedPost.query.all():
        post.json_column["comments"] = [comment for comment in post.json_column['comments']
                                        if User.query.filter_by(email=comment["author_email"]).first() is not None]
        for comment in post.json_column["comments"]:
            comment["replies"] = [reply for reply in comment["replies"] if
                                  User.query.filter_by(email=reply["author_email"]).first() is not None]


def clean_notifications(category):
    if category in ['comment', 'reply']:
        [db.session.delete(notification) for notification in Notification.query.filter_by(category=category).all()
         if eval(f"notification.parent_{category}") is None]
    else:
        return abort(403)
