"""
All the API objects inherit from UpApi.
"""
import datetime
import httplib
import httplib2
import json
import oauth2client.client
import upapi.endpoints
import upapi.exceptions
import upapi.scopes
import urlparse


"""
Setting a specific User-Agent for analytics purposes.
"""
SDK_VERSION = '0.4'
USERAGENT = 'upapi/{} (https://developer.jawbone.com)'.format(SDK_VERSION)


class UpApi(object):
    """
    The UpApi manages the OAuth connection to the Jawbone UP API. All UP API resources are subclasses of UpApi.
    """
    def __init__(
            self,
            app_id,
            app_secret,
            app_redirect_uri,
            app_scope=None,
            credentials_saver=None,
            user_credentials=None,
            token_saver=None,
            user_token=None):
        """
        Create an UpApi object to manage the OAuth connection.

        :param app_id: Client ID from UP developer portal
        :param app_secret: App Secret from UP developer portal
        :param app_redirect_uri: one of your OAuth redirect URLs
        :param app_scope: list of permissions a user will have to approve (see upapi.scopes). Defaults to
            upapi.scopes.BASIC_READ
        :param credentials_saver: function to call to save a user's credentials when they get updated. This function
            should take an oauth2client.client.OAuth2Credentials object.
        :param user_credentials: oauth2client.client.OAuth2Credentials object from a previously OAuth'd user. This will
            override any value passed in for user_token. If neither user_token or user_credentials are passed in, then
            the app must send the user through the OAuth flow and call the get_up_token method to retrieve the token
            and credentials.
        :param token_saver: function to call to save a user's token dict when it gets updated. This function should take
            a single argument, the dict returned from the UP API.
        :param user_token: the dict containing access and refresh tokens returned from the UP API. This will only be
            used if you do not pass in user_credentials.
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self._redirect_uri = app_redirect_uri

        #
        # Default scope to BASIC_READ. The API itself will do this, but the OAuth2Client library complains if scope is
        # None.
        #
        if app_scope is None:
            self.app_scope = upapi.scopes.BASIC_READ
        else:
            self.app_scope = app_scope

        self.credentials_saver = credentials_saver
        self._credentials = user_credentials
        self.token_saver = token_saver

        #
        # Make sure token and credentials match
        #
        if (self._credentials is None) and (user_token is not None):
            self._credentials = self.token_to_creds(user_token)

        #
        # Initialize the OAuth objects.
        #
        self.flow = None
        self._refresh_flow()
        self.http = None
        self._refresh_http()

        super(UpApi, self).__init__()

    def token_to_creds(self, token):
        """
        Convert a token dictionary to an oauth2client.client.OAuth2Credentials object.

        :param token: the token dict returned from the UP API
        :return: the OAuth2Credentials object
        """
        return oauth2client.client.OAuth2Credentials(
            token['access_token'],
            self.app_id,
            self.app_secret,
            token['refresh_token'],
            datetime.datetime.now() + datetime.timedelta(seconds=token['expires_in']),
            upapi.endpoints.TOKEN,
            USERAGENT,
            token_response=token,
            scopes=self.app_scope)

    def _refresh_flow(self):
        """
        Get a new flow object--called automatically when creating the object or updating the redirect URI.
        """
        self.flow = oauth2client.client.OAuth2WebServerFlow(
            self.app_id,
            client_secret=self.app_secret,
            scope=self.app_scope,
            redirect_uri=self.redirect_uri,
            user_agent=USERAGENT,
            auth_uri=upapi.endpoints.AUTH,
            token_uri=upapi.endpoints.TOKEN)

    def _refresh_http(self):
        """
        Get new http object--called automatically when creating the object or updating the credentials/token.
        """
        if self.credentials is None:
            self.http = None
        else:
            self.http = self.credentials.authorize(httplib2.Http())

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
        self._refresh_flow()

    @property
    def credentials(self):
        """
        The OAuth2Credentials object from a successful OAuth flow

        :return: the OAuth2Credentials object
        """
        return self._credentials

    @credentials.setter
    def credentials(self, new_creds):
        """
        Update the credentials and refresh the oauth objects.

        :param new_creds: new OAuth2Credentials object
        """
        self._credentials = new_creds
        self._refresh_http()

    @property
    def token(self):
        """
        The token from the OAuth handshake

        :return: the token
        """
        if self._credentials is None:
            return None
        else:
            return self._credentials.token_response

    @token.setter
    def token(self, new_token):
        """
        Update the token and the oauth object.

        :param new_token: new token value
        """
        self.credentials = self.token_to_creds(new_token)

    def get_redirect_url(self):
        """
        Get the OAuth login redirect URL for this app.

        :return: the OAuth login redirect URL
        """
        return self.flow.step1_get_authorize_url()

    def call_savers(self):
        """
        If credential or token savers exist, call them.
        """
        if self.credentials_saver is not None:
            self.credentials_saver(self.credentials)
        if self.token_saver is not None:
            self.token_saver(self.token)

    def get_up_token(self, callback_url):
        """
        Retrieve a token after the user has logged in and approved your app (i.e., second half of the OAuth handshake).
        Set the token in the object, and call the savers.

        :param callback_url: The full URL on your server that Jawbone sent the user back to
        """
        #
        # Parse the code parameter out of the URL.
        #
        code = urlparse.parse_qs(urlparse.urlparse(callback_url).query)['code'][0]
        self.credentials = self.flow.step2_exchange(code)
        self.call_savers()
        return self.token

    def refresh_token(self):
        """
        Refresh the current OAuth token.
        """
        #
        # Need a fresh Http object because we cannot pass the existing access token to the refresh endpoint, and then
        # we need to refresh the Http object with the new credentials.
        #
        self.credentials.refresh(httplib2.Http())
        self._refresh_http()
        self.call_savers()
        return self.token

    def _raise_for_status(self, ok_statuses):
        """
        Check the API response status and throw an exception if necessary.

        :param ok_statuses: list of acceptable response codes
        """
        if self.resp.status not in ok_statuses:
            raise upapi.exceptions.UnexpectedAPIResponse('{} {}'.format(self.resp.status, self.content))

    def _request(self, url, method='GET'):
        """
        Issue an HTTP request using the authorized Http object, handle bad responses, set the Meta object from the
        response content, and return the data as JSON.

        :param url: endpoint to send the request
        :param method: HTTP method (e.g. GET, POST, etc.), defaults to GET
        :return: JSON data
        """
        self.resp, self.content = self.http.request(url, method)
        self._raise_for_status([httplib.OK])
        resp_json = json.loads(self.content)
        self.meta = upapi.meta.Meta(**resp_json['meta'])
        return resp_json['data']

    def get(self, url):
        """
        Send a GET request to URL.

        :param url: endpoint to send the GET
        :return: JSON data
        """
        return self._request(url)

    def delete(self, url):
        """
        Send a DELETE request to URL.

        :param url: endpoint to send the DELETE
        :return: JSON data
        """
        return self._request(url, method='DELETE')

    def disconnect(self):
        """
        Revoke access for this user.
        """
        self.delete(upapi.endpoints.DISCONNECT)
        self.credentials = None
        self.call_savers()

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
