from flask import Blueprint, render_template
from forms import NewsletterSubscriptionForm, NewsletterUnsubscribeForm, NewNewsletter
from newsletter.functions import get_subscription_page_elements, get_unsubscription_page_elements, add_subscriber, \
    remove_subscriber, get_subscribers, newsletter_distribution
from validation_manager.wrappers import staff_only, newsletter_route, newsletter_staff

newsletter = Blueprint('newsletter', __name__, url_prefix='/newsletter')


@newsletter.route('/subscribe', methods=['GET', 'POST'])
@newsletter_route
def subscribe():
    form = NewsletterSubscriptionForm()
    heading, subheading = get_subscription_page_elements()
    if form.validate_on_submit():
        return add_subscriber(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data)
    return render_template('config.html', config_title=heading,
                           config_desc=subheading, form=form,
                           config_func="newsletter.subscribe")


@newsletter.route('/unsubscribe', methods=['GET', 'POST'])
@newsletter_route
def unsubscribe():
    form = NewsletterUnsubscribeForm()
    heading, subheading = get_unsubscription_page_elements()
    if form.validate_on_submit():
        return remove_subscriber(email=form.email.data, reason=form.reason.data, explanation=form.explanation.data)
    return render_template('config.html', config_title=heading,
                           config_desc=subheading, form=form,
                           config_func="newsletter.unsubscribe")


@newsletter.route('/send-newsletter', methods=['GET', 'POST'])
@staff_only
@newsletter_staff
@newsletter_route
def send_newsletter():
    invalid = False
    kwargs = {"config_title": "New Newsletter", "config_desc": "Send out a newsletter to all newsletter subscribers.",
              "config_func": "newsletter.send_newsletter"}
    if any(get_subscribers()):
        form = NewNewsletter()
        if form.validate_on_submit():
            return newsletter_distribution(title=form.title.data, contents=form.contents.data)
        kwargs['form'] = form
    else:
        invalid = True
    return render_template('config.html', **kwargs, invalid=invalid)
