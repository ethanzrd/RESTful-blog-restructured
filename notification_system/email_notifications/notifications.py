from flask import url_for

from context_manager import get_name
from notification_system.email_notifications.functions import send_mail
from flask_mail import Message
from settings import EMAIL
from html2text import html2text
from data_manager import get_data
from utils import generate_date


def account_deleted_notification(email, name, action_user, action_title, action_reason):
    msg = Message('Account Deleted', sender=EMAIL, recipients=[email])
    msg.body = f"Hello {name}, this is an automatic email from {get_name('m')} to notify you of recent" \
               f" events that occurred in regards to your account.\n\n" \
               f'Your account was deleted by {action_user} due to "{action_title}".\n\n' \
               f'Deletion reasoning by actioning staff member:\n\n{html2text(action_reason)}\n\n' \
               f'If you believe that a mistake was made, contact us by replying to this email or via our website.'
    send_mail(msg)


def deletion_request_notification(email, name, decision):
    msg = Message('Deletion Request', sender=EMAIL, recipients=[email])
    if decision:
        msg.body = f"Hello {name}, this is an automatic email from {get_name('m')} to notify you of recent" \
                   f" events that occurred in regards to your account.\n\n" \
                   f"Your Deletion Request was {decision}.\n\n" \
                   f"If you believe that a mistake was made, please contact us by replying to this email or via our" \
                   f" website."
    send_mail(msg)


def set_notification(category, email, name, action_user, action_reason):
    try:
        support_email = get_data()["contact-configuration"]["support_email"]
    except KeyError:
        msg = Message(f'Account set as {category}', sender=EMAIL, recipients=[email])
    else:
        msg = Message(f'Account set as {category}', sender=EMAIL, recipients=[email,
                                                                              support_email])
    msg.body = f"Hello {name}, this is an automatic email from {get_name('m')} to notify you of recent" \
               f" events that occurred in regards to your account.\n\n" \
               f'Your account was set as an {category} by {action_user}.\n\n' \
               f'Reasoning by actioning staff member:\n\n{html2text(action_reason)}\n\n' \
               f'Congratulations, if you have any inquires, contact us by replying to this email or via our website.'
    send_mail(msg)


def remove_notification(category, email, name, action_user, action_reason):
    try:
        support_email = get_data()["contact-configuration"]["support_email"]
    except KeyError:
        msg = Message(f'Account removed as {category}', sender=EMAIL, recipients=[email])
    else:
        msg = Message(f'Account removed as {category}', sender=EMAIL, recipients=[email,
                                                                                  support_email
                                                                                  ])
    msg.body = f"Hello {name}, this is an automatic email from {get_name('m')} to notify you of recent" \
               f" events that occurred in regards to your account.\n\n" \
               f'Your account was removed as an {category} by {action_user}.\n\n' \
               f'Reasoning by actioning staff member:\n\n{html2text(action_reason)}\n\n' \
               f'If you believe that a mistake was made, contact us by replying to this email or via our website.'
    send_mail(msg)


def contact_inquiry_notification(email, name, action_reason):
    try:
        support_email = get_data()["contact_configuration"]["support_email"]
    except KeyError:
        return False
    else:
        if support_email is None:
            return False
    msg = Message(f"{get_name('m')} - Contact Inquiry", sender=EMAIL,
                  recipients=[support_email])
    msg.body = f"This is an automatic email from {get_name('m')} to notify you of a" \
               f" user inquiry.\n\n" \
               f'Name: {name}\n\n' \
               f'Email: {email}\n\n' \
               f'Message:\n\n{html2text(action_reason)}' \
               f'Note: This email was set as a support email for {get_name("m")}, if you are not familiar with the' \
               f' source of this email, please contact us by replying to this email or via our website.'
    send_mail(msg)


def password_changed_notification(email, name, date):
    msg = Message(f'Password Changed', sender=EMAIL, recipients=[email])
    msg.body = f"Hello {name}, this is an automatic email from {get_name('m')} to notify you of recent" \
               f" events that occurred in regards to your account.\n\n" \
               f'Your account password was changed at {date}.\n\n' \
               f"If this wasn't you, contact us by replying to this email or via our website."
    send_mail(msg)


def reset_password_notification(name, email, link):
    msg = Message('Forget Password', sender=EMAIL, recipients=[email])
    msg.body = f"Hello {name}, you have recently requested a password change," \
               f" please go to this link to reset your password.\n\n{link}\n\n" \
               f"If this wasn't you, please contact us by replying to this email or via our website."
    return send_mail(msg)


def verify_email(name, email, link):
    msg = Message('Confirmation Email', sender=EMAIL, recipients=[email])
    msg.body = f"Hello {name}, please go to this link to finalize your registration.\n\n" \
               f"{link}\n\nNote: If you're unfamiliar with the source of this email, simply ignore it."
    return send_mail(msg, allow_redirects=False)


def email_set_as_support_notification(email, link):
    msg = Message(f'Email set as support email', sender=EMAIL, recipients=[email])
    msg.body = f"Hello, this is an automatic email from {get_name('m')}." \
               f" This email was specified as the support email for {get_name('m')} at {generate_date()}." \
               f" To confirm and set this email as the support email, please go to the link below.\n\n" \
               f'{link}.\n\n' \
               f"Note: If you are unfamiliar with the source of this email, simply ignore it."
    return send_mail(msg)


def verify_subscription_notification(email, link):
    msg = Message(f'Newsletter Subscription Verification', sender=EMAIL, recipients=[email])
    msg.body = f"Hello, this is an automatic email from {get_name('m')}." \
               f" This email was used to sign up to a newsletter in {get_name('m')} at {generate_date()}." \
               f" To confirm and subscribe to our newsletter, please go to the link below.\n\n" \
               f'{link}.\n\n' \
               f"Note: If you are unfamiliar with the source of this email, simply ignore it."
    return send_mail(msg, allow_redirects=False)


def verify_unsubscription_notification(email, name, link):
    msg = Message(f'Newsletter Unsubscription Verification', sender=EMAIL, recipients=[email])
    msg.body = f"Hello, {name}. We are sorry that you are dissatisfied with our newsletter.\n\n" \
               f"This is the last step towards unsubscribing from our newsletter, you can re-subscribe at any time." \
               f" Go to the link below to finalize the unsubscription.\n\n{link}"
    return send_mail(msg)


def newsletter_notification(title, contents, newsletter_recipients):
    msg = Message(title, sender=EMAIL, recipients=newsletter_recipients)
    msg.body = f"{contents}\n\nCopyright (C) {get_name('m')} All rights reserved.\n" \
               f"You received this email because you opted into our newsletter.\n" \
               f"To unsubscribe from this newsletter, go to the link below:\n\n" \
               f"{url_for('newsletter.unsubscribe', _external=True)}"
    return send_mail(msg)
