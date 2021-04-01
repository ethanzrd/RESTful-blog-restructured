from html2text import html2text
from werkzeug.utils import redirect

from data_manager import get_data
from models import NewsletterSubscription
from flask import abort, flash, url_for
from extensions import db
from notification_system.email_notifications.notifications import newsletter_notification
from verification_manager.generate_verification import generate_subscription_verification, \
    generate_unsubscription_verification


def authors_allowed():
    return get_data().get('newsletter_configuration', {}).get('authors_allowed', False)


def get_subscribers():
    return [subscriber for subscriber in NewsletterSubscription.query.all() if subscriber.active]


def get_subscribers_emails():
    return [subscriber.email for subscriber in get_subscribers()]


def add_subscriber(first_name, last_name, email):
    if first_name and last_name and email:
        requested_subscription = NewsletterSubscription.query.filter_by(email=email).first()
        if requested_subscription:
            if requested_subscription.active:
                flash("You are already subscribed to the newsletter.")
                return redirect(url_for('home.home_page', category='danger'))
            else:
                db.session.delete(requested_subscription)
        new_subscriber = NewsletterSubscription(first_name=first_name, last_name=last_name, email=email)
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


def newsletter_distribution(title, contents):
    subscribers = get_subscribers_emails()
    if any(subscribers):
        status = newsletter_notification(title=title, contents=html2text(contents), newsletter_recipients=subscribers)
        flash("Newsletter sent successfully." if status else "Sender is not specified, newsletter was not sent.")
        return redirect(url_for('home.home_page', category="success" if status else "danger"))
    else:
        flash("The newsletter has no subscribers, newsletter was not sent.")
        return redirect(url_for('home.home_page', category='danger'))
