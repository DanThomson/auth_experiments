import os

import flask
import flask_login
import requests
import werkzeug.middleware.proxy_fix

import db
import google
import user


# Localize needed environment variables
port_num = os.environ.get('FLASK_SERVER_PORT', 9091)
secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)


# Create our Flask
app = flask.Flask(__name__)
app.secret_key = secret_key
app.wsgi_app = werkzeug.middleware.proxy_fix.ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)


# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


try:
    db.init_db_command()
except db.OperationalError:
    pass  # Database already initialized


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return user.User.get(user_id)


@app.route('/')
def index():
    user = flask_login.current_user

    if not user.is_authenticated:
        return '<a class="button" href="/login">Google Login</a>'

    # Show user info
    return (
        '<p>Hello, {}! You\'re logged in! Email: {}</p>'
        '<div><p>Google Profile Picture:</p>'
        '<img src="{}" alt="Google profile pic"></img></div>'
        '<a class="button" href="/logout">Logout</a>'.format(
            user.name,
            user.email,
            user.profile_pic,
        )
    )


@app.route('/login')
def login():
    return flask.redirect(google.get_login_uri())


@app.route('/login/callback')
def callback():
    code = flask.request.args.get('code')
    try:
        user = google.receive_user(code)
    except google.NoVerifiedEmail as exc:
        return str(exc), 400

    flask_login.login_user(user)
    return flask.redirect(flask.url_for('index'))


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('index'))
