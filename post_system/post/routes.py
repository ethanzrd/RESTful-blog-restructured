from flask import Blueprint, request, render_template
from flask_login import current_user
from forms import CommentForm, CreatePostForm
from models import BlogPost, DeletedPost
from flask import abort
from post_system.comment.functions import add_comment
from post_system.post.functions import get_post_elements, post_addition, post_edition, get_deleted_posts, post_deletion, \
    post_recovery, post_permanent_deletion
from utils import handle_page
from validation_manager.wrappers import staff_only, admin_only
post = Blueprint('post', __name__, url_prefix='/post')


@post.route("/<int:post_id>", methods=['GET', 'POST'])
def show_post(post_id):
    deleted = request.args.get('deleted')
    comment_page = request.args.get('c_page', 1)
    form = CommentForm()
    requested_post, post_comments = get_post_elements(post_id, deleted)
    if form.validate_on_submit():
        return add_comment(requested_post, form.comment.data)
    return handle_page("post.html", post=requested_post, deleted=str(deleted), post_id=post_id,
                       form=form, items_arg='comments', count_arg='c_count', items_lst=post_comments,
                       page_arg='current_c', page_id=comment_page)


@post.route('/add', methods=['GET', 'POST'])
@staff_only
def add_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        return post_addition(form)
    return render_template('make-post.html', form=form)


@post.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@staff_only
def edit_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    if requested_post:
        if current_user.is_authenticated:
            if requested_post.author.email == current_user.email:
                form = CreatePostForm(title=requested_post.title,
                                      subtitle=requested_post.subtitle,
                                      img_url=requested_post.img_url,
                                      body=requested_post.body)
                if form.validate_on_submit():
                    return post_edition(requested_post=requested_post, form=form, request='POST')
                else:
                    return post_edition(requested_post=requested_post, form=form, request='GET')
            else:
                return abort(403)
        else:
            return abort(401)
    else:
        return abort(404)


@post.route('/deleted')
@post.route('/deleted/<int:page_id>')
@staff_only
def deleted_posts(page_id=1):
    return handle_page(endpoint='index.html', items_lst=get_deleted_posts(), deleted="True", items_arg='deleted_posts',
                       title="Deleted Posts", subtitle="View and recover deleted posts!", page_id=page_id)


@post.route('/delete/<int:post_id>')
@staff_only
def delete_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    if requested_post:
        return post_deletion(requested_post)
    else:
        return abort(404)


@post.route('/recover/<int:post_id>')
@staff_only
def recover_post(post_id):
    try:
        database_entry = DeletedPost.query.get(post_id)
        requested_post = database_entry.json_column
    except AttributeError:
        return abort(404)
    if database_entry and requested_post:
        return post_recovery(database_entry, requested_post)
    else:
        return abort(400)


@post.route('/perm-delete/<int:post_id>')
@admin_only
def perm_delete(post_id):
    try:
        database_entry = DeletedPost.query.get(post_id)
    except AttributeError:
        return abort(404)
    else:
        return post_permanent_deletion(database_entry)
