from flask import url_for, flash
from werkzeug.security import generate_password_hash
from werkzeug.utils import redirect
from extensions import db
from models import User
from verification_manager.generate_verification import generate_email_verification


def register_user(name, email, password):
    user = User.query.filter_by(email=email).first()
    if not user:
        add_user(name, email, password)
    else:
        if user.confirmed_email is True:
            flash("This email already exists, please try again.")
            return redirect(url_for('login_system.register'))
        else:
            db.session.delete(user)
            db.session.commit()
            add_user(name, email, password)
            return redirect(url_for('home.home_page'))

    return redirect(url_for('home.home_page'))


def add_user(name, email, password):
    password = generate_password_hash(password=password,
                                      method='pbkdf2:sha256', salt_length=8)
    new_user = User(email=email, password=password, name=name)
    db.session.add(new_user)
    db.session.commit()
    generate_email_verification(email, name)
    return redirect(url_for('home.home_page'))
