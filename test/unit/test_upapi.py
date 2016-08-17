"""
Unit tests for upapi.__init__
"""
import mock
import unittest
import upapi
import upapi.endpoints
import upapi.scopes


class TestUp(unittest.TestCase):

    @mock.patch('upapi.base.UpApi', autospec=True)
    def test_up(self, mock_upapi):
        """
        Verify override_url gets passed correctly.

        :param mock_upapi: mocked UpApi object
        :return:
        """
        #
        # No override URL
        #
        upapi.up()
        mock_upapi.assert_called_with(
            upapi.client_id,
            upapi.client_secret,
            app_redirect_uri=upapi.redirect_uri,
            app_scope=upapi.scope,
            app_token_saver=upapi.token_saver,
            app_token=upapi.token)


class TestGetToken(unittest.TestCase):

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
        token = {'access_token': 'access_token'}
        mock_get_token.return_value = token
        upapi.get_token('https://callback.url')
        self.assertEqual(upapi.token, token)


class TestRefreshToken(unittest.TestCase):

    @mock.patch('upapi.base.UpApi.refresh_token', autospec=True)
    def test_refresh_token(self, mock_refresh):
        """
        Verify that global token gets set correctly when we refresh.

        :param mock_refresh: mock UpApi method
        """
        upapi.token = {'access_token': 'access_token'}
        refreshed_token = {'access_token': 'refreshed_token'}
        mock_refresh.return_value = refreshed_token
        upapi.refresh_token()
        self.assertEqual(upapi.token, refreshed_token)


class TestDisconnect(unittest.TestCase):

    @mock.patch('upapi.base.UpApi.disconnect', autospec=True)
    def test_disconnect(self, mock_disconnect):
        """
        Verify that a disconnect makes the global token None.

        :param mock_disconnect: mock UpApi method
        """
        upapi.token = {'access_token': 'access_token'}
        upapi.disconnect()
        self.assertIsNone(upapi.token)


class TestGetUser(unittest.TestCase):

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
            app_redirect_uri=upapi.redirect_uri,
            app_scope=upapi.scope,
            app_token_saver=upapi.token_saver,
            app_token=upapi.token)
