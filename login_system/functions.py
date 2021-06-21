from flask import url_for, flash
from flask_login import current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import redirect
from extensions import db
from models import User
from verification_manager.generate_verification import generate_email_verification
from notification_system.email_notifications.notifications import password_changed_notification


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


def password_change(new_password):
    current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256',
                                                   salt_length=8)
    email_status = password_changed_notification(email=current_user.email, name=current_user.name, redirect=False)
    if email_status:
        db.session.commit()
        flash("Password changed successfully.")
    else:
        flash("Sender Email is not specified, password was not changed.")
        return redirect(url_for('home.home_page', category='danger'))
    return redirect(url_for('home.home_page'))
