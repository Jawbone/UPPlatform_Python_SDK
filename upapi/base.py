"""
All the API objects inherit from UpApi.
"""
import httplib
import requests_oauthlib
import upapi.endpoints
import upapi.exceptions


"""
Setting a specific User-Agent for analytics purposes.
"""
SDK_VERSION = '0.2'
USERAGENT = 'upapi/{} (https://developer.jawbone.com)'.format(SDK_VERSION)


class UpApi(object):
    """
    The UpApi manages the OAuth connection to the Jawbone UP API. All UP API resources are subclasses of UpApi.
    """
    def __init__(self, app_id, app_secret, app_redirect_uri=None, app_scope=None, app_token_saver=None, app_token=None):
        """
        Create an UpApi object to manage the OAuth connection.

        :param app_id: Client ID from UP developer portal
        :param app_secret: App Secret from UP developer portal
        :param app_redirect_uri: one of your OAuth redirect URLs. If this is not provided, the object cannot auth a new
            user.
        :param app_scope: list of permissions a user will have to approve
        :param app_token_saver: method to call to save token on refresh. If this is not provied, the object will not
            automatically save tokens.
        :param app_token: token from a previously OAuth'd user. If this is not provided, the object must first auth a
            new user.
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self._redirect_uri = app_redirect_uri
        self.app_scope = app_scope
        self.app_token_saver = app_token_saver
        self._token = app_token

        #
        # Initialize the OAuth object.
        #
        self.oauth = None
        self._refresh_oauth()

        super(UpApi, self).__init__()

    def _refresh_oauth(self):
        """
        Get a new OAuth object. This gets called automatically when you
        1. create the object
        2. update the user's token
        3. update the redirect_uri
        """
        if self.app_token_saver is None:
            refresh_kwargs = {}
        else:
            #
            # Required args to auto-refresh tokens
            #
            refresh_kwargs = {
                'auto_refresh_url': upapi.endpoints.TOKEN,
                'auto_refresh_kwargs': {'client_id': self.app_id, 'client_secret': self.app_secret},
                'token_updater': self.app_token_saver}

        self.oauth = requests_oauthlib.OAuth2Session(
            client_id=self.app_id,
            scope=self.app_scope,
            redirect_uri=self._redirect_uri,
            token=self.token,
            **refresh_kwargs)
        self.oauth.headers['User-Agent'] = '{} {}'.format(USERAGENT, self.oauth.headers['User-Agent'])

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
    def token(self):
        """
        The token from the OAuth handshake

        :return: the token
        """
        return self._token

    @token.setter
    def token(self, new_token):
        """
        Update the token and the oauth object.

        :param new_token: new token value
        """
        self._token = new_token
        self._refresh_oauth()

    def get_up_token(self, callback_url):
        """
        Retrieve a token after the user has logged in and approved your app (i.e., second half of the OAuth handshake).

        :param callback_url: The full URL on your server that Jawbone sent the user back to
        :return: the token from the UP API
        """
        self._token = self.oauth.fetch_token(
            upapi.endpoints.TOKEN,
            authorization_response=callback_url,
            client_secret=self.app_secret)

        #
        # New token, so call the token_saver if one is defined.
        #
        if self.app_token_saver is not None:
            self.app_token_saver(self._token)

        return self._token

    def refresh_token(self):
        """
        Refresh the current OAuth token.
        """
        self._token = self.oauth.refresh_token(
            upapi.endpoints.TOKEN,
            client_id=self.app_id,
            client_secret=self.app_secret)

        #
        # Token saver is set, so call it even on a manual refresh.
        #
        if self.app_token_saver is not None:
            self.app_token_saver(self._token)

        return self._token

    def _raise_for_status(self, ok_statuses):
        """
        Check the API response status and throw an exception if necessary.

        :param ok_statuses: list of acceptable response codes
        """
        if self.response.status_code not in ok_statuses:
            self.response.raise_for_status()
            raise upapi.exceptions.UnexpectedAPIResponse('{} {}'.format(self.response.status_code, self.response.text))

    def _request(self, method, url):
        """
        Issue an HTTP request using the OAuth token, handle bad responses, set the Meta object for the request, and
        return the data as JSON.

        :param method: HTTP method (e.g. self.oauth.get)
        :param url: endpoint to send the request
        :return: JSON data
        """
        self.response = method(url)
        self._raise_for_status([httplib.OK])
        resp_json = self.response.json()
        self.meta = upapi.meta.Meta(**resp_json['meta'])
        return resp_json['data']

    def get(self, url):
        """
        Send a GET request to URL.

        :param url: endpoint to send the GET
        :return: JSON data
        """
        return self._request(self.oauth.get, url)

    def delete(self, url):
        """
        Send a DELETE request to URL.

        :param url: endpoint to send the DELETE
        :return: JSON data
        """
        return self._request(self.oauth.delete, url)

    def disconnect(self):
        """
        Revoke access for this user.
        """
        self.delete(upapi.endpoints.DISCONNECT)
        self._token = None
        self.oauth = None

        #
        # If there is a token_saver call it with None for the token.
        #
        if self.app_token_saver is not None:
            self.app_token_saver(None)

    #
    # TODO: finish pubsub implementation.
    #
    # def set_pubsub(self, url):
    #     """
    #     Register a user-specific pubsub webhook.
    #
    #     :param url: user-specific webhook callback URL
    #     """
    #     resp = self.oauth.post(upapi.endpoints.PUBSUB, data={'webhook': url})
    #     self._raise_for_status([httplib.OK], resp)
    #
    # def delete_pubsub(self):
    #     """
    #     Delete a user-specific pubsub webhook.
    #     """
    #     self.delete(upapi.endpoints.PUBSUB)
