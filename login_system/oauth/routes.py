from flask import Blueprint, abort, redirect, url_for, flash, session
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.twitter import twitter
from flask_dance.contrib.github import github
from flask_dance.contrib.google import google
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError, InvalidClientIdError
from login_system.oauth.wrappers import provider_auth_required, provider_linked, provider_not_linked
from validation_manager.wrappers import logout_required
from login_system.oauth.functions import link_provider, unlink_provider, login_with_provider

oauth_routing = Blueprint('oauth', __name__)


def retrieve_twitter_screen_name():
    account_info = twitter.get('account/settings.json')

    if account_info.ok:
        account_info_json = account_info.json()
        screen_name = account_info_json['screen_name']
        return screen_name
    else:
        return False


def retrieve_github_id():
    account_info = github.get('/user')

    if account_info.ok:
        account_info_json = account_info.json()
        account_id = int(account_info_json['id'])
        return account_id
    else:
        return False


def retrieve_google_id():
    try:
        account_info = google.get('/oauth2/v1/userinfo')
    except (TokenExpiredError, InvalidClientIdError):
        session.clear()
        return redirect(url_for('google.login'))

    if account_info.ok:
        account_info_json = account_info.json()
        account_id = str(account_info_json['id'])
        return account_id
    else:
        return False


@oauth_routing.route('/link-twitter')
@provider_not_linked(provider_identifier='twitter_name')
@provider_auth_required(provider_object=twitter, login_route='twitter.login')
def link_twitter():
    return link_provider(user_identifier=retrieve_twitter_screen_name(), provider_identifier='twitter_name',
                         provider='Twitter')


@oauth_routing.route('/link-github')
@provider_not_linked(provider_identifier='github_id')
@provider_auth_required(provider_object=github, login_route='github.login')
def link_github():
    return link_provider(user_identifier=retrieve_github_id(), provider_identifier='github_id', provider='GitHub')


@oauth_routing.route('/link-google')
@provider_not_linked(provider_identifier='google_id')
@provider_auth_required(provider_object=google, login_route='google.login')
def link_google():
    return link_provider(user_identifier=retrieve_google_id(), provider_identifier='google_id', provider='Google')


@oauth_routing.route('/unlink-twitter')
@provider_linked(provider_identifier='twitter_name')
def unlink_twitter():
    return unlink_provider(provider_identifier='twitter_name', provider='Twitter')


@oauth_routing.route('/unlink-github')
@provider_linked(provider_identifier='github_id')
def unlink_github():
    return unlink_provider(provider_identifier='github_id', provider='GitHub')


@oauth_routing.route('/unlink-google')
@provider_linked(provider_identifier='google_id')
def unlink_google():
    return unlink_provider(provider_identifier='google_id', provider='Google')


@oauth_routing.route('/login-twitter')
@logout_required
@provider_auth_required(provider_object=twitter, login_route='twitter.login')
def login_with_twitter():
    return login_with_provider(provider_identifier='twitter_name', user_identifier=retrieve_twitter_screen_name())


@oauth_routing.route('/login-github')
@logout_required
@provider_auth_required(provider_object=github, login_route='github.login')
def login_with_github():
    return login_with_provider(provider_identifier='github_id', user_identifier=retrieve_github_id())


@oauth_routing.route('/login-google')
@logout_required
@provider_auth_required(provider_object=google, login_route='google.login')
def login_with_google():
    return login_with_provider(provider_identifier='google_id', user_identifier=retrieve_google_id())


@oauth_authorized.connect
def redirect_to_next_url(blueprint, token):
    """
    allows the the callback url to be dynamic without having to register
    each protected endpoint as a redirect with OAuth2ConsumerBlueprint.
    """
    blueprint.token = token
    next_url = session.get('next_url', '/')
    session.pop('next_url', None)
    return redirect(next_url)
