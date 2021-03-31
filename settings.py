from itsdangerous import URLSafeTimedSerializer
from app_config import MAIL_USERNAME, SECRET_KEY

EMAIL = MAIL_USERNAME
serializer = URLSafeTimedSerializer(SECRET_KEY)
MAX_POSTS_PER_PAGE = 3
TOKEN_AGE = 259200
CONFIG_KEYS = {'about_configuration': ['page_heading', 'page_subheading', 'page_content', 'background_image'],
               'website_configuration': ['name', 'homepage_title', 'homepage_subtitle', 'navigation_bar_color',
                                         'background_image',
                                         'dev_link',
                                         'twitter_link', 'facebook_link', 'github_link', 'youtube_link',
                                         'linkedin_link', 'instagram_link'],
               'contact_configuration': ['page_heading', 'page_subheading', 'page_description', 'background_image',
                                         'support_email'],
               'api_configuration': ['all_posts', 'all_users', 'random_post']}
