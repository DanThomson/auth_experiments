import json
import os
import sqlite3

import requests

from flask import Flask, redirect, request, url_for
from flask_login import LoginManager
from flask_login import current_user, login_required, login_user, logout_user

from oauthlib.oauth2 import WebApplicationClient
from werkzeug.middleware.proxy_fix import ProxyFix

from db import init_db_command
from user import User


GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = os.environ.get('GOOGLE_DISCOVERY_URL', 'https://accounts.google.com/.well-known/openid-configuration')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)

try:
    init_db_command()
except sqlite3.OperationalError:
    pass  # Database already initialized

client = WebApplicationClient(GOOGLE_CLIENT_ID)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/')
def index():
    if current_user.is_authenticated:
        return (
            '<p>Hello, {}! You\'re logged in! Email: {}</p>'
            '<div><p>Google Profile Picture:</p>'
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name,
                current_user.email,
                current_user.profile_pic,
            )
        )
    else:
        return '<a class="button" href="/login">Google Login</a>'


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route('/login')
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg['authorization_endpoint']

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + '/callback',
        scope=['openid', 'email', 'profile'],
    )

    return redirect(request_uri)


@app.route('/login/callback')
def callback():
    code = request.args.get('code')
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg['token_endpoint']

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg['userinfo_endpoint']
    uri, headers, body = client.add_token(userinfo_endpoint)

    userinfo_response = requests.get(uri, headers=headers, data=body)
    userinfo_response_json = userinfo_response.json()

    if userinfo_response_json.get('email_verified'):
        unique_id = userinfo_response_json['sub']
        user_name = userinfo_response_json['given_name']
        users_email = userinfo_response_json['email']
        picture = userinfo_response_json['picture']
    else:
        'User email not available or not verified by Google', 400

    user = User(id_=unique_id, name=user_name, email=users_email, profile_pic=picture)

    if not User.get(unique_id):
        User.create(unique_id, user_name, users_email, picture)

    login_user(user)

    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__=='__main__':
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
    app.run(
        host='0.0.0.0',
        port=os.environ.get("FLASK_SERVER_PORT", 9090),
        # debug=True,
    )
