"""
Unit tests for upapi.__init__
"""
import mock
import unittest
import upapi


def token_saver(_):
    """
    Stub of a token saver method

    :param _: the new token
    """
    pass


class TestUpApi(unittest.TestCase):
    def setUp(self):
        """
        Create the UpApi object.
        """
        upapi.client_id = 'client_id'
        upapi.client_secret = 'client_secret'
        upapi.redirect_uri = 'redirect_uri'
        upapi.scope = [upapi.SCOPES.EXTENDED_READ, upapi.SCOPES.MOVE_READ]
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
        app_scope = [upapi.SCOPES.FRIENDS_READ]
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
        tokens = {'token': 'foo'}
        self.up.tokens = tokens
        self.assertEqual(self.up.tokens, tokens)
        self.assertIsNot(self.up.oauth, default_oauth)


class TestGetTokens(unittest.TestCase):
    @mock.patch('upapi.requests_oauthlib.OAuth2Session.fetch_token', autospec=True)
    def test_get_tokens(self, mock_fetch_tokens):
        upapi.client_id = 'client_id'
        upapi.client_secret = 'client_secret'
        upapi.redirect_uri = 'redirect_uri'
        upapi.scope = [upapi.SCOPES.EXTENDED_READ, upapi.SCOPES.MOVE_READ]

        #
        # No tokens because we haven't set them.
        #
        self.assertIsNone(upapi.tokens)

        #
        # Mock the tokens
        #
        mock_fetch_tokens.return_value = {
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
