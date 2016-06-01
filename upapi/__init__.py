"""
This is the Python SDK for the Jawbone UP API.

For API details: https://jawbone.com/up/developer
For SDK details: https://github.com/Jawbone/UPPlatform_Python_SDK
"""
import requests_oauthlib

"""
Set these variables with the values for your app from https://jawbone.com/up/developer

Example:
import upapi
upapi.client_id = ...

If you have multiple redirect URLs, leave this as None and specify the redirect_uri in your API calls.
"""
client_id = None
client_secret = None
redirect_uri = None
scope = None


def get_redirect_url(app_url=None):
    """
    Get the URL to redirect new users to allow your access to your application.

    :param app_url: override any globally set redirect_uri
    :return: your app-specific URL
    """
    if app_url is None:
        app_url = redirect_uri
    oauth = requests_oauthlib.OAuth2Session(client_id=client_id, redirect_uri=app_url, scope=scope)
    authorization_url, state = oauth.authorization_url('https://jawbone.com/auth/oauth2/auth')
    return authorization_url

