from flask import jsonify
from flask_login import current_user
from models import Log
from extensions import db
from data_manager import get_data
from utils import generate_date


def get_logs_by_filter(category=None):
    if category == 'newsletter':
        return Log.query.filter_by(category='newsletter').all()
    elif category == 'configuration':
        return Log.query.filter_by(category='configuration').all()
    else:
        return Log.query.all()


def log_changes(configuration, new_configuration, keys_lst, values_lst):
    data = get_data()
    requested_data = data.get(configuration, {})
    track_changes = True if requested_data else False
    changes_lst = []
    for index, value in enumerate(new_configuration):
        if '_' in keys_lst[index]:
            current_key = ' '.join(keys_lst[index].split('_')).title()
        else:
            current_key = keys_lst[index].title()
        current_change = values_lst[index] if str(values_lst[index]).strip() != '' else None
        if not track_changes:
            changes_lst.append(f"{current_key}: {current_change}")
        else:
            try:
                previous_version = data[configuration].get(value, f"{current_key}: {current_change}")
            except KeyError:
                changes_lst.append(f"{current_key}: {current_change}")
                continue
            if values_lst[index] != previous_version:
                changes_lst.append(f"{current_key}: {previous_version} -> {current_change}")
    changes = '<br><br>'.join(changes_lst)
    if any(changes_lst):
        new_log = Log(user=current_user, user_name=current_user.name, category='configuration',
                      description=f"{current_user.name} configured the {' '.join(configuration.split('_')).title()}."
                                  f"<br><br>"
                                  f"Changes:<br><br>{changes}", date=generate_date(), user_email=current_user.email)
        db.session.add(new_log)
        db.session.commit()


def log_api_post_addition(post, requesting_user):
    new_log = Log(user=requesting_user, user_name=requesting_user.name, category='api_request',
                  description=f"{requesting_user.name} published a post via an API request.<br><br>"
                              f'Post ID: {post.id}',
                  date=generate_date(), user_email=requesting_user.email)
    db.session.add(new_log)
    db.session.commit()


def log_api_post_edition(requested_post, changes_json, requesting_user):
    changes = []
    for key in changes_json:
        if getattr(requested_post, key) != changes_json[key] and any(str(changes_json[key]).strip()):
            new_change = f"{key.title() if key != 'img_url' else 'Image URL'}:" \
                         f" {requested_post[key]} -> {changes_json[key]}"
            changes.append(new_change)
    changes_description = '<br><br>'.join(changes)
    if any(changes):
        new_log = Log(user=requesting_user, user_name=requesting_user.name, category='api_request',
                      description=f"{requesting_user.name} edited a post via an API request.<br>"
                                  f'Post ID: {requested_post.id}<br><br>'
                                  f'Changes:<br><br>{changes_description}', user_email=requesting_user.emai,
                      date=generate_date())
        db.session.add(new_log)
        db.session.commit()


def log_api_post_deletion(requested_post, requesting_user):
    post_information = [f"Author - {requested_post.author.name}",
                        f"Title - {requested_post.title}",
                        f"Subtitle - {requested_post.subtitle}"]
    log_information = '<br><br>'.join(post_information)
    new_log = Log(user=requesting_user, user_name=requesting_user.name, category='api_request',
                  description=f"{requesting_user.name} deleted a post via an API request.<br><br>"
                              f"Post Details:<br><br>{log_information}", user_email=requesting_user.email,
                  date=generate_date())
    db.session.add(new_log)
    db.session.commit()


def log_newsletter_sendout(title, contents):
    new_log = Log(user=current_user,
                  description=f"{current_user.name} sent out a newsletter.<br><br>"
                              f"Title: {title}<br><br>Contents: {contents}",
                  user_name=current_user.name, date=generate_date(), category='newsletter',
                  user_email=current_user.email)
    db.session.add(new_log)
    db.session.commit()


def log_api_newsletter_sendout(requesting_user, title, contents):
    new_log = Log(user=requesting_user,
                  description=f"{requesting_user.name} sent out a newsletter via an API request.<br><br>"
                              f"Title: {title}<br><br>Contents: {contents}",
                  user_name=requesting_user.name, date=generate_date(), category='api_request',
                  user_email=requesting_user.email)
    db.session.add(new_log)
    db.session.commit()
