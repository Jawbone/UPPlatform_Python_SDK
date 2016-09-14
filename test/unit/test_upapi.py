"""
Unit tests for upapi.__init__
"""
import mock
import test.unit
import unittest
import upapi
import upapi.endpoints
import upapi.scopes


class TestUp(test.unit.TestSDK):

    @mock.patch('upapi.base.UpApi', autospec=True)
    def test_up(self, mock_upapi):
        """
        Verify UpApi object creation.

        :param mock_upapi: mocked UpApi object
        """
        #
        # No override URL
        #
        upapi.up()
        mock_upapi.assert_called_with(
            upapi.client_id,
            upapi.client_secret,
            upapi.redirect_uri,
            app_scope=upapi.scope,
            credentials_saver = upapi.credentials_saver,
            user_credentials = upapi.credentials,
            token_saver=upapi.token_saver,
            user_token=upapi.token)


class TestGetRedirectUrl(test.unit.TestSDK):

    @mock.patch('upapi.base.UpApi.get_redirect_url', autospec=True)
    def test_get_redirect_url(self, mock_redirect):
        """
        Verify redirect URL gets generated correctly.

        :param mock_redirect: mocked UpApi method
        """
        upapi.get_redirect_url()
        self.assertTrue(mock_redirect.called)


class TestGetToken(test.unit.TestSDK):

    @mock.patch('upapi.base.UpApi.get_up_token', autospec=True)
    def test_get_token(self, mock_get_token):
        """
        Verify that global token gets set.

        :param mock_get_token: mock UpApi method
        """
        #
        # Token not set yet.
        #
        self.assertIsNone(upapi.token)

        #
        # Set the token
        #
        mock_get_token.return_value = self.token
        upapi.get_token('https://callback.url')
        self.assertEqual(upapi.token, self.token)


class TestRefreshToken(test.unit.TestSDK):

    @mock.patch('upapi.base.UpApi.refresh_token', autospec=True)
    def test_refresh_token(self, mock_refresh):
        """
        Verify that global token gets set correctly when we refresh.

        :param mock_refresh: mock UpApi method
        """
        upapi.token = self.token
        refreshed_token = {'access_token': 'refreshed_token'}
        mock_refresh.return_value = refreshed_token
        upapi.refresh_token()
        self.assertEqual(upapi.token, refreshed_token)


class TestDisconnect(test.unit.TestSDK):

    @mock.patch('upapi.base.UpApi.disconnect', autospec=True)
    def test_disconnect(self, mock_disconnect):
        """
        Verify that a disconnect makes the global token None.

        :param mock_disconnect: mock UpApi method
        """
        upapi.token = self.token
        upapi.disconnect()
        self.assertIsNone(upapi.token)


class TestGetUser(test.unit.TestSDK):

    @mock.patch('upapi.user.User', autospec=True)
    def test_get_user(self, mock_user):
        """
        Verify User object gets greated with global values.

        :param mock_user: mocked User object
        """
        upapi.get_user()
        mock_user.assert_called_with(
            upapi.client_id,
            upapi.client_secret,
            upapi.redirect_uri,
            app_scope=upapi.scope,
            credentials_saver=upapi.credentials_saver,
            user_credentials=upapi.credentials,
            token_saver=upapi.token_saver,
            user_token=upapi.token)
