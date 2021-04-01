from flask import request, abort, Blueprint, render_template, flash, url_for
from flask_login import login_required
from werkzeug.utils import redirect

from forms import ForgetHandlingForm, ForgetPasswordForm, MakeUserForm, AuthForm
from utils import get_admin_count
from validation_manager.functions import admin_redirect
from validation_manager.wrappers import admin_only
from verification_manager.handle_verification import handle_email_verification, handle_forgot_password, load_token, \
    handle_support_confirmation, make_user_administrator, remove_administrator, handle_deletion_decision, \
    subscription_verification_handling, unsubscription_verification_handling
from verification_manager.generate_verification import generate_password_reset, redirect_after_verification
from models import User, NewsletterSubscription

verification = Blueprint('verification', __name__)


@verification.route('/verify-email/<token>')
def verify_email(token):
    email = request.args.get('email')
    if email:
        return handle_email_verification(token=token, email=email)
    else:
        return abort(400)


@verification.route('/generate-forget', methods=['GET', 'POST'])
def generate_forget():
    form = ForgetHandlingForm()
    if form.validate_on_submit():
        return generate_password_reset(form.email.data)
    return render_template('login.html', form=form, handling=True)


@verification.route('/handle-forget/<token>', methods=['GET', 'POST'])
def forget_password(token):
    load_token(token=token, salt='forget-password', redirect_to='login_system.login')
    email = request.args.get('email')
    form = ForgetPasswordForm()
    user = User.query.filter_by(email=email).first()
    if user:
        if form.validate_on_submit():
            return handle_forgot_password(token=token, user=user, new_password=form.new_password.data)
        return render_template('login.html', forget=True, token=token, form=form, email=email)
    else:
        flash("Could not find a user with the specified email address.")
        return redirect(url_for('home.home_page', category='danger'))


@verification.route('/verify-support/<token>')
def handle_support_confirmation(token):
    email = request.args.get('email')
    return handle_support_confirmation(token=token, email=email)


@verification.route('/admin/<token>', methods=['GET', 'POST'])
@login_required
def handle_new_admin(token):
    if get_admin_count() > 0:
        admin_redirect()
    load_token(token, salt='make-auth')
    try:
        user_id = int(request.args.get('user_id'))
    except (TypeError, ValueError):
        return abort(400)
    user = User.query.get(user_id)
    form = MakeUserForm()
    if user:
        if not user.admin:
            if form.validate_on_submit():
                return make_user_administrator(token=token, user=user, reason=form.reason.data)
            return render_template('admin-form.html', form=form, user_name=user.name, user_id=user_id,
                                   category='admin', token=token)
        else:
            flash("This user is already an administrator.")
            return redirect(url_for('user_operations.user_page', user_id=user_id))
    else:
        flash("Could not find a user with the specified ID.")
        return redirect(url_for('home.home_page', category='danger'))


@verification.route('/admin-remove/<token>', methods=['GET', 'POST'])
@admin_only
def handle_admin_removal(token):
    load_token(token=token, salt='remove-auth')
    try:
        user_id = int(request.args.get('user_id'))
    except (TypeError, ValueError):
        return abort(400)
    user = User.query.get(user_id)
    form = MakeUserForm()
    if user is not None:
        if user.admin is True:
            if form.validate_on_submit():
                return remove_administrator(token=token, user=user, reason=form.reason.data)
            return render_template('admin-form.html', form=form, user_name=user.name, user_id=user_id,
                                   category='admin', remove="True", token=token, )
        else:
            flash("This user is not an administrator.")
            return redirect(url_for('user_operations.user_page', user_id=user_id))
    else:
        return abort(404)


@verification.route('/auth/<int:user_id>', methods=['GET', 'POST'])
@admin_only
def authorization(user_id):
    form = AuthForm()
    user = User.query.get(user_id)
    if not user:
        return abort(400)
    if form.validate_on_submit():
        return redirect_after_verification(user_id=user_id, auth_func='authorization',
                                           redirect_to='user_operations.delete_user',
                                           salt='delete-auth', password=form.code.data)
    return render_template('delete.html', form=form, authorization=True, user_id=user_id)


@verification.route('/admin-auth/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_auth(user_id):
    if get_admin_count() > 0:
        admin_redirect()
    form = AuthForm()
    remove = request.args.get('remove')
    if not User.query.get(user_id):
        return abort(404)
    if form.validate_on_submit():
        if remove != 'True':
            return redirect_after_verification(user_id=user_id, password=form.code.data, auth_func='admin_auth',
                                               redirect_to='verification.handle_new_admin', salt='make-auth')
        else:
            return redirect_after_verification(user_id=user_id, password=form.code.data, auth_func='admin_auth',
                                               redirect_to='verification.handle_admin_removal', salt='remove-auth')
    return render_template('admin-form.html', form=form, authorization=True, user_id=user_id,
                           category='admin',
                           remove=remove)


@verification.route('/handle-request/<token>')
@admin_only
def handle_request(token):
    email = request.args.get('email')
    decision = request.args.get('decision')
    requested_user = User.query.filter_by(email=email).first()
    if requested_user:
        return handle_deletion_decision(requested_user=requested_user, decision=decision, token=token)
    else:
        flash("Could not find a user with the specified ID.")
        return redirect(url_for('home.home_page', category='danger'))


@verification.route('/verify-subscription/<token>')
def handle_subscription_verification(token):
    email = request.args.get('email')
    requested_subscription = NewsletterSubscription.query.filter_by(email=email).first()
    if requested_subscription:
        return subscription_verification_handling(requested_subscription=requested_subscription, token=token)
    else:
        flash("Could not find a subscription with the specified email.")
        return redirect(url_for('home.home_page', category='danger'))


@verification.route('/verify-unsubscription/<token>')
def handle_unsubscription_verification(token):
    email = request.args.get('email')
    reason = request.args.get('reason', '')
    explanation = request.args.get('explanation', '')
    requested_subscription = NewsletterSubscription.query.filter_by(email=email).first()
    if requested_subscription:
        return unsubscription_verification_handling(requested_subscription=requested_subscription, token=token,
                                                    reason=reason, explanation=explanation)
    else:
        flash("Could not find a subscription with the specified email.")
        return redirect(url_for('home.home_page', category='danger'))
