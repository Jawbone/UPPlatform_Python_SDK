"""
This is the Python SDK for the Jawbone UP API.

For API details: https://jawbone.com/up/developer
For SDK details: https://github.com/Jawbone/UPPlatform_Python_SDK

When testing, if you are unable to use HTTPS, you will need to do one of the following:

1. Set an environment variable.

export OAUTHLIB_INSECURE_TRANSPORT=1

2. Set the above in Python (somewhere before you import the SDK)

import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
"""
import upapi.endpoints
import upapi.meta
import upapi.base
import upapi.user

"""
Set these variables with the values for your app from https://developer.jawbone.com

If you have multiple redirect URLs, you can change this value as needed.

If you do not specify a token_saver, upapi will not automatically refresh expired tokens.

If you specify a token, the SDK will use it to establish the OAuth connection. A token refresh or disconnect
will automatically update this variable.
"""
client_id = None
client_secret = None
redirect_uri = None
scope = None
token_saver = None
token = None


def up():
    """
    Create an UpApi object with the global properties.

    :return: upapi.base.UpApi object
    """
    return upapi.base.UpApi(
        client_id,
        client_secret,
        app_redirect_uri=redirect_uri,
        app_scope=scope,
        app_token_saver=token_saver,
        app_token=token)


def get_redirect_url():
    """
    Get the URL to redirect new users to where they grant access to your application.

    :return: your app-specific URL
    """
    authorization_url, state = up().oauth.authorization_url(upapi.endpoints.AUTH)
    return authorization_url


def get_token(callback_url):
    """
    Retrieve the OAuth token from the server based on the authorization code in the callback_url.

    :param callback_url: the URL on your server that Jawbone sent the user back to
    :return: a dictionary containing the token
    """
    global token
    token = up().get_up_token(callback_url)
    return token


def refresh_token():
    """
    Manually refresh your OAuth token.

    :return: the new token
    """
    global token
    token = up().refresh_token()
    return token


def get_user():
    """
    Create a User object with the global properties.

    :return: upapi.user.User object
    """
    return upapi.user.User(
        client_id,
        client_secret,
        app_redirect_uri=redirect_uri,
        app_scope=scope,
        app_token_saver=token_saver,
        app_token=token)


def disconnect():
    """
    Revoke the API access for this user.
    """
    up().disconnect()
    global token
    token = None
