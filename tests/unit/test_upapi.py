"""
Unit tests for upapi.__init__
"""
import mock
import tests.unit
import upapi
import upapi.endpoints
import upapi.exceptions
import upapi.scopes


class TestGetAccessToken(tests.unit.TestResource):
    """
    Tests upapi.get_access_token
    """

    def test_get_access_token(self):
        """
        Verify access token getter.
        """
        #
        # No creds, so getter should raise.
        #
        self.assertRaises(upapi.exceptions.MissingCredentials, upapi.get_access_token)

        #
        # Set creds and get the right token
        #
        upapi.credentials = self.credentials
        self.assertEqual(upapi.get_access_token(), self.token)


class TestSetAccessToken(tests.unit.TestSDK):
    """
    Tests upapi.set_access_token
    """

    def test_set_access_token(self):
        """
        Verify the token is set correctly by trying to get it back.
        """
        upapi.set_access_token(self.token)
        self.assertEqual(upapi.get_access_token(), self.token)


class TestUp(tests.unit.TestSDK):
    """
    Tests upapi.up
    """

    @mock.patch('upapi.base.UpApi', autospec=True)
    def test_up(self, mock_upapi):
        """
        Verify UpApi object creation.

        :param mock_upapi: mocked UpApi object
        """
        upapi.up()
        mock_upapi.assert_called_with(
            upapi.client_id,
            upapi.client_secret,
            upapi.redirect_uri,
            app_scope=upapi.scope,
            credentials_storage=upapi.credentials_storage,
            user_credentials=upapi.credentials)


class TestGetRedirectUrl(tests.unit.TestSDK):
    """
    Tests upapi.get_redirect_url
    """

    @mock.patch('upapi.base.UpApi.get_redirect_url', autospec=True)
    def test_get_redirect_url(self, mock_redirect):
        """
        Verify redirect URL gets generated correctly.

        :param mock_redirect: mocked UpApi method
        """
        upapi.get_redirect_url()
        self.assertTrue(mock_redirect.called)


class TestGetToken(tests.unit.TestSDK):
    """
    Tests upapi.get_token
    """

    @mock.patch('upapi.up', autospec=True)
    def test_get_token(self, mock_up):
        """
        Verify that global credentials get set.

        :param mock_up: mock UpApi getter
        """
        #
        # Credentials not set yet.
        #
        self.assertIsNone(upapi.credentials)

        #
        # Set up the mock to return the proper token and credential values
        #
        mock_up.return_value = mock.Mock('upapi.base.UpApi', autospec=True)
        mock_up.return_value.get_up_token = mock.Mock('upapi.base.UpApi.get_up_token', autospec=True)
        mock_up.return_value.get_up_token.return_value = self.token
        mock_up.return_value.credentials = mock.Mock('upapi.base.UpApi.credentials', autospec=True)

        #
        # Set the token and credentials. Then verify.
        #
        callback_url = 'https://callback.url'
        token = upapi.get_token(callback_url)
        mock_up.assert_called_with()
        mock_up.return_value.get_up_token.assert_called_with(callback_url)
        self.assertEqual(token, self.token)
        self.assertEqual(upapi.credentials, mock_up.return_value.credentials)


class TestRefreshToken(tests.unit.TestSDK):
    """
    Tests upapi.refresh_token
    """

    @mock.patch('upapi.up', autospec=True)
    def test_refresh_token(self, mock_up):
        """
        Verify that global credentials get set correctly when we refresh.

        :param mock_up: mock UpApi getter
        """
        upapi.token = self.token

        #
        # Set up the mocks to return the token and credentials
        #
        mock_up.return_value = mock.Mock('upapi.base.UpApi', autospec=True)
        mock_up.return_value.refresh_token = mock.Mock('upapi.base.UpApi.refresh_token', autospec=True)
        refreshed_token = {'access_token': 'refreshed_token'}
        mock_up.return_value.refresh_token.return_value = refreshed_token
        mock_up.return_value.credentials = mock.Mock('upapi.base.UpApi.credentials', autospec=True)

        #
        # Refresh and test
        #
        token = upapi.refresh_token()
        mock_up.assert_called_with()
        mock_up.return_value.refresh_token.assert_called_with()
        self.assertEqual(token, refreshed_token)
        self.assertEqual(upapi.credentials, mock_up.return_value.credentials)


class TestDisconnect(tests.unit.TestSDK):
    """
    Tests upapi.disconnect
    """

    @mock.patch('upapi.up', autospec=True)
    def test_disconnect(self, mock_up):
        """
        Verify that a disconnect makes the global credentials None.

        :param mock_up: mock UpApi getter
        """
        upapi.credentials = self.credentials

        mock_up.return_value = mock.Mock('upapi.base.UpApi', autospec=True)
        mock_up.return_value.disconnect = mock.Mock('upapi.base.UpApi.disconnect', autospec=True)
        upapi.disconnect()
        mock_up.assert_called_with()
        mock_up.return_value.disconnect.assert_called_with()
        self.assertIsNone(upapi.credentials)


class TestGetUser(tests.unit.TestSDK):
    """
    Tests upapi.get_user
    """

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
            credentials_storage=upapi.credentials_storage,
            user_credentials=upapi.credentials)
