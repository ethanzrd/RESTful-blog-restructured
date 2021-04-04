from flask import jsonify, abort

from extensions import db
from logs.functions import log_api_post_edition, log_api_post_addition, log_api_post_deletion
from models import BlogPost
from utils import generate_date


def validate_post_addition(post_json, requesting_user):
    required = ['title', 'subtitle', 'body']
    try:
        missing = [key for key in required if key not in list(post_json.keys())]
    except (AttributeError, TypeError):
        return jsonify(response=f"You are missing the following keys: {', '.join(required)}")
    if not missing:
        try:
            new_post = BlogPost(title=post_json['title'], subtitle=post_json['subtitle'], body=post_json['body'],
                                author=requesting_user, img_url=post_json.get('img_url', ''), date=generate_date())
        except KeyError:
            return jsonify(response="Malformed request."), 400
        else:
            db.session.add(new_post)
            db.session.commit()
            log_api_post_addition(requesting_user=requesting_user, post=new_post)
            return jsonify(message="Post published."), 201
    else:
        return jsonify(response=f"You are missing the following keys: {', '.join(missing)}"), 400


def validate_post_edition(requested_post, changes_json, requesting_user):
    initial_post = requested_post
    try:
        for key in changes_json:
            if key in ['title', 'subtitle', 'body', 'img_url']:
                try:
                    setattr(requested_post, key, changes_json[key])
                except KeyError:
                    return abort(400)
    except TypeError:
        return jsonify(message="Malformed request, maybe you forgot to specify the changes?")
    db.session.commit()
    log_api_post_edition(requested_post=initial_post, changes_json=changes_json, requesting_user=requesting_user)
    return jsonify(message="Post edited successfully."), 200


def validate_post_deletion(requested_post, requesting_user):
    if requested_post:
        db.session.delete(requested_post)
        db.session.commit()
        log_api_post_deletion(requested_post=requested_post, requesting_user=requesting_user)
        return jsonify(message="Post deleted successfully."), 200
    else:
        return jsonify("Malformed request."), 400
