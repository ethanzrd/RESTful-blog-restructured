from flask import Blueprint
from forms import EditReplyForm
from post_system.reply.functions import reply_deletion, reply_edition
from flask import request, abort
from models import Reply

reply = Blueprint('reply', __name__, url_prefix='/reply')


@reply.route('/delete/<int:reply_id>')
def delete_reply(reply_id):
    requested_reply = Reply.query.get(reply_id)
    current_c = request.args.get('c_page', 1)
    if requested_reply:
        return reply_deletion(requested_reply, current_c)
    else:
        return abort(404)


@reply.route('/edit/<int:reply_id>', methods=['GET', 'POST'])
def edit_reply(reply_id):
    requested_reply = Reply.query.get(reply_id)
    current_c = request.args.get('c_page', 1)
    form = EditReplyForm(reply=requested_reply.reply)
    if requested_reply:
        if form.validate_on_submit():
            return reply_edition(requested_reply=requested_reply, form=form, current_page=current_c, request='POST')
        return reply_edition(requested_reply=requested_reply, form=form, current_page=current_c, request='GET')
    else:
        return abort(404)
