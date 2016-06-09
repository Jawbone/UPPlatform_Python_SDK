"""
Unit tests for upapi.__init__
"""
import httplib
import mock
import requests.exceptions
import unittest
import upapi
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

    def __init__(self, status_code):
        self.status_code = status_code
        self.text = 'FakeResponse'

    def raise_for_status(self):
        """
        Fake the behavior by raising for any 40x/50x
        """
        if 400 <= self.status_code < 600:
            raise requests.exceptions.HTTPError


class TestUpApi(unittest.TestCase):
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
        self.assertEqual(self.up._tokens, upapi.tokens)

        #
        # Override properties
        #
        app_id = 'app_id'
        app_secret = 'app_secret'
        app_redirect_uri = 'app_redirect_uri'
        app_scope = [upapi.scopes.FRIENDS_READ]
        app_token_saver = token_saver
        app_tokens = 'app_tokens'
        self.up = upapi.UpApi(
            app_id=app_id,
            app_secret=app_secret,
            app_redirect_uri=app_redirect_uri,
            app_scope=app_scope,
            app_token_saver=app_token_saver,
            app_tokens=app_tokens)
        self.assertEqual(self.up.app_id, app_id)
        self.assertEqual(self.up.app_secret, app_secret)
        self.assertEqual(self.up._redirect_uri, app_redirect_uri)
        self.assertEqual(self.up.app_scope, app_scope)
        self.assertEqual(self.up.app_token_saver, app_token_saver)
        self.assertEqual(self.up._tokens, app_tokens)

    @mock.patch('upapi.requests_oauthlib.OAuth2Session', autospec=True)
    def test__refresh_oauth(self, mock_oauth):
        """
        Verify that the OAuth2Session's auto refresh is set correctly when instantiating a new oauth object.

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
            token=upapi.tokens)

        #
        # Token saver -> auto refresh
        #
        upapi.token_saver = token_saver
        upapi.UpApi()
        mock_oauth.assert_called_with(
            client_id=upapi.client_id,
            redirect_uri=upapi.redirect_uri,
            scope=upapi.scope,
            token=upapi.tokens,
            auto_refresh_url='https://jawbone.com/auth/oauth2/token',
            auto_refresh_kwargs={'client_id': upapi.client_id, 'client_secret': upapi.client_secret},
            token_updater=upapi.token_saver)

    def test_redirect_uri(self):
        """
        Verify setting redirect uri updates the UpApi and oauth objects.
        """
        default_oauth = self.up.oauth
        url = 'https://override.com'
        self.up.redirect_uri = url
        self.assertEqual(self.up.redirect_uri, url)
        self.assertIsNot(self.up.oauth, default_oauth)

    def test_tokens(self):
        """
        Verify setting tokens updates the UpApi and oauth objects.
        """
        default_oauth = self.up.oauth
        tokens = {'access_token': 'foo'}
        self.up.tokens = tokens
        self.assertEqual(self.up.tokens, tokens)
        self.assertIsNot(self.up.oauth, default_oauth)

    @mock.patch('upapi.requests_oauthlib.OAuth2Session.refresh_token')
    def test_refresh_tokens(self, mock_refresh):
        """
        Verify the requests_oauthlib call to refresh the tokens  and that it updates the UpApi object.

        :param mock_refresh:
        :return:
        """
        ret_tokens = {'access_token': 'refreshed_access'}
        mock_refresh.return_value = ret_tokens
        self.up.refresh_tokens()
        mock_refresh.assert_called_with(
            'https://jawbone.com/auth/oauth2/token',
            client_id=upapi.client_id,
            client_secret=upapi.client_secret)
        self.assertEqual(self.up.tokens, ret_tokens)

    @mock.patch('upapi.requests_oauthlib.OAuth2Session.delete', autospec=True)
    def test_disconnect(self, mock_delete):
        """
        Verify that a disconnect sets the tokens and oauth to None.

        :param mock_delete: mock OAuth lib function
        """
        #
        # 404 should raise from the library
        #
        mock_delete.return_value = FakeResponse(httplib.NOT_FOUND)
        self.assertRaises(requests.exceptions.HTTPError, self.up.disconnect)

        #
        # Non-200 and Non-40x/50x should raise from the SDK.
        #
        mock_delete.return_value = FakeResponse(httplib.SEE_OTHER)
        self.assertRaises(upapi.UnexpectedAPIResponse, self.up.disconnect)

        #
        # Successful disconnect should clear the tokens
        #
        mock_delete.return_value = FakeResponse(httplib.OK)
        self.up.disconnect()
        self.assertIsNone(self.up._tokens)
        self.assertIsNone(self.up.oauth)


class TestGetTokens(unittest.TestCase):
    @mock.patch('upapi.requests_oauthlib.OAuth2Session.fetch_token', autospec=True)
    def test_get_tokens(self, mock_fetch_token):
        """
        Verify that global tokens get set correctly when we retrieve tokens from the API.

        :param mock_fetch_token: mock OAuth lib function
        """
        upapi.client_id = 'client_id'
        upapi.client_secret = 'client_secret'
        upapi.redirect_uri = 'redirect_uri'
        upapi.scope = [upapi.scopes.EXTENDED_READ, upapi.scopes.MOVE_READ]

        #
        # No tokens because we haven't set them.
        #
        self.assertIsNone(upapi.tokens)

        #
        # Mock the tokens
        #
        mock_fetch_token.return_value = {
            'access_token': 'mock_token',
            'token_type': 'Bearer',
            'expires_in': 31536000,
            'refresh_token': 'mock_refresh',
            'expires_at': 1496509667.275609}
        upapi.get_tokens('https://localhost/foo')

        #
        # Global tokens should be set and UpApi should pick them up
        #
        self.assertIsNotNone(upapi.tokens)
        self.assertEqual(upapi.UpApi().tokens, upapi.tokens)


class TestRefreshTokens(unittest.TestCase):
    @mock.patch('upapi.requests_oauthlib.OAuth2Session.refresh_token', autospec=True)
    def test_refresh_tokens(self, mock_refresh):
        """
        Verify that global tokens get set correctly when we retrieve tokens from the API.

        :param mock_refresh: mock OAuth lib function
        """
        ret_tokens = {'access_token': 'refreshed_access'}
        mock_refresh.return_value = ret_tokens
        upapi.refresh_tokens()
        self.assertEqual(upapi.tokens, ret_tokens)


class TestDisconnect(unittest.TestCase):
    @mock.patch('upapi.requests_oauthlib.OAuth2Session.delete', autospec=True)
    def test_disconnect(self, mock_delete):
        """
        Verify that a disconnect makes the global tokens None.

        :param mock_delete: mock OAuth lib function
        """
        upapi.tokens = {'access_token': 'access_token'}
        mock_delete.return_value = FakeResponse(httplib.OK)
        upapi.disconnect()
        self.assertIsNone(upapi.tokens)
