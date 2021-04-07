from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import LoginManager
from flask_mail import Mail
from flask_msearch import Search
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_restful import Api

ckeditor = CKEditor()
bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
search = Search()
csrf_protection = CSRFProtect()
gravatar = Gravatar(size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False,
                    base_url=None)
flask_api = Api(decorators=[csrf_protection.exempt])
