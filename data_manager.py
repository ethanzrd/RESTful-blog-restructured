import os
from werkzeug.security import generate_password_hash
from settings import EMAIL
from sqlalchemy.exc import OperationalError
from flask import redirect, url_for
from models import Data
from extensions import db


def get_data(homepage=False):  # GET CONFIG DATA
    def set_default():
        default_data = {"secret_password": generate_password_hash(password="default",
                                                                  method='pbkdf2:sha256', salt_length=8),
                        "website_configuration": {
                            "name": "Website",
                            "homepage_title": "A website",
                            "homepage_subtitle": "A fully fledged website",
                            "background_image": "https://www.panggi.com/images/featured/python.png",
                            "twitter_link": "https://www.twitter.com",
                            "github_link": "https://www.github.com",
                            "facebook_link": "https://www.facebook.com",
                            "instagram_link": "https://www.instagram.com",
                            "youtube_link": "https://www.youtube.com",
                            "linkedin_link": "https://www.linkedin.com",
                            "dev_link": "https://dev.to",
                            "whatsapp_link": "https://www.whatsapp.com",
                            "reddit_link": "https://www.reddit.com",
                            "pinterest_link": "https://www.pinterest.com",
                            "telegram_link": "https://www.telegram.com"
                        },
                        "api_configuration": {
                            "all_posts": True,
                            "all_users": True,
                            "random_post": True
                        },
                        "newsletter_configuration": {
                            'subscription_title': 'Subscribe to our newsletter!',
                            'subscription_subtitle': 'Get all of our internet doses!',
                            'unsubscription_title': 'Unsubscribe from our newsletter',
                            'unsubscription_subtitle': 'Dissatisfied with our newsletter? Unsubscribe here.',
                            'authors_allowed': False,
                            'enabled': False
                        },
                        "contact_configuration": {
                            "page_heading": "Contact us",
                            "page_subheading": "Contact us, and we'll respond as soon as we can.",
                            "page_description": "With the current workload, we are able to respond within 24 hours.",
                            "background_image": "https://www.panggi.com/images/featured/python.png",
                            "support_email": os.environ.get('EMAIL', EMAIL)
                        },
                        "about_configuration": {
                            "page_heading": "About us",
                            "page_subheading": "About what we do.",
                            "background_image": "https://www.panggi.com/images/featured/python.png",
                            "page_content": "For now, this page remains empty."
                        }
                        }
        update_data(default_data)

    try:
        data = Data.query.all()[0].json_column
        if homepage:
            title = data["website_configuration"]["homepage_title"]
            subtitle = data["website_configuration"]["homepage_subtitle"]
            return title, subtitle
        else:
            return data
    except (KeyError, TypeError, OperationalError):
        if homepage:
            title = "A website."
            subtitle = "A fully-fledged website."
            return title, subtitle
        else:
            return {}
    except (AttributeError, IndexError):
        set_default()
        if homepage:
            get_data(homepage=True)
        else:
            get_data()
        return redirect(url_for("home"))


def update_data(given_data):
    new_data = Data(json_column=given_data)
    if len(Data.query.all()) > 0 and Data.query.all()[0] is not None:
        db.session.delete(Data.query.all()[0])
    db.session.add(new_data)
    db.session.commit()
