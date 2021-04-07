from data_manager import get_data
from notification_system.email_notifications.notifications import contact_inquiry_notification
from flask import abort, redirect, url_for, flash


def get_page_elements():
    try:
        contact_config = get_data()['contact_configuration']
    except KeyError:
        heading = "Contact us"
        subheading = "We'll get to you as soon as we can."
        description = "Want to get in touch? Fill out the form below and we'll respond as soon as we can!"
    else:
        heading = contact_config.get('page_heading')
        subheading = contact_config.get('page_subheading')
        description = contact_config.get('page_description')
    return heading, subheading, description


def is_page_valid():
    valid = True
    try:
        support_email = get_data()["contact_configuration"]["support_email"]
    except KeyError:
        valid = False
    else:
        if support_email is None:
            valid = False
    return valid


def send_message(form):
    try:
        notification = contact_inquiry_notification(form.email.data, form.name.data, form.message.data)
    except AttributeError:
        return abort(400)
    else:
        if notification is False:
            flash("No support email specified, unable to send your message.")
            return redirect(url_for('home.home_page', category='danger'))
        else:
            flash("Message successfully sent.")
            return redirect(url_for('home.home_page', category='success'))
