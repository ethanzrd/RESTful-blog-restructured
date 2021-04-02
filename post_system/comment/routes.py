from flask import Blueprint, request, url_for, abort, flash
from flask_login import current_user, login_required
from werkzeug.utils import redirect
from extensions import db
from forms import ReplyForm, EditCommentForm
from models import Comment
from post_system.comment.functions import get_comment_elements, comment_edition, comment_deletion
from post_system.reply.functions import add_reply
from utils import handle_page

comment = Blueprint('comment', __name__, url_prefix='/comment')


@comment.route('/<int:comment_id>', methods=['GET', 'POST'])
def show_comment(comment_id):
    form = ReplyForm()
    reply_page = request.args.get('c_page', 1)
    deleted = request.args.get('deleted')
    post_id = request.args.get('post_id')
    requested_comment, replies, parent_post = get_comment_elements(comment_id, deleted, post_id)
    if form.validate_on_submit():
        return add_reply(requested_comment, form.reply.data, reply_page)
    return handle_page(endpoint='post.html', count_arg='c_count', page_id=reply_page, page_arg='current_c',
                       items_lst=replies, items_arg='replies', original_comment=requested_comment, post=parent_post,
                       comments=[requested_comment], form=form, deleted=str(deleted), post_id=post_id,
                       comment=True)


@comment.route('/edit/<int:comment_id>', methods=['GET', 'POST'])
def edit_comment(comment_id):
    requested_comment = Comment.query.get(comment_id)
    if requested_comment:
        if current_user.is_authenticated:
            if requested_comment.author.email == current_user.email:
                form = EditCommentForm(comment=requested_comment.comment)
                if form.validate_on_submit():
                    comment_edition(requested_comment=requested_comment, form=form, request='POST')
                comment_edition(requested_comment=requested_comment, form=form)
            else:
                return abort(403)
        else:
            return abort(401)
    else:
        flash("Could not find a comment with the specified ID.")
        return redirect(url_for('home.home_page', category='danger'))


@comment.route('/delete-comment/<int:comment_id>')
@login_required
def delete_comment(comment_id):
    requested_comment = Comment.query.get(comment_id)
    if requested_comment:
        return comment_deletion(requested_comment)
    else:
        return abort(404)
