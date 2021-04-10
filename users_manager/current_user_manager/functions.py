from models import User, ApiKey, DeletionReport, Log


def get_user_posts(user_id):
    try:
        return User.query.get(user_id).posts
    except AttributeError:
        return []


def get_user_comments(user_id):
    try:
        return User.query.get(user_id).comments
    except AttributeError:
        return []


def get_user_notifications(user_id):
    try:
        return User.query.get(user_id).notifications
    except AttributeError:
        return []


def get_full_users_dict(users=None):
    if users:
        users_dict = {users.index(user) + 1: {"id": user.id,
                                              "email": user.email,
                                              "username": user.name,
                                              "posts_num":
                                                  len(user.posts),
                                              "is_developer": user_has_api_key(user.id),
                                              "pending_deletion": user_has_deletion_request(user.id),
                                              "permissions": [
                                                  "Administrator" if user.admin else "Author"
                                                  if user.author else "Developer"
                                                  if user_has_api_key(
                                                      user.id) else "Registered User"
                                                  if user.confirmed_email else None][0],
                                              "confirmed": user.confirmed_email,
                                              "joined_on": user.join_date} for user in users}
        return users_dict
    return {}


def get_user_deletion_report(user_id):
    try:
        requested_report = DeletionReport.query.filter_by(user_id=user_id).first()
    except AttributeError:
        return None
    if requested_report:
        report_dict = {1: {"name": "Deletion Request Report",
                           "description": "View Report",
                           "Deletion Reason": requested_report.deletion_reason,
                           "Additional Information": requested_report.deletion_explanation,
                           "Submitted on": requested_report.date,
                           "approval": requested_report.approval_link,
                           "rejection": requested_report.rejection_link}}
        return report_dict
    return None


def get_user_api(user_id):
    try:
        requested_api = ApiKey.query.filter_by(developer_id=user_id).first()
    except AttributeError:
        return
    if requested_api is not None:
        api_dict = {1: {"key_id": requested_api.id,
                        "name": "API Key Status",
                        "description": "API Key Status | " + "Online" if requested_api.blocked is False else "Blocked",
                        "Developer's Occupation": requested_api.occupation,
                        "Application": requested_api.application,
                        "API Usage": requested_api.usage,
                        "API Key": requested_api.api_key},
                    2: {"name": "API Requests",
                        "description": "API Request Statistics",
                        "Total Requests": sum([requested_api.all_posts, requested_api.random_post,
                                               requested_api.all_users, requested_api.random_user]),
                        "All Posts Requests": requested_api.all_posts,
                        "Random Post Requests": requested_api.random_post,
                        "All Users Requests": requested_api.all_users,
                        "Random User Requests": requested_api.random_user}}
        website_operation_requests = Log.query.filter_by(user=requested_api.developer, category='api_request').all()
        if website_operation_requests:
            api_dict[3] = {"name": "Website Operations Requests",
                           "description": "Website Operations Request Statistics",
                           "Total Requests": len(website_operation_requests),
                           "Get Post Requests": requested_api.get_post,
                           "Add Post Requests": requested_api.add_post,
                           "Edit Post Requests": requested_api.edit_post,
                           "Delete Post Requests": requested_api.delete_post,
                           "Newsletter Sendout Requests": requested_api.newsletter_sendout}
        return api_dict
    return


def user_has_api_key(user_id):
    return ApiKey.query.filter_by(developer_id=user_id).first() is not None


def user_has_deletion_request(user_id):
    return DeletionReport.query.filter_by(user_id=user_id).first() is not None
