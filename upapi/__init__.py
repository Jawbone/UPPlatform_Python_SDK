"""
This is the Python SDK for the Jawbone UP API.

For API details: https://jawbone.com/up/developer
For SDK details: https://github.com/Jawbone/UPPlatform_Python_SDK
"""
import requests_oauthlib

"""
Set these variables with the values for your app from https://jawbone.com/up/developer

If you have multiple redirect URLs, you can override this redirect_uri in your API calls.

If you do not specify a token_saver, upapi will not automatically refresh expired tokens.
"""
client_id = None
client_secret = None
redirect_uri = None
scope = None
token_saver = None
tokens = None


class SCOPES(object):
    """
    Refer to https://nudgestage.jawbone.com/up/developer/authentication for a definition of these scopes.
    """
    BASIC_READ = 'basic_read'
    EXTENDED_READ = 'extended_read'
    LOCATION_READ = 'location_read'
    FRIENDS_READ = 'friends_read'
    MOOD_READ = 'mood_read'
    MOOD_WRITE = 'mood_write'
    MOVE_READ = 'move_read'
    MOVE_WRITE = 'move_write'
    SLEEP_READ = 'sleep_read'
    SLEEP_WRITE = 'sleep_write'
    MEAL_READ = 'meal_read'
    MEAL_WRITE = 'meal_write'
    WEIGHT_READ = 'weight_read'
    WEIGHT_WRITE = 'weight_write'
    GENERIC_EVENT_READ = 'generic_event_read'
    GENERIC_EVENT_WRITE = 'generic_event_write'
    HEARTRATE_READ = 'heartrate_read'


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
up.
    :param callback_url: The URL on your server that Jawbone sent the user back to
    :return: a dictionary containing the tokens
    """
    global tokens
    tokens = UpApi().get_up_tokens(callback_url)
    return tokens


def get_refresh_token():
    """
    Retrieve the OAuth refresh token if you want to refresh manually.

    :return: the refresh token
    """
    return UpApi().refresh_token


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
            app_token_saver=None,
            app_tokens=None):
        """
        Create an UpApi object to manage the OAuth connection.

        :param app_id: Client ID from UP developer portal
        :param app_secret: App Secret from UP developer portal
        :param app_redirect_uri: one of your OAuth redirect URLs
        :param app_scope: list of permissions a user will have to approve
        :param app_token_saver: method to call to save token on refresh
        :param app_tokens: tokens from a previously OAuth'd user
        """
        self.oauth = None

        #
        # Use the module scope to default any unpassed args
        #
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
        if app_token_saver is None:
            self.app_token_saver = token_saver
        else:
            self.app_token_saver = app_token_saver
        if app_tokens is None:
            self._tokens = tokens
        else:
            self._tokens = app_tokens

        self._refresh_oauth()
        super(UpApi, self).__init__()

    def _refresh_oauth(self):
        """
        Get a new OAuth object. This gets called automatically when you
        1. create the object
        2. update the user's tokens
        3. update the redirect_uri
        """
        if self.app_token_saver is None:
            refresh_kwargs = {}
        else:
            refresh_kwargs = {
                'auto_refresh_url': 'https://jawbone.com/auth/oauth2/token',
                'auto_refresh_kwargs': {'client_id': self.app_id, 'client_secret': self.app_secret},
                'token_updater': self.app_token_saver}

        self.oauth = requests_oauthlib.OAuth2Session(
            client_id=self.app_id,
            scope=self.app_scope,
            redirect_uri=self._redirect_uri,
            token=self.tokens,
            **refresh_kwargs)

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
    def tokens(self, new_tokens):
        self._tokens = new_tokens
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

    @property
    def refresh_token(self):
        """
        Get the OAuth refresh token.

        :return: the refresh token
        """
        return self._tokens['refresh_token']
