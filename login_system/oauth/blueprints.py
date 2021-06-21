from flask_dance.contrib.twitter import make_twitter_blueprint
from flask_dance.contrib.github import make_github_blueprint
from flask_dance.contrib.google import make_google_blueprint
from login_system.oauth.config import TWITTER_API_KEY, TWITTER_API_SECRET, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GOOGLE_CLIENT_ID, \
    GOOGLE_CLIENT_SECRET

twitter_blueprint = make_twitter_blueprint(api_key=TWITTER_API_KEY, api_secret=TWITTER_API_SECRET)
github_blueprint = make_github_blueprint(client_id=GITHUB_CLIENT_ID, client_secret=GITHUB_CLIENT_SECRET)
google_blueprint = make_google_blueprint(client_id=GOOGLE_CLIENT_ID, client_secret=GOOGLE_CLIENT_SECRET)
