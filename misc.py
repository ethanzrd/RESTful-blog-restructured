from werkzeug.security import generate_password_hash

from settings import EMAIL

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
                    "all_posts": False,
                    "all_users": False,
                    "random_post": False,
                    "random_user": False,
                    "get_post": False,
                    "add_post": False,
                    "edit_post": False,
                    "delete_post": False,
                    "newsletter_sendout": False
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
                    "support_email": EMAIL
                },
                "about_configuration": {
                    "page_heading": "About us",
                    "page_subheading": "About what we do.",
                    "background_image": "https://www.panggi.com/images/featured/python.png",
                    "page_content": "For now, this page remains empty."
                }
                }
