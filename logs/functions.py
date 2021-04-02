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
        current_change = values_lst[index] if values_lst[index].strip() != '' else None
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
