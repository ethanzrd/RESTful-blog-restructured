from misc import default_data
from sqlalchemy.exc import OperationalError
from flask import redirect, url_for
from models import Data
from extensions import db


def get_data(homepage=False):  # GET CONFIG DATA
    def set_default():
        update_data(default_data)
    try:
        data = Data.query.all()[0].json_column
        if homepage:
            title = data["website_configuration"]["homepage_title"]
            subtitle = data["website_configuration"]["homepage_subtitle"]
            return title, subtitle
        else:
            return data
    except (KeyError, TypeError, OperationalError):
        if homepage:
            title = "A website."
            subtitle = "A fully-fledged website."
            return title, subtitle
        else:
            return {}
    except (AttributeError, IndexError):
        set_default()
        if homepage:
            get_data(homepage=True)
        else:
            get_data()
        return redirect(url_for("home"))


def update_data(given_data):
    new_data = Data(json_column=given_data)
    if len(Data.query.all()) > 0 and Data.query.all()[0] is not None:
        db.session.delete(Data.query.all()[0])
    db.session.add(new_data)
    db.session.commit()
