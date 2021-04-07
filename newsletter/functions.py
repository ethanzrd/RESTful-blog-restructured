from flask_login import current_user
from html2text import html2text
from werkzeug.utils import redirect

from data_manager import get_data
from logs.functions import log_newsletter_sendout, log_api_newsletter_sendout
from models import NewsletterSubscription, Log, User
from flask import abort, flash, url_for, jsonify, make_response
from extensions import db
from notification_system.email_notifications.notifications import newsletter_notification
from utils import generate_date
from verification_manager.generate_verification import generate_subscription_verification, \
    generate_unsubscription_verification


def authors_allowed(configuration=None):
    allowed = get_data().get('newsletter_configuration', {}).get('authors_allowed', False)
    if configuration:
        return allowed
    return dict(authors_allowed=allowed)


def get_subscribers():
    return NewsletterSubscription.query.filter_by(active=True).all()


def get_subscribers_emails():
    return [subscriber.email for subscriber in get_subscribers()]


def get_subscribers_by_filter(view_filter):
    if view_filter == 'inactive':
        return [subscriber for subscriber in NewsletterSubscription.query.all() if subscriber.active is False]
    elif view_filter == 'active':
        return get_subscribers()
    else:
        return NewsletterSubscription.query.all()


def get_subscribers_dict(subscribers):
    try:
        subscribers_dict = [{'first_name': subscriber.first_name, 'last_name': subscriber.last_name,
                             'email': subscriber.email, 'active': subscriber.active,
                             "unsubscription_reason": subscriber.unsubscription_reason,
                             "unsubscription_explanation": subscriber.unsubscription_explanation,
                             "unsubscription_date": subscriber.unsubscription_date, "date": subscriber.date,
                             "signed_up": User.query.filter_by(email=subscriber.email, confirmed_email=True).first()}
                            for subscriber in subscribers]
        return subscribers_dict
    except AttributeError:
        return abort(400)


def add_subscriber(first_name, last_name, email):
    if first_name and last_name and email:
        requested_subscription = NewsletterSubscription.query.filter_by(email=email).first()
        if requested_subscription:
            if requested_subscription.active:
                flash("You are already subscribed to the newsletter.")
                return redirect(url_for('home.home_page', category='danger'))
            else:
                db.session.delete(requested_subscription)
                db.session.commit()
        new_subscriber = NewsletterSubscription(first_name=first_name, last_name=last_name, email=email,
                                                date=generate_date())
        db.session.add(new_subscriber)
        db.session.commit()
        return generate_subscription_verification(email=email)
    else:
        return abort(400)


def remove_subscriber(email, reason, explanation):
    if email:
        requested_subscription = NewsletterSubscription.query.filter_by(email=email).first()
        if requested_subscription:
            if requested_subscription.active:
                explanation = html2text(explanation) if any(explanation) else "No additional info provided."
                return generate_unsubscription_verification(email=email, reason=reason, explanation=explanation,
                                                            name=requested_subscription.first_name)
            else:
                flash("You're already unsubscribed from our newsletter.")
                return redirect(url_for('home.home_page', category='danger'))
        else:
            flash("Could not find a newsletter subscription with the specified email address.")
            return redirect(url_for('home.home_page', category='danger'))
    else:
        return abort(400)


def validate_newsletter_distribution(requesting_user, newsletter_json):
    required = ['title', 'contents']
    try:
        missing = [key for key in required if key not in list(newsletter_json.keys())]
    except (AttributeError, TypeError):
        return make_response(jsonify(response=f"You are missing the following keys: {', '.join(required)}"), 400)
    if not missing:
        title, contents = newsletter_json['title'], newsletter_json['contents']
        distribution = newsletter_distribution(title, contents, api_call=True)
        if distribution:
            log_api_newsletter_sendout(requesting_user, title, contents)
            return make_response(jsonify(response="Newsletter sent."), 200)
        else:
            return make_response(jsonify(response="Cannot send newsletter, newsletter has no subscribers."), 409)
    else:
        return make_response(jsonify(response=f"You are missing the following keys: {', '.join(missing)}"), 400)


def get_subscription_page_elements():
    try:
        subscription_page = get_data()['newsletter_configuration']
    except KeyError:
        heading = "Subscribe to our newsletter!"
        subheading = "Enjoy all of our internet doses."
    else:
        heading = subscription_page.get('subscription_title', "Enjoy all of our internet doses.")
        subheading = subscription_page.get('subscription_subtitle', "Enjoy all of our internet doses.")

    return heading, subheading


def get_unsubscription_page_elements():
    try:
        config_data = get_data()['newsletter_configuration']
    except KeyError:
        heading = "Unsubscribe from our newsletter"
        subheading = "Not satisfied with our newsletter? Unsubscribe here."
    else:
        heading = config_data.get("unsubscription_title", "Unsubscribe from our newsletter")
        subheading = config_data.get("unsubscription_subtitle", "Not satisfied with our newsletter? Unsubscribe here.")

    return heading, subheading


def newsletter_distribution(title, contents, api_call=False):
    subscribers = get_subscribers_emails()
    contents = html2text(contents)
    if subscribers:
        status = newsletter_notification(title=title, contents=html2text(contents), newsletter_recipients=subscribers)
        if status:
            if not api_call:
                flash(
                    "Newsletter sent successfully." if status else "Sender is not specified, newsletter was not sent.")
                log_newsletter_sendout(title, contents)
                return redirect(url_for('home.home_page', category="success" if status else "danger"))
            else:
                return True
    else:
        if not api_call:
            flash("The newsletter has no subscribers, newsletter was not sent.")
            return redirect(url_for('home.home_page', category='danger'))
        else:
            return False
