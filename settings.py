from itsdangerous import URLSafeTimedSerializer
from app_config import MAIL_USERNAME, SECRET_KEY

EMAIL = MAIL_USERNAME
serializer = URLSafeTimedSerializer(SECRET_KEY)
MAX_POSTS_PER_PAGE = 3
TOKEN_AGE = 259200
CONFIG_KEYS = {'about_configuration': ['page_heading', 'page_subheading', 'page_content', 'background_image'],
               'website_configuration': ['name', 'homepage_title', 'homepage_subtitle', 'background_image',
                                         'dev_link', 'twitter_link', 'facebook_link', 'github_link', 'youtube_link',
                                         'linkedin_link', 'instagram_link', 'whatsapp_link', 'reddit_link',
                                         'pinterest_link', 'telegram_link'],
               'contact_configuration': ['page_heading', 'page_subheading', 'page_description', 'background_image',
                                         'support_email'],
               'api_configuration': ['all_posts', 'all_users', 'random_post', 'random_user', 'get_post', 'add_post',
                                     'edit_post', 'delete_post', 'newsletter_sendout'],
               'newsletter_configuration': ['subscription_title', 'subscription_subtitle',
                                            'unsubscription_title', 'unsubscription_subtitle',
                                            'authors_allowed', 'enabled']}
API_METHODS = {'get': 'get_post', 'post': 'add_post', 'put': 'edit_post', 'delete': 'delete_post'}