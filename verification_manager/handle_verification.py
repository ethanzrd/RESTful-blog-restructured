from flask_login import login_user, current_user, logout_user
from itsdangerous import SignatureExpired, BadTimeSignature
from flask import flash, redirect, url_for, abort
from werkzeug.security import generate_password_hash

from data_manager import get_data, update_data
from maintenance import clean_posts
from notification_system.email_notifications.notifications import password_changed_notification, set_notification, \
    remove_notification, deletion_request_notification
from settings import serializer, TOKEN_AGE
from models import User, Notification, DeletionReport
from utils import generate_date
from extensions import db


def load_token(token, salt, redirect_to='home.home_page'):
    """Checks whether a token is valid or redirects the user."""
    try:
        confirmation = serializer.loads(token, salt=salt, max_age=TOKEN_AGE)
    except SignatureExpired:
        flash("The token is expired, please try again.")
        return redirect(url_for(redirect_to))
    except BadTimeSignature:
        flash("Incorrect token, please try again.")
        return redirect(url_for(redirect_to))


def handle_email_verification(token, email):
    load_token(token=token, salt='email-verify', redirect_to='register')
    user = User.query.filter_by(email=email).first()
    if user:
        if not user.confirmed_email:
            user.confirmed_email = True
            user.join_date = generate_date()
            db.session.commit()
            login_user(user)
            flash("You've confirmed your email successfully.")
            category = 'success'
        else:
            flash("You've already confirmed your email.")
            category = 'danger'
        return redirect(url_for('home.home_page', category=category))
    else:
        flash("This user does not exist.")
        return redirect(url_for('login_system.register'))


def handle_forgot_password(token, user, new_password):
    load_token(token=token, salt='forget-password', redirect_to='login')
    if user:
        new_password = generate_password_hash(password=new_password,
                                              method='pbkdf2:sha256', salt_length=8)
        try:
            user.password = new_password
        except AttributeError:
            return abort(400)
        db.session.commit()
        password_changed_notification(user.email, user.name, generate_date())
        flash("Password changed successfully.")
        return redirect(url_for('login_system.login', category='success'))
    else:
        flash("Could not find a user with the specified email address.")
        return redirect(url_for('home.home_page', category='danger'))


def handle_support_confirmation(token, email):
    load_token(token=token, salt='support-verify')
    if not any(email):
        return abort(400)
    config_data = get_data()
    try:
        if config_data["contact_configuration"]["support_email"] != email:
            config_data["contact_configuration"]["support_email"] = email
            update_data(config_data)
            flash("This email was successfully set as the support email.")
            return redirect(url_for('home.home_page', category='success'))
        else:
            flash("This email is already set as the support email.")
            return redirect(url_for('home.home_page', category='danger'))
    except KeyError:
        return abort(500)


def make_user_administrator(token, user, reason):
    load_token(token, salt='make-auth')
    if user:
        try:
            user.author = False
        except AttributeError:
            return abort(400)
        set_notification('administrator', user.email, user.name, current_user.name, reason)
        user.admin = True
        new_notification = Notification(user=user, by_user=current_user.email, user_name=current_user.name,
                                        body=f"You were set as an administrator by {current_user.name}."
                                        , date=generate_date(), category='new')
        db.session.add(new_notification)
        db.session.commit()
        flash("The user has been set as an administrator, a notification has been sent to the user.")
        return redirect(url_for('user_operations.user_page', user_id=user.id))
    else:
        return abort(400)


def remove_administrator(token, user, reason):
    load_token(token=token, salt='remove-auth')
    if user:
        try:
            user.admin = False
        except AttributeError:
            return abort(400)
        remove_notification('administrator', user.email, user.name, current_user.name, reason)
        new_notification = Notification(user=user, by_user=current_user.email, user_name=current_user.name,
                                        body=f"You were removed as an administrator by {current_user.name}."
                                        , date=generate_date(), category='removal')
        db.session.add(new_notification)
        db.session.commit()
        flash("The user has been removed as an administrator, a notification has been sent to the user.")
        return redirect(url_for('user_operations.user_page', user_id=user.id))
    else:
        return abort(400)


def handle_deletion_decision(decision, requested_user, token):
    load_token(token=token, salt='deletion_request')
    requested_report = DeletionReport.query.filter_by(user=requested_user).first()
    if requested_report:
        if decision == 'approved':
            return handle_approved_deletion_request(requested_user)
        elif decision == 'rejected':
            return handle_rejected_deletion_request(requested_user)
        else:
            return abort(400)
    else:
        return abort(404)


def handle_approved_deletion_request(requested_user):
    deletion_request_notification(email=requested_user.email, name=requested_user.name, decision="approved")
    if current_user == requested_user:
        logout_user()
    flash("Deletion requested approved, a notification has been sent to the user.")
    db.session.delete(requested_user)
    clean_posts()
    db.session.commit()
    return redirect(url_for('home.home_page', category='success'))


def handle_rejected_deletion_request(requested_user):
    deletion_request_notification(email=requested_user.email, name=requested_user.name, decision="rejected")
    flash("Deletion request rejected, a notification has been sent to the user.")
    requested_report = DeletionReport.query.filter_by(user=requested_user).first()
    if requested_report:
        db.session.delete(requested_report)
    db.session.commit()
    return redirect(url_for('home.home_page', category='success'))


def subscription_verification_handling(requested_subscription, token):
    load_token(token=token, salt='subscription-verify')
    if requested_subscription:
        if not requested_subscription.active:
            requested_subscription.active = True
        else:
            flash("You've already confirmed your email.")
            return redirect(url_for('home.home_page', category='success'))
        db.session.commit()
        flash("You've confirmed your email successfully.")
        return redirect(url_for('home.home_page', category='success'))
    else:
        return abort(400)


def unsubscription_verification_handling(requested_subscription, token, reason, explanation):
    load_token(token=token, salt='unsubscription-verify')
    if requested_subscription:
        if requested_subscription.active:
            requested_subscription.active = False
            requested_subscription.unsubscription_reason = reason
            requested_subscription.unsubscription_explanation = explanation
            requested_subscription.unsubscription_date = generate_date()
            db.session.commit()
            flash("You've unsubscribed from the newsletter successfully.")
            return redirect(url_for('home.home_page', category='success'))
        else:
            flash("You've already unsubscribed from our newsletter.")
            return redirect(url_for('home.home_page', category='success'))
    else:
        return abort(400)
