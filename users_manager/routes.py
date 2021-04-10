from flask import Blueprint, flash, render_template, url_for, request, abort
from flask_login import login_required, current_user
from werkzeug.utils import redirect
from functools import partial

from context_manager import user_has_api_operations
from forms import MakeUserForm, DeleteForm, DeletionRequest
from models import User
from validation_manager.wrappers import admin_only
from users_manager.functions import make_user_author, remove_user_as_author, user_page_redirect, handle_user_posts, \
    handle_user_api, handle_user_comments, handle_user_deletion_report, handle_account_deletion, \
    handle_deletion_request, handle_account_settings
from verification_manager.handle_verification import load_token

user_operations = Blueprint('user_operations', __name__, url_prefix='/user')


@user_operations.route('/author/<int:user_id>', methods=['GET', 'POST'])
@admin_only
def make_author(user_id):
    user = User.query.get(user_id)
    form = MakeUserForm()
    if user:
        if not user.author:
            if form.validate_on_submit():
                return make_user_author(user=user, reason=form.reason.data)
            return render_template('admin-form.html', form=form, user_name=user.name, user_id=user_id,
                                   category='author')
        else:
            flash("This user is already set as an author.")
            return redirect(url_for('user_operations.user_page', user_id=user_id))
    else:
        flash("Could not find a user with the specified ID.")
        return redirect(url_for('home.home_page', category='danger'))


@user_operations.route('/author-remove/<int:user_id>', methods=['GET', 'POST'])
@admin_only
def remove_author(user_id):
    user = User.query.get(user_id)
    form = MakeUserForm()
    if user is not None:
        if user.author is True:
            if form.validate_on_submit():
                remove_user_as_author(user, form.reason.data)
            return render_template('admin-form.html', form=form, user_name=user.name, user_id=user_id,
                                   category='author', remove="True")
        else:
            flash("This user is not an author.")
            return redirect(url_for('user_operations.user_page', user_id=user_id))
    else:
        flash("Could not find a user with the specified ID.")
        return redirect(url_for('home.home_page', category='danger'))


@user_operations.route('/<int:user_id>')
def user_page(user_id):
    user = User.query.get(user_id)
    if user:
        current_mode = request.args.get('current_mode', 'posts')
        page_id = request.args.get('page_id', 1)
        return user_page_redirect(user_id=user_id, current_mode=current_mode, page_id=page_id)
    else:
        return abort(404)


@user_operations.route('/<int:user_id>/posts')
@user_operations.route('/<int:user_id>/posts/<int:page_id>')
def user_posts(user_id, page_id=1):
    user = User.query.get(user_id)
    if user:
        return handle_user_posts(user, page_id)
    else:
        return abort(404)


@user_operations.route('/<int:user_id>/api')
@user_operations.route('/<int:user_id>/api/<int:page_id>')
def user_api(user_id, page_id=1):
    user = User.query.get(user_id)
    if user:
        return handle_user_api(user, page_id)
    else:
        return abort(404)


@user_operations.route('/<int:user_id>/comments')
@user_operations.route('/<int:user_id>/comments/<int:page_id>')
def user_comments(user_id, page_id=1):
    user = User.query.get(user_id)
    if user:
        return handle_user_comments(user, page_id)
    else:
        return abort(404)


@user_operations.route('/<int:user_id>/deletion-report')
def user_deletion_report(user_id):
    user = User.query.get(user_id)
    if user:
        return handle_user_deletion_report(user)
    else:
        return abort(404)


@user_operations.route('/delete-user/<int:user_id>', methods=['GET', 'POST'])
@user_operations.route('/delete-user/<int:user_id>/<token>')
@admin_only
def delete_user(user_id, token=None):
    user = User.query.get(user_id)
    if user:
        if user.admin:
            if token:
                load_token(token=token, salt='remove-auth')
            else:
                return redirect(url_for('verification.authorization', user_id=user_id))
        form = DeleteForm()
        if form.validate_on_submit():
            return handle_account_deletion(user=user, title=form.title.data, reason=form.reason.data)
        return render_template('delete.html', form=form, user_id=user_id, user_name=user.name,
                               token=request.args.get('token'))
    else:
        return abort(404)


@user_operations.route('/request-deletion', methods=['GET', 'POST'])
@login_required
def request_deletion():
    form = DeletionRequest()
    if form.validate_on_submit():
        return handle_deletion_request(reason=form.reason.data, explanation=form.explanation.data)
    return render_template('config.html', config_title="Account Deletion Request",
                           config_desc="Request to delete your account.",
                           form=form, config_func="user_operations.request_deletion")


@user_operations.route('/settings')
@login_required
def settings():
    return handle_account_settings()
