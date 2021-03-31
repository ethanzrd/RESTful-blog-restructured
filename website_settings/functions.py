from flask_login import current_user
from flask import abort, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import redirect

from current_user_manager.functions import user_has_api_key, user_has_deletion_request
from data_manager import get_data, update_data
from settings import MAX_POSTS_PER_PAGE, CONFIG_KEYS

from models import Data


def get_options(requested_page: int = 1, website=False):
    def get_last(given_options: dict):
        try:
            use_id = list(given_options.keys())[-1] + 1
        except IndexError:
            use_id = 1
        return use_id

    if website:
        if current_user.is_authenticated and current_user.admin is True:
            options_dict = {1: {"name": "Website Configuration",
                                "desc": "Configure your website.",
                                "func": "website_settings.web_configuration"},
                            2: {"name": "Contact Me Configuration",
                                "desc": 'Configure the "Contact Me" page.',
                                "func": "website_settings.contact_configuration"},
                            3: {"name": "About Me Configuration",
                                "desc": 'Configure the "About Me" page.',
                                "func": "website_settings.about_configuration"},
                            4: {"name": "Authentication Configuration",
                                "desc": "Configure the website's authentication system.",
                                "func": "website_settings.authentication_configuration"},
                            5: {"name": "User Database Table",
                                "desc": "Visualize your user database effortlessly.",
                                "func": "website_settings.user_table"},
                            6: {"name": "API Configuration",
                                "desc": "Configure and manage your API system.",
                                "func": "website_settings.api_configuration"}
                            }
        else:
            return abort(403)
    else:
        if current_user.is_authenticated:
            options_dict = {}
            if not user_has_api_key(current_user.id):
                options_dict[get_last(options_dict)] = {"name": "Generate API Key",
                                                        "desc": "Generate an API Key to use our API services.",
                                                        "func": "api.generate_key"}
            if not user_has_deletion_request(current_user.id):
                options_dict[get_last(options_dict)] = {"name": "Delete my Account",
                                                        "desc": "Request account deletion",
                                                        "func": "user_operations.request_deletion"}

        else:
            return abort(401)

    options = list(options_dict.values())

    return options


def check_errors():
    errors = {}

    try:
        test = Data.query.all()[0].json_column
    except (AttributeError, IndexError):
        errors["Data File"] = "Data file is empty, no website configurations available."
    else:
        if check_password_hash(test['secret_password'], 'default'):
            errors["Authentication Password"] = "Authentication Password is set to default, change it immediately."

    return errors


def load_menu_elements():
    options = get_options(website=True)
    title = "Settings"
    subtitle = "Here you will be able to access primary website configurations."
    errors = check_errors()
    return options, title, subtitle, errors


def get_form_elements(configuration):
    try:
        requested_configuration = get_data()[configuration]
    except KeyError:
        return {}
    else:
        try:
            form_arguments = {key: requested_configuration[key] for key in requested_configuration}
        except KeyError:
            form_arguments = {}
        else:
            return form_arguments


def update_configuration(configuration, form, new_email=False, flash_message=None):
    data = get_data()
    try:
        keys = CONFIG_KEYS[configuration]
    except KeyError:
        return abort(400)
    else:
        new_data = {configuration: {
            key: form[key].data if key != 'navigation_bar_color' else form[key].data.hex
            if key != 'support_email' and new_email is False else data[configuration]['support_email']
            for key in keys
        }}
        data.update(new_data)
        update_data(data)
        flash(flash_message) if flash_message else None
        return redirect(url_for('website_settings.menu', mode='admin'))


def update_authentication_password(form):
    data = get_data()

    def set_authentication_password(password):
        new_password = generate_password_hash(password=password,
                                              method='pbkdf2:sha256', salt_length=8)
        password_data = {"secret_password": new_password}
        data.update(password_data)
        update_data(data)

    try:
        authentication_password = data['secret_password']
    except KeyError:
        authentication_password = None
    try:
        if authentication_password:
            if check_password_hash(authentication_password, form.old_password.data):
                set_authentication_password(form.new_password.data)
                return redirect(url_for('website_settings.menu', mode='admin'))
            else:
                flash("Incorrect authentication password.")
                return redirect(url_for('website_settings.authentication_configuration'))
        else:
            set_authentication_password(form.new_password.data)
            return redirect(url_for('website_settings.menu', mode='admin'))
    except (AttributeError, TypeError):
        return abort(400)
