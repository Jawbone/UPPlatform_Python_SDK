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

If you have multiple redirect URLs, you can override this redirect_uri in your API calls.
"""
client_id = None
client_secret = None
redirect_uri = None
scope = None


def get_redirect_url(override_url=None):
    """
    Get the URL to redirect new users to allow your access to your application.

    :param override_url: override any globally set redirect_uri
    :return: your app-specific URL
    """
    authorization_url, state = UpApi(app_redirect_uri=override_url).oauth.authorization_url(
        'https://jawbone.com/auth/oauth2/auth')
    return authorization_url


def get_tokens(callback_url):
    """
    Retrieve the OAuth tokens from the server based on the authorization code in the callback_url.

    :param callback_url: The URL on your server that Jawbone sent the user back to
    :return: a dictionary containing the tokens
    """
    return UpApi().get_up_tokens(callback_url)


class UpApi(object):
    """
    The UpApi manages the OAuth connection to the Jawbone UP API. All UP API resources are subclasses of UpApi.
    """
    def __init__(
            self,
            app_id=None,
            app_secret=None,
            app_redirect_uri=None,
            app_scope=None,
            tokens=None):
        """
        Create an UpApi object to manage the OAuth connection.

        :param app_id: Client ID from UP developer portal
        :param app_secret: App Secret from UP developer portal
        :param app_redirect_uri: one of your OAuth redirect URLs
        :param app_scope: list of permissions a user will have to approve
        :param tokens: tokens from a previously OAuth'd user
        """
        if app_id is None:
            self.app_id = client_id
        else:
            self.app_id = app_id
        if app_secret is None:
            self.app_secret = client_secret
        else:
            self.app_secret = app_secret
        if app_redirect_uri is None:
            self._redirect_uri = redirect_uri
        else:
            self._redirect_uri = app_redirect_uri
        if app_scope is None:
            self.app_scope = scope
        else:
            self.app_scope = app_scope
        self._tokens = tokens
        self.oauth = None
        self._refresh_oauth()
        super(UpApi, self).__init__()

    def _refresh_oauth(self):
        """
        Get a new OAuth object. This gets called automatically when you
        1. create the object
        2. update the user's tokens
        3. update the redirect_uri
        """
        self.oauth = requests_oauthlib.OAuth2Session(
            client_id=self.app_id,
            scope=self.app_scope,
            redirect_uri=self._redirect_uri,
            token=self.tokens)

    @property
    def redirect_uri(self):
        """
        An app can have multiple redirect_uris, so use this property to differentiate.

        :return: the URI
        """
        return self._redirect_uri

    @redirect_uri.setter
    def redirect_uri(self, url):
        """
        Override the global redirect_uri and create a new oauth object.

        :param url: the specific redirect_url for this connection
        """
        self._redirect_uri = url
        self._refresh_oauth()

    @property
    def tokens(self):
        """
        The tokens from the OAuth handshake

        :return: the tokens
        """
        return self._tokens

    @tokens.setter
    def tokens(self, tokens):
        self._tokens = tokens
        self._refresh_oauth()

    def get_up_tokens(self, callback_url):
        """
        Retrieve a fresh set of tokens after the user has logged in and approved your app (i.e., second half of the
        OAuth handshake).

        :param callback_url: The URL on your server that Jawbone sent the user back to
        :return: the token dictionary from the UP API
        """
        self._tokens = self.oauth.fetch_token(
            'https://jawbone.com/auth/oauth2/token',
            authorization_response=callback_url,
            client_secret=self.app_secret)
        return self._tokens
