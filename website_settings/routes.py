from flask import Blueprint, render_template, request

from context_manager import get_background
from newsletter.functions import get_subscribers_by_filter, get_subscribers_dict
from users_manager.current_user_manager.functions import get_full_users_dict
from data_manager import get_data
from forms import WebConfigForm, ContactConfigForm, AboutConfigForm, AuthConfig, ApiConfig, NewsletterConfigurationForm
from users_manager.functions import get_users_by_filter, if_unconfirmed_users, delete_unconfirmed_users
from utils import handle_page
from validation_manager.wrappers import admin_only
from website_settings.functions import load_menu_elements, get_form_elements, update_configuration, \
    update_authentication_password
from logs.functions import get_logs_by_filter
from verification_manager.generate_verification import generate_support_email_verification

website_settings = Blueprint('website_settings', __name__, url_prefix='/settings')


@website_settings.route('/')
@website_settings.route('/<int:page_id>')
@admin_only
def menu(page_id=1):
    options, title, subtitle, errors = load_menu_elements()
    return handle_page(endpoint='index.html', settings="True", items_lst=options, errors=errors,
                       title=title, subtitle=subtitle, page_id=page_id, mode='admin', items_arg='options')


@website_settings.route('/web-configure', methods=['GET', 'POST'])
@admin_only
def web_configuration():
    form = WebConfigForm(**get_form_elements('website_configuration'))
    if form.validate_on_submit():
        return update_configuration('website_configuration', form)
    return render_template('config.html', config_title="Website Configuration",
                           config_desc="Configure primary website elements.", form=form,
                           config_func="website_settings.web_configuration")


@website_settings.route('/contact-configure', methods=['GET', 'POST'])
@admin_only
def contact_configuration():
    form = ContactConfigForm(**get_form_elements('contact_configuration'))
    message = None
    if form.validate_on_submit():
        new_email = False
        data = get_data()
        support_email = data.get("contact_configuration", {}).get("support_email", '')
        if form.support_email.data != support_email:
            message = generate_support_email_verification(form.support_email.data)
            new_email = True
        return update_configuration('contact_configuration', form, new_email=new_email, flash_message=message)
    return render_template('config.html', config_title="Contact Page Configuration",
                           config_desc="Configure primary elements of the contact page.", form=form,
                           config_func="website_settings.contact_configuration",
                           background_image=get_background('contact_configuration'))


@website_settings.route('/about-configure', methods=['GET', 'POST'])
@admin_only
def about_configuration():
    form = AboutConfigForm(**get_form_elements('about_configuration'))
    if form.validate_on_submit():
        return update_configuration('about_configuration', form)
    return render_template('config.html', config_title="About Page Configuration",
                           config_desc="Configure primary elements of the about page.", form=form,
                           config_func="website_settings.about_configuration",
                           background_image=get_background('about_configuration'))


@website_settings.route('/auth-configure', methods=['GET', 'POST'])
@admin_only
def authentication_configuration():
    form = AuthConfig()
    if form.validate_on_submit():
        return update_authentication_password(form)
    return render_template('config.html', config_title="Authentication Configuration",
                           config_desc="Configure primary elements of the website's authentication", form=form,
                           config_func="website_settings.authentication_configuration")


@website_settings.route('/api/configure', methods=['GET', 'POST'])
@admin_only
def api_configuration():
    form = ApiConfig(**get_form_elements('api_configuration'))
    if form.validate_on_submit():
        return update_configuration('api_configuration', form)
    return render_template('config.html', config_title="API Configuration",
                           config_desc="Configure the allowed routes for developers.", form=form,
                           config_func="website_settings.api_configuration")


@website_settings.route('/newsletter', methods=['GET', 'POST'])
@admin_only
def newsletter_configuration():
    form = NewsletterConfigurationForm(**get_form_elements('newsletter_configuration'))
    if form.validate_on_submit():
        return update_configuration('newsletter_configuration', form)
    return render_template('config.html', config_title="Newsletter Configuration",
                           config_desc="Configure the primary elements of the built-in newsletter functionality.",
                           form=form, config_func="website_settings.newsletter_configuration")


@website_settings.route('/user-table')
@website_settings.route('/user-table/<int:page_id>')
@admin_only
def user_table(page_id=1):
    view_filter = request.args.get('view_filter')
    users = get_users_by_filter(view_filter)
    users_dict = get_full_users_dict(users)
    return handle_page(endpoint='index.html', items_lst=list(users_dict.values()), page_id=page_id, user_table="True",
                       title="User Database Table", subtitle="Visualize your user database effortlessly.",
                       current_view=view_filter, unconfirmed=if_unconfirmed_users(), items_arg='users')


@website_settings.route('/logs')
@website_settings.route('/logs/<int:page_id>')
@admin_only
def logs(page_id=1):
    view_filter = request.args.get('view_filter')
    requested_logs = get_logs_by_filter(view_filter)
    return handle_page(endpoint='index.html', logs="True", items_lst=requested_logs, page_id=page_id,
                       items_arg='log_items', title='Website Logs', current_view=view_filter,
                       subtitle='View all of the website logs.')


@website_settings.route('/newsletter-table')
@website_settings.route('/newsletter-table/<int:page_id>')
@admin_only
def newsletter_subscribers_table(page_id=1):
    view_filter = request.args.get('view_filter')
    requested_subscribers = get_subscribers_by_filter(view_filter)
    subscribers_dict = get_subscribers_dict(requested_subscribers)
    return handle_page(endpoint='index.html', newsletter_table="True", items_lst=subscribers_dict, page_id=page_id,
                       items_arg='subscribers', title='Newsletter Subscribers Database', current_view=view_filter,
                       subtitle='Visualize your newsletter subscribers database effortlessly.')


@website_settings.route('/delete-unconfirmed')
@admin_only
def unconfirmed_users_deletion():
    return delete_unconfirmed_users()
