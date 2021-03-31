from flask import render_template


def unauthorized(e):
    return render_template('http-error.html',
                           error="401 - Unauthorized", error_description="You're unauthorized to perform this action.",
                           ), 401


def forbidden(e):
    return render_template('http-error.html',
                           error="403 - Forbidden", error_description="You're unauthorized to perform this action.",
                           ), 403


def not_found(e):
    return render_template('http-error.html',
                           error="404 - Page Not Found", error_description="Page not found.",
                           ), 404


def internal_error(e):
    return render_template('http-error.html',
                           error="500 - Internal Server Error", error_description="An error has occurred on our side, "
                                                                                  "we apologize for the inconvenience.",
                           ), 500


def bad_request(e):
    return render_template('http-error.html',
                           error="400 - Bad Request", error_description="The browser sent a request that the server"
                                                                        " could not understand,"
                                                                        " we apologize for the inconvenience.",
                           ), 500