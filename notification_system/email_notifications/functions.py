from extensions import mail
from flask import flash, redirect, url_for


def send_mail(msg, allow_redirects=True):
    try:
        mail.send(msg)
        return True
    except AssertionError:
        if allow_redirects:
            flash("Sender Email is not specified, please contact the website staff.")
            return redirect(url_for('home.home_page', category='danger'))
        return False
