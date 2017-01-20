"""
This is the Python SDK for the Jawbone UP API.

For API details: https://jawbone.com/up/developer
For SDK details: https://github.com/Jawbone/UPPlatform_Python_SDK
"""
import upapi.endpoints
import upapi.exceptions
import upapi.base
import upapi.user

"""
Set these variables with the values for your app from https://developer.jawbone.com

If you have multiple redirect URLs, you can change this value as needed.

If you specify a credentials_storage object, the SDK will use it to save automatically refreshed credentials. Refer to
http://oauth2client.readthedocs.io/en/latest/source/oauth2client.client.html#oauth2client.client.Storage and
https://developers.google.com/api-client-library/python/guide/aaa_oauth#storage for details on storage objects.

If you specify a credentials object, the SDK will use it to establish the OAuth connection. Manually
refreshing the token or disconnecting will automatically update the credentials variable.

If you only have an access token and not a credentials object, you can use set_access_token, which will set the
credentials variable from that token.
"""
client_id = None
client_secret = None
redirect_uri = None
scope = None
credentials_storage = None
credentials = None


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
        credentials_storage=credentials_storage,
        user_credentials=credentials)


"""
upapi stores access tokens as Credentials objects. If you prefer to use the access tokens returned from the UP OAuth
flow, use these functions to:
- get the currently set user's access token from the upapi.credentials object
- set the current user's access token (and in turn the upapi.credentials object)
"""


def get_access_token():
    """
    Convert the current Credentials object into an access token.

    :return: the access token
    """
    if credentials is None:
        raise upapi.exceptions.MissingCredentials('No credentials to convert into a token.')
    return credentials.token_response


def set_access_token(access_token):
    """
    Convert the token to a credentials object and set it.

    :param access_token: access token
    """
    global credentials
    credentials = up().token_to_creds(access_token)


"""
The following functions are meant to help automate the OAuth flow.
1. Send the user to the value of get_redirect_url()
2. Have your callback handler call get_token() with it's URL

When the token expires call refresh_token().

When the user wants to be removed from your app, call disconnect().
"""


def get_redirect_url():
    """
    Get the URL to redirect new users to where they grant access to your application.

    :return: your app-specific URL
    """
    return up().get_redirect_url()


def get_token(callback_url):
    """
    Retrieve the OAuth token from the server based on the authorization code in the callback_url.
    This function returns the access token, and it sets the upapi.credentials object.

    :param callback_url: the URL on your server that Jawbone sent the user back to
    :return: a dictionary containing the token
    """
    global credentials
    my_up = up()
    token = my_up.get_up_token(callback_url)
    credentials = my_up.credentials
    return token


def refresh_token():
    """
    Manually refresh your OAuth token.

    :return: the new token
    """
    global credentials
    my_up = up()
    token = my_up.refresh_token()
    credentials = my_up.credentials
    return token


def disconnect():
    """
    Revoke API access for this user.
    """
    up().disconnect()
    global credentials
    credentials = None


"""
The following functions are helpers for accessing upapi objects (i.e., API resources).
"""


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
        credentials_storage=credentials_storage,
        user_credentials=credentials)
