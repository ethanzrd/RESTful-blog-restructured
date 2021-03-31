from flask import Flask
from extensions import ckeditor, bootstrap, mail, db, login_manager, search, gravatar
from context_manager import get_name, get_date, get_background, get_navbar, get_social
from error_manager import unauthorized, forbidden, not_found, internal_error, bad_request
from post_system.post.routes import post
from post_system.comment.routes import comment
from post_system.reply.routes import reply
from search.routes import search_routing
from about.routes import about_routing
from verification_manager.routes import verification
from users_manager.routes import user_operations
from api.routes import api
from contact.routes import contact_routing
from notification_system.website_notifications.routes import notification_routing
from website_settings.routes import website_settings
from login_system.routes import login_system
from home import home


def create_app(config_file='app_config.py'):
    app = Flask(__name__)

    app.config.from_pyfile(config_file)

    ckeditor.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    search.init_app(app)
    gravatar.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            requested_user = User.query.get(user_id)
            if requested_user.confirmed_email:
                return requested_user
        except AttributeError:
            pass

    app.register_blueprint(home)
    app.register_blueprint(post)
    app.register_blueprint(comment)
    app.register_blueprint(search_routing)
    app.register_blueprint(about_routing)
    app.register_blueprint(verification)
    app.register_blueprint(user_operations)
    app.register_blueprint(api)
    app.register_blueprint(contact_routing)
    app.register_blueprint(notification_routing)
    app.register_blueprint(reply)
    app.register_blueprint(website_settings)
    app.register_blueprint(login_system)

    app.register_error_handler(400, bad_request)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(404, not_found)
    app.register_error_handler(500, internal_error)
    app.register_error_handler(401, unauthorized)
    return app


app = create_app()
app.app_context().push()
from models import BlogPost, ApiKey, DeletionReport, Comment, DeletedPost, User, Reply, Notification, Data
db.create_all()

app.context_processor(get_name)
app.context_processor(get_date)
app.context_processor(get_background)
app.context_processor(get_navbar)
app.context_processor(get_social)


if __name__ == '__main__':
    app.run(debug=True)
