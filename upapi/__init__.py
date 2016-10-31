"""
This is the Python SDK for the Jawbone UP API.

For API details: https://jawbone.com/up/developer
For SDK details: https://github.com/Jawbone/UPPlatform_Python_SDK
"""
import upapi.endpoints
import upapi.base
import upapi.user

"""
Set these variables with the values for your app from https://developer.jawbone.com

If you have multiple redirect URLs, you can change this value as needed.

If you specify a credentials object or a token, the SDK will use it to establish the OAuth connection. Manually
refreshing the token or disconnecting will automatically update these variables.
"""
client_id = None
client_secret = None
redirect_uri = None
scope = None
credentials_saver = None
credentials = None
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
        redirect_uri,
        app_scope=scope,
        credentials_saver=credentials_saver,
        user_credentials=credentials,
        token_saver=token_saver,
        user_token=token)


def get_redirect_url():
    """
    Get the URL to redirect new users to where they grant access to your application.

    :return: your app-specific URL
    """
    return up().get_redirect_url()


def get_token(callback_url):
    """
    Retrieve the OAuth token from the server based on the authorization code in the callback_url.

    :param callback_url: the URL on your server that Jawbone sent the user back to
    :return: a dictionary containing the token
    """
    global token, credentials
    my_up = up()
    token = my_up.get_up_token(callback_url)
    credentials = my_up.credentials
    return token


def refresh_token():
    """
    Manually refresh your OAuth token.

    :return: the new token
    """
    global token, credentials
    my_up = up()
    token = my_up.refresh_token()
    credentials = my_up.credentials
    return token


def get_user():
    """
    Create a User object with the global properties.

    :return: upapi.user.User object
    """
    return upapi.user.User(
        client_id,
        client_secret,
        redirect_uri,
        app_scope=scope,
        credentials_saver=credentials_saver,
        user_credentials=credentials,
        token_saver=token_saver,
        user_token=token)


def disconnect():
    """
    Revoke the API access for this user.
    """
    up().disconnect()
    global token, credentials
    token = None
    credentials = None
