import jwt
from datetime import datetime, timedelta
from flask import Flask
import pytest

from validation_manager.wrappers import token_required
from extensions import db
from models import User, ApiKey

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'testsecret'
    db.init_app(app)
    with app.app_context():
        db.create_all()
        user = User(email='a@test.com', name='TestUser')
        db.session.add(user)
        db.session.commit()
        key = ApiKey(developer=user, occupation='Student', application='Test', usage='Test', api_key='abc')
        db.session.add(key)
        db.session.commit()

        @app.route('/protected')
        @token_required
        def protected_route(requesting_user):
            return 'ok', 200

        yield app

@pytest.fixture
def client(app):
    return app.test_client()


def _generate_token(app, user_id, delta):
    payload = {'user': {'user_id': user_id}, 'exp': datetime.utcnow() + delta}
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token


def test_invalid_token(client):
    response = client.get('/protected', headers={'x-access-token': 'invalid'})
    assert response.status_code == 401


def test_expired_token(client, app):
    with app.app_context():
        user_id = User.query.first().id
        token = _generate_token(app, user_id, timedelta(seconds=-1))
    response = client.get('/protected', headers={'x-access-token': token})
    assert response.status_code == 401


def test_valid_token(client, app):
    with app.app_context():
        user_id = User.query.first().id
        token = _generate_token(app, user_id, timedelta(minutes=5))
    response = client.get('/protected', headers={'x-access-token': token})
    assert response.status_code == 200
