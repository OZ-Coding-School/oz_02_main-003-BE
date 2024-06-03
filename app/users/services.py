import urllib.parse
import urllib.request
import json

from common.data.envdata import GOOGLE_OAUTH2_CLIENT_ID, GOOGLE_OAUTH2_CLIENT_SECRET

from django.core.exceptions import ValidationError

GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'


def google_get_access_token(google_token_api, code):
    client_id = GOOGLE_OAUTH2_CLIENT_ID
    client_secret = GOOGLE_OAUTH2_CLIENT_SECRET
    grant_type = 'authorization_code'
    redirection_uri = "http://127.0.0.1:8000/api/v1/users/auth/google/callback"
    state = "random_string"

    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'grant_type': grant_type,
        'redirect_uri': redirection_uri,
        'state': state,
    }

    url = f"{google_token_api}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, method="POST")
    try:
        with urllib.request.urlopen(request) as response:
            if response.status != 200:
                raise ValidationError('google_token is invalid')

            token_response = json.loads(response.read().decode())
            access_token = token_response.get('access_token')

            return access_token
    except urllib.error.URLError as e:
        raise ValidationError(f'Failed to obtain access token from Google: {e.reason}')


def google_get_user_info(access_token):
    params = {
        'access_token': access_token
    }

    url = f"{GOOGLE_USER_INFO_URL}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url)

    try:
        with urllib.request.urlopen(request) as response:
            if response.status != 200:
                raise ValidationError('Failed to obtain user info from Google.')

            user_info = json.loads(response.read().decode())

            return user_info
    except urllib.error.URLError as e:
        raise ValidationError(f'Failed to obtain user info from Google: {e.reason}')
