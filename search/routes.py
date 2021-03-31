from flask import Blueprint, render_template
from forms import SearchForm
from search.functions import display_results

search_routing = Blueprint('search', __name__, url_prefix='/search')


@search_routing.route('/', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        return display_results(search_query=form.search.data, category=form.category.data)
    return render_template('search.html', form=form)
