from flask import Blueprint, render_template
from flask_login import current_user

from general.contact.functions import get_page_elements, is_page_valid, send_message
from context_manager import get_background
from forms import ContactForm

contact_routing = Blueprint('contact', __name__, url_prefix='/contact')


@contact_routing.route("/", methods=['GET', 'POST'])
def contact():
    valid = is_page_valid()
    heading, subheading, description = get_page_elements()
    if current_user.is_authenticated and current_user.confirmed_email:
        form = ContactForm(name=current_user.name, email=current_user.email)
    else:
        form = ContactForm()
    if form.validate_on_submit():
        return send_message(form)
    kwargs = {'heading': heading, 'subheading': subheading, 'description': description, 'valid': valid,
              'background_image': get_background('contact_configuration')}
    if valid:
        kwargs['form'] = form
    return render_template("contact.html", **kwargs)
