from flask import Blueprint, url_for, flash, render_template, request, abort
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import redirect
from forms import LoginForm, RegisterForm, ChangePasswordForm
from models import User
from validation_manager.wrappers import logout_required
from login_system.functions import register_user, password_change
from verification_manager.generate_verification import generate_email_verification

login_system = Blueprint('login_system', __name__)


@login_system.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    form = LoginForm()
    user_name = None
    email = None
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            if user.confirmed_email:
                if check_password_hash(user.password, form.password.data):
                    login_user(user)
                    return redirect(url_for('home.home_page'))
                else:
                    flash("Incorrect password, please try again.")
            else:
                email = user.email
                user_name = user.name
                flash("unconfirmed")
        else:
            flash("This email does not exist, please try again.")
    return render_template("login.html", form=form, email=email, user_name=user_name,
                           category=request.args.get('category', 'danger'))


@login_system.route('/register', methods=['GET', 'POST'])
@logout_required
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        return register_user(name=form.name.data, email=form.email.data.lower(), password=form.password.data)
    return render_template('register.html', form=form)


@login_system.route('/validate')
def validate():
    email = request.args.get('email')
    name = request.args.get('name')
    if not name or not email:
        return abort(400)
    else:
        return generate_email_verification(email, name)


@login_system.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password, form.old_password.data):
            return password_change(form.new_password.data)
        else:
            flash("The old password does not match.")
    return render_template('config.html', form=form, config_func='login_system.change_password')


@login_system.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home.home_page'))
