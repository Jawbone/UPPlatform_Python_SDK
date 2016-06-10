"""
Unit tests for upapi.__init__
"""
import httplib
import mock
import requests.exceptions
import requests.utils
import unittest
import upapi
import upapi.endpoints
import upapi.scopes


def token_saver(_):
    """
    Stub of a token saver method

    :param _: the new token
    """
    pass


class FakeResponse(object):
    """
    Fake ResponseObject for mocking requests_oauthlib.
    """

    def __init__(self, status_code, raise_for_status=None):
        """
        Fakes requests.Response

        :param status_code: HTTP status code of the response
        :param raise_for_status: use this to mock the Response object's 40x/50x exception behavior
        """
        self.status_code = status_code
        self.text = 'FakeResponse'
        if raise_for_status is not None:
            self.raise_for_status = raise_for_status


class TestUpApi(unittest.TestCase):
    """
    Unit tests for the UpApi object
    """
    def setUp(self):
        """
        Create the UpApi object.
        """
        upapi.client_id = 'client_id'
        upapi.client_secret = 'client_secret'
        upapi.redirect_uri = 'redirect_uri'
        upapi.scope = [upapi.scopes.EXTENDED_READ, upapi.scopes.MOVE_READ]
        self.up = upapi.UpApi()
        super(TestUpApi, self).setUp()

    def test___init__(self):
        """
        Verify defaulting of __init__ params
        """
        self.assertEqual(self.up.app_id, upapi.client_id)
        self.assertEqual(self.up.app_secret, upapi.client_secret)
        self.assertEqual(self.up._redirect_uri, upapi.redirect_uri)
        self.assertEqual(self.up.app_scope, upapi.scope)
        self.assertEqual(self.up.app_token_saver, upapi.token_saver)
        self.assertEqual(self.up._token, upapi.token)

        #
        # Override properties
        #
        app_id = 'app_id'
        app_secret = 'app_secret'
        app_redirect_uri = 'app_redirect_uri'
        app_scope = [upapi.scopes.FRIENDS_READ]
        app_token_saver = token_saver
        app_token = 'app_token'
        self.up = upapi.UpApi(
            app_id=app_id,
            app_secret=app_secret,
            app_redirect_uri=app_redirect_uri,
            app_scope=app_scope,
            app_token_saver=app_token_saver,
            app_token=app_token)
        self.assertEqual(self.up.app_id, app_id)
        self.assertEqual(self.up.app_secret, app_secret)
        self.assertEqual(self.up._redirect_uri, app_redirect_uri)
        self.assertEqual(self.up.app_scope, app_scope)
        self.assertEqual(self.up.app_token_saver, app_token_saver)
        self.assertEqual(self.up._token, app_token)

    @mock.patch('upapi.requests_oauthlib.OAuth2Session')
    def test__refresh_oauth(self, mock_oauth):
        """
        Verify that the OAuth2Session's auto refresh is set correctly when instantiating a new oauth object.
        Additionally, check that the User-Agent is set correctly.

        :param mock_oauth: mocked OAuth2Session
        """
        #
        # No token saver -> no auto refresh
        #
        upapi.UpApi()
        mock_oauth.assert_called_with(
            client_id=upapi.client_id,
            redirect_uri=upapi.redirect_uri,
            scope=upapi.scope,
            token=upapi.token)
        self.assertTrue(self.up.oauth.headers['User-Agent'].startswith(upapi.USERAGENT))

        #
        # Token saver -> auto refresh
        #
        upapi.token_saver = token_saver
        upapi.UpApi()
        mock_oauth.assert_called_with(
            client_id=upapi.client_id,
            redirect_uri=upapi.redirect_uri,
            scope=upapi.scope,
            token=upapi.token,
            auto_refresh_url=upapi.endpoints.TOKEN,
            auto_refresh_kwargs={'client_id': upapi.client_id, 'client_secret': upapi.client_secret},
            token_updater=upapi.token_saver)
        self.assertTrue(self.up.oauth.headers['User-Agent'].startswith(upapi.USERAGENT))

    def test_redirect_uri(self):
        """
        Verify setting redirect uri updates the UpApi and oauth objects.
        """
        default_oauth = self.up.oauth
        url = 'https://override.com'
        self.up.redirect_uri = url
        self.assertEqual(self.up.redirect_uri, url)
        self.assertIsNot(self.up.oauth, default_oauth)

    def test_token(self):
        """
        Verify setting token updates the UpApi and oauth objects.
        """
        default_oauth = self.up.oauth
        token = {'access_token': 'foo'}
        self.up.token = token
        self.assertEqual(self.up.token, token)
        self.assertIsNot(self.up.oauth, default_oauth)

    @mock.patch('upapi.requests_oauthlib.OAuth2Session.refresh_token')
    def test_refresh_token(self, mock_refresh):
        """
        Verify the requests_oauthlib call to refresh the token and that it updates the UpApi object.

        :param mock_refresh: mocked requests_oauthlib token refresh method
        """
        ret_token = {'access_token': 'refreshed_access'}
        mock_refresh.return_value = ret_token
        self.up.refresh_token()
        mock_refresh.assert_called_with(
            upapi.endpoints.TOKEN,
            client_id=upapi.client_id,
            client_secret=upapi.client_secret)
        self.assertEqual(self.up.token, ret_token)

    @mock.patch('upapi.requests_oauthlib.OAuth2Session.delete', autospec=True)
    @mock.patch('upapi.requests_oauthlib.requests.Response.raise_for_status')
    def test_disconnect(self, mock_raise, mock_delete):
        """
        Verify that a disconnect sets the token and oauth to None, or raises the correct Exceptions.

        :param mock_raise: mock OAuth lib Response function
        :param mock_delete: mock OAuth lib function
        """
        #
        # 404 should raise from the library
        #
        mock_raise.side_effect = requests.exceptions.HTTPError
        mock_delete.return_value = FakeResponse(httplib.NOT_FOUND, raise_for_status=mock_raise)
        self.assertRaises(requests.exceptions.HTTPError, self.up.disconnect)

        #
        # Non-200 and Non-40x/50x should raise from the SDK.
        #
        mock_raise.side_effect = None
        mock_delete.return_value = FakeResponse(httplib.CREATED, raise_for_status=mock_raise)
        self.assertRaises(upapi.UnexpectedAPIResponse, self.up.disconnect)

        #
        # Successful disconnect should clear the token
        #
        mock_delete.return_value = FakeResponse(httplib.OK)
        self.up.disconnect()
        self.assertIsNone(self.up._token)
        self.assertIsNone(self.up.oauth)


class TestGetToken(unittest.TestCase):
    """
    Unit tests for upapi.get_token
    """
    @mock.patch('upapi.requests_oauthlib.OAuth2Session.fetch_token', autospec=True)
    def test_get_token(self, mock_fetch_token):
        """
        Verify that global token gets set correctly when we retrieve the token from the API.

        :param mock_fetch_token: mock OAuth lib function
        """
        upapi.client_id = 'client_id'
        upapi.client_secret = 'client_secret'
        upapi.redirect_uri = 'redirect_uri'
        upapi.scope = [upapi.scopes.EXTENDED_READ, upapi.scopes.MOVE_READ]

        #
        # No token because we haven't set them.
        #
        self.assertIsNone(upapi.token)

        #
        # Mock the token
        #
        mock_fetch_token.return_value = {
            'access_token': 'mock_token',
            'token_type': 'Bearer',
            'expires_in': 31536000,
            'refresh_token': 'mock_refresh',
            'expires_at': 1496509667.275609}
        upapi.get_token('https://localhost/foo')

        #
        # Global token should be set and UpApi should pick them up
        #
        self.assertIsNotNone(upapi.token)
        self.assertEqual(upapi.UpApi().token, upapi.token)


class TestRefreshToken(unittest.TestCase):
    @mock.patch('upapi.requests_oauthlib.OAuth2Session.refresh_token', autospec=True)
    def test_refresh_token(self, mock_refresh):
        """
        Verify that global token gets set correctly when we retrieve the token from the API.

        :param mock_refresh: mock OAuth lib function
        """
        ret_token = {'access_token': 'refreshed_access'}
        mock_refresh.return_value = ret_token
        upapi.refresh_token()
        self.assertEqual(upapi.token, ret_token)


class TestDisconnect(unittest.TestCase):
    @mock.patch('upapi.requests_oauthlib.OAuth2Session.delete', autospec=True)
    def test_disconnect(self, mock_delete):
        """
        Verify that a disconnect makes the global token None.

        :param mock_delete: mock OAuth lib function
        """
        upapi.token = {'access_token': 'access_token'}
        mock_delete.return_value = FakeResponse(httplib.OK)
        upapi.disconnect()
        self.assertIsNone(upapi.token)
