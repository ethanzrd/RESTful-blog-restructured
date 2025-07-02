import os
import secrets

# SECURITY: fall back to a random key if SECRET_KEY env variable is missing
SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///blog.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USERNAME = os.environ.get('EMAIL')
MAIL_PASSWORD = os.environ.get('PASSWORD')
MAIL_USE_TLS = True
JSON_SORT_KEYS = False
