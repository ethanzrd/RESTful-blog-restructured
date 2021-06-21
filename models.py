from flask_login import UserMixin, current_user
from extensions import db
from sqlalchemy.orm import relationship
from sqlalchemy_json import mutable_json_type
from sqlalchemy.dialects.postgresql import JSON
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from login_system.oauth.blueprints import twitter_blueprint, github_blueprint, google_blueprint


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __searchable__ = ['name']
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(700), unique=True)
    confirmed_email = db.Column(db.Boolean(), default=False)
    join_date = db.Column(db.String(300), default='')
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    admin = db.Column(db.Boolean(), default=False)
    author = db.Column(db.Boolean(), default=False)
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    replies = relationship("Reply", back_populates="author")
    api_key = relationship("ApiKey", back_populates="developer")
    deletion_report = relationship('DeletionReport', back_populates='user')
    notifications = relationship("Notification", back_populates='user')
    logs = relationship("Log", back_populates='user')
    twitter_name = db.Column(db.String, unique=True)
    github_id = db.Column(db.Integer, unique=True)
    google_id = db.Column(db.String, unique=True)


class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)


twitter_blueprint.backend = SQLAlchemyStorage(OAuth, db.session, user=current_user)
github_blueprint.backend = SQLAlchemyStorage(OAuth, db.session, user=current_user)
google_blueprint.backend = SQLAlchemyStorage(OAuth, db.session, user=current_user)


class DeletionReport(db.Model):
    __tablename__ = 'deletion_reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates='deletion_report')
    deletion_reason = db.Column(db.String(1200), default='')
    deletion_explanation = db.Column(db.String(1200), default='')
    approval_link = db.Column(db.String(1000), default='')
    rejection_link = db.Column(db.String(1000), default='')
    date = db.Column(db.String(250), default='')

    __mapper_args__ = {
        "order_by": id.desc()
    }


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates='notifications')
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"))
    parent_comment = relationship("Comment", back_populates='notification')
    reply_id = db.Column(db.Integer, db.ForeignKey("replies.id"))
    parent_reply = relationship("Reply", back_populates='notification')
    category = db.Column(db.String(300), nullable=False)
    by_user = db.Column(db.String(1200), nullable=False)
    user_name = db.Column(db.String(1200), nullable=False)
    body = db.Column(db.String(1200), default='')
    date = db.Column(db.String(250), default='')

    __mapper_args__ = {
        "order_by": id.desc()
    }


class ApiKey(db.Model):
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    developer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    developer = relationship("User", back_populates="api_key")
    occupation = db.Column(db.String(200), nullable=False)
    application = db.Column(db.String(1200), nullable=False)
    usage = db.Column(db.String(1200))
    blocked = db.Column(db.Boolean(), default=False)
    api_key = db.Column(db.String(500), nullable=False)
    all_posts = db.Column(db.Integer, default=0)
    random_post = db.Column(db.Integer, default=0)
    all_users = db.Column(db.Integer, default=0)
    random_user = db.Column(db.Integer, default=0)
    get_post = db.Column(db.Integer, default=0)
    add_post = db.Column(db.Integer, default=0)
    edit_post = db.Column(db.Integer, default=0)
    delete_post = db.Column(db.Integer, default=0)
    newsletter_sendout = db.Column(db.Integer, default=0)

    __mapper_args__ = {
        "order_by": id.desc()
    }


class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    __searchable__ = ["title", "subtitle"]
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(400), nullable=False)
    subtitle = db.Column(db.String(400), nullable=False)
    date = db.Column(db.String(400), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(600), nullable=True)
    comments = relationship("Comment", back_populates="parent_post")

    __mapper_args__ = {
        "order_by": id.desc()
    }


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="comments")
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates='comments')
    replies = relationship("Reply", back_populates='parent_comment')
    notification = relationship("Notification", back_populates='parent_comment')
    comment = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(250), nullable=False)

    __mapper_args__ = {
        "order_by": id.desc()
    }


class Reply(db.Model):
    __tablename__ = 'replies'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="replies")
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"))
    parent_comment = relationship("Comment", back_populates='replies')
    notification = relationship("Notification", back_populates='parent_reply')
    reply = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(250), nullable=False)

    __mapper_args__ = {
        "order_by": id.desc()
    }


class DeletedPost(db.Model):
    __tablename__ = 'deleted_posts'
    id = db.Column(db.Integer, primary_key=True)
    json_column = db.Column(mutable_json_type(dbtype=JSON, nested=True), nullable=False)

    __mapper_args__ = {
        "order_by": id.desc()
    }


class Data(db.Model):
    __tablename__ = 'data_table'
    id = db.Column(db.Integer, primary_key=True)
    json_column = db.Column(JSON, nullable=False)


class NewsletterSubscription(db.Model):
    __tablename__ = 'newsletter_subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(300), nullable=False)
    last_name = db.Column(db.String(300), nullable=False)
    email = db.Column(db.String(700), nullable=False, unique=True)
    active = db.Column(db.Boolean(), default=False)
    unsubscription_reason = db.Column(db.String(700), default='')
    unsubscription_explanation = db.Column(db.String(3000), default='')
    unsubscription_date = db.Column(db.String(300), default='')
    date = db.Column(db.String(300), nullable=False)

    __mapper_args__ = {
        "order_by": id.desc()
    }


class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship("User", back_populates='logs')
    category = db.Column(db.String(700), nullable=False)
    description = db.Column(db.String(1200), nullable=False)
    user_name = db.Column(db.String(700), nullable=False)
    user_email = db.Column(db.String(700), nullable=False)
    date = db.Column(db.String(700), nullable=False)

    __mapper_args__ = {
        "order_by": id.desc()
    }
