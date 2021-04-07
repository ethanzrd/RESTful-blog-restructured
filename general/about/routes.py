from flask import Blueprint, render_template
from general.about.functions import get_page_elements

about_routing = Blueprint('about', __name__, url_prefix='/about')


@about_routing.route("/")
def about():
    heading, subheading, content, background_image = get_page_elements()
    return render_template("about.html", heading=heading, subheading=subheading, content=content,
                           background_image=background_image)
