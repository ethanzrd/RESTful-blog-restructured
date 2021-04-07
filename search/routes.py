from flask import Blueprint, render_template, request
from forms import SearchForm
from search.functions import display_results

search_routing = Blueprint('search', __name__, url_prefix='/search')


@search_routing.route('/', methods=['GET', 'POST'])
@search_routing.route('<int:page_id>', methods=['GET', 'POST'])
def search(page_id=1):
    category = request.args.get('category', 'posts')
    query = request.args.get('query', None)
    if not query:
        form = SearchForm()
        if form.validate_on_submit():
            return display_results(search_query=form.search.data, category=form.category.data)
    else:
        return display_results(search_query=query, category=category, page_id=page_id)
    return render_template('search.html', form=form)
