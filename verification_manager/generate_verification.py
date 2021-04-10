from flask_login import current_user, login_required
from werkzeug.security import check_password_hash
from werkzeug.utils import redirect

from users_manager.current_user_manager.functions import user_has_deletion_request
from data_manager import get_data
from extensions import db
from models import User, DeletionReport
from notification_system.email_notifications.notifications import verify_email, reset_password_notification, \
    email_set_as_support_notification, verify_subscription_notification, verify_unsubscription_notification
from settings import serializer
from flask import url_for, flash, abort

from utils import generate_date


def generate_email_verification(email, name):
    token = serializer.dumps(email, salt='email-verify')
    link = url_for('verification.verify_email', token=token, email=email, _external=True)
    status = verify_email(email=email, name=name, link=link)
    category = "success" if status else "danger"
    flash("A confirmation email has been sent to you." if status else \
              "No sender specified, please contact the website staff.")
    return redirect(url_for('home.home_page', category=category))


def generate_password_reset(email):
    requesting_user = User.query.filter_by(email=email).first()
    if requesting_user:
        token = serializer.dumps(email, salt='forget-password')
        link = url_for('verification.forget_password', token=token, email=email, _external=True)
        status = reset_password_notification(requesting_user.name, email, link)
        category = "success" if status else "danger"
        flash("A password reset email has been sent to you.") if status else \
            flash("No sender, specified, please contact the website staff.")
        return redirect(url_for('home.home_page', category=category))
    else:
        flash("Could not find a user with the specified email address.")
        return redirect(url_for('verification.generate_forget'))


def generate_support_email_verification(email):
    token = serializer.dumps(email, salt='support-verify')
    link = url_for('verification.handle_support_confirmation', token=token, email=email, _external=True)
    status = email_set_as_support_notification(email, link)
    flash("A confirmation email has been sent to the specified support email." if status
          else "No sender specified, could not send a confirmation email to the specified support email. "
               "Support email unchanged.")
    return redirect(url_for('home.home_page', category='success' if status else 'danger'))


def generate_subscription_verification(email):
    token = serializer.dumps(email, salt='subscription-verify')
    link = url_for('verification.handle_subscription_verification', token=token, email=email, _external=True)
    status = verify_subscription_notification(email=email, link=link)
    flash("A confirmation email has been sent to you." if status
          else "No sender specified, could not send a confirmation email. Unable to subscribe at this time.")
    return redirect(url_for('home.home_page', category='success' if status else 'danger'))


def generate_unsubscription_verification(email, name, **kwargs):
    token = serializer.dumps(email, salt='unsubscription-verify')
    link = url_for('verification.handle_unsubscription_verification', token=token, email=email, _external=True,
                   **kwargs)
    status = verify_unsubscription_notification(email=email, link=link, name=name)
    flash("A confirmation email has been sent to you." if status
          else "No sender specified, could not send a confirmation email. Unable to subscribe at this time.")
    return redirect(url_for('home.home_page', category='success' if status else 'danger'))


def redirect_after_verification(user_id, password, redirect_to, salt, auth_func):
    if not User.query.get(user_id):
        return abort(400)
    try:
        contents = get_data()
        secret_password = contents['secret_password']
    except (KeyError, TypeError, IndexError):
        flash("Authentication Password is not available. Deletion cannot be performed at this time.")
        return redirect(url_for('home.home_page', category='danger'))
    if check_password_hash(secret_password, password):
        token = serializer.dumps(current_user.email, salt=salt)
        link = url_for(redirect_to, token=token, email=current_user.email, user_id=user_id)
        return redirect(link)
    else:
        flash("Incorrect authorization code.")
        return redirect(url_for(f"verification.{auth_func}", user_id=user_id))


@login_required
def generate_deletion():
    def create_link(decision):
        link_token = serializer.dumps(current_user.email, salt='deletion_request')
        return url_for('verification.handle_request', token=link_token, email=current_user.email, decision=decision,
                       _external=True)

    if user_has_deletion_request(current_user.id):
        requested_report = DeletionReport.query.filter_by(user_id=current_user.id).first()
        if not requested_report.approval_link:
            try:
                requested_report.approval_link = create_link(decision='approved')
                requested_report.rejection_link = create_link(decision='rejected')
                requested_report.date = generate_date()
            except AttributeError:
                return abort(500)
            else:
                db.session.commit()
                flash("Request sent, please wait 1-3 days for administrators to review your request.")
                return redirect(url_for('home.home_page', category='success'))
        else:
            flash("Your account is already in a pending deletion state.")
            return redirect(url_for('home.home_page', category='danger'))
    else:
        return abort(400)
