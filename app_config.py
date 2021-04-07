import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'string')
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///blog.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USERNAME = os.environ.get('EMAIL', 'gm.sobig@gmail.com')
MAIL_PASSWORD = os.environ.get('PASSWORD', 'zwymqmzluzohliov')
MAIL_USE_TLS = True
JSON_SORT_KEYS = False
