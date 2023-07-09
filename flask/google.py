import json
import os

import flask
import oauthlib.oauth2
import requests

from user import User


# In a larger app this would be defined somewhere else and imported to this module
class NoVerifiedEmail(Exception):
    pass


# key_key maps keynames used by google to keynames used by flask's user object
key_key = [
    ('sub', 'id_'),
    ('given_name', 'name'),
    ('email', 'email'),
    ('picture', 'profile_pic')
]


GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = os.environ.get('GOOGLE_DISCOVERY_URL', 'https://accounts.google.com/.well-known/openid-configuration')


# We presume that google doesn't change its provider_cfg within the timeframe this app runs
provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
client = oauthlib.oauth2.WebApplicationClient(GOOGLE_CLIENT_ID)


def get_login_uri():
    authorization_endpoint = provider_cfg['authorization_endpoint']
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=flask.request.base_url + '/callback',
        scope=['openid', 'email', 'profile'],
    )

    return request_uri


def receive_user(code):
    token_url, headers, body = client.prepare_token_request(
        provider_cfg['token_endpoint'],
        authorization_response=flask.request.url,
        redirect_url=flask.request.base_url,
        code=code,
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    # Get userinfo
    uri, headers, body = client.add_token(provider_cfg['userinfo_endpoint'])
    userinfo_response = requests.get(uri, headers=headers, data=body)
    userinfo = userinfo_response.json()

    if not userinfo.get('email_verified', False):
        raise NoVerifiedEmail('User email not available or not verified by Google')

    user_attributes = {
        user_key: userinfo[google_key] for google_key, user_key in key_key
    }
    return User(**user_attributes)
