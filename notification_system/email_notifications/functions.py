from extensions import mail
from flask import flash, redirect, url_for


def send_mail(msg):
    try:
        mail.send(msg)
        return True
    except AssertionError:
        flash("Sender Email is not specified, please contact the website staff.")
        return redirect(url_for('home.home_page', category='danger'))
