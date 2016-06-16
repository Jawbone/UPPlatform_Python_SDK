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
        upapi.token_saver = None
        self.up = upapi.UpApi()
        super(TestUpApi, self).setUp()

    def _attribute_test(self, cid, secret, uri, scope, saver, token):
        """
        Helper function to test equality for UpApi object attributes.

        :param cid: client id
        :param secret: app secret key
        :param uri: redirect uri
        :param scope: list of scopes
        :param saver: token saver
        :param token: token
        """
        self.assertEqual(self.up.app_id, cid)
        self.assertEqual(self.up.app_secret, secret)
        self.assertEqual(self.up._redirect_uri, uri)
        self.assertEqual(self.up.app_scope, scope)
        self.assertEqual(self.up.app_token_saver, saver)
        self.assertEqual(self.up._token, token)

    def test___init__(self):
        """
        Verify defaulting of __init__ params
        """
        self._attribute_test(
            upapi.client_id,
            upapi.client_secret,
            upapi.redirect_uri,
            upapi.scope,
            upapi.token_saver,
            upapi.token)

        #
        # Override properties
        #
        app_id = 'app_id'
        app_secret = 'app_secret'
        app_redirect_uri = 'app_redirect_uri'
        app_scope = [upapi.scopes.FRIENDS_READ]
        app_token_saver = mock.Mock(spec=['token'])
        app_token = 'app_token'
        self.up = upapi.UpApi(
            app_id=app_id,
            app_secret=app_secret,
            app_redirect_uri=app_redirect_uri,
            app_scope=app_scope,
            app_token_saver=app_token_saver,
            app_token=app_token)
        self._attribute_test(app_id, app_secret, app_redirect_uri, app_scope, app_token_saver, app_token)

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
        upapi.token_saver = mock.Mock(spec=['token'])
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

    def _saver_test(self, test_func, test_args=None, saver_args=None):
        """
        Helper function to verify when and how a token saver should be called.

        :param test_func: function that tests other code execution thatconditionally calls token_saver
        :param test_args: arguments to pass to test_func
        :param saver_args: arguments to pass to the token saver
        """
        mock_saver = mock.Mock(spec=['token'])

        #
        # self.up does not have a token_saver
        #
        test_func(self.up, *test_args)
        mock_saver.assert_not_called()

        #
        # Now, test with a token_saver
        #
        up = upapi.UpApi(app_token_saver=mock_saver)
        test_func(up, *test_args)
        mock_saver.assert_called_once_with(*saver_args)

    @mock.patch('upapi.requests_oauthlib.OAuth2Session.fetch_token')
    def _get_token_test(self, up, ret_token, mock_fetch):
        """
        Helper function to verify the fetch_token call and the token returned.

        :param up: the UpApi object
        :param ret_token: expected token
        :param mock_fetch: mocked requests_oauthlib fetch method
        """
        mock_fetch.return_value = ret_token
        callback_url = 'https://callback.url'
        token = up.get_up_token(callback_url)
        mock_fetch.assert_called_with(
            upapi.endpoints.TOKEN,
            authorization_response=callback_url,
            client_secret=up.app_secret)
        self.assertEqual(token, ret_token)

    def test_get_up_token(self):
        """
        Verify that getting a new token calls the token_saver if it's defined.
        """
        token = {'access_token': 'access_token'}
        self._saver_test(self._get_token_test, test_args=[token], saver_args=[token])

    @mock.patch('upapi.requests_oauthlib.OAuth2Session.refresh_token')
    def _refresh_test(self, up, ret_token, mock_refresh):
        """
        Helper function to verify the refresh call and the token returned.

        :param up: the UpApi object
        :param ret_token: expected token
        :param mock_refresh: mocked requests_oauthlib token refresh method
        """
        mock_refresh.return_value = ret_token
        token = up.refresh_token()
        mock_refresh.assert_called_with(
            upapi.endpoints.TOKEN,
            client_id=upapi.client_id,
            client_secret=upapi.client_secret)
        self.assertEqual(token, ret_token)

    def test_refresh_token(self):
        """
        Verify the requests_oauthlib call to refresh the token and that it updates the UpApi object.
        """
        token = {'access_token': 'access_token'}
        self._saver_test(self._refresh_test, test_args=[token], saver_args=[token])

    def _disconnect_test(self, up, mock_response, mock_delete):
        """
        Verifies the expected behavior of disconnect.
        :param up: the UpApi object
        :param mock_response: mock OAuth lib Response object
        :param mock_delete: mock OAuth lib function
        """
        mock_response.status_code = httplib.OK
        mock_delete.return_value = mock_response
        up.disconnect()
        self.assertIsNone(up._token)
        self.assertIsNone(up.oauth)

    @mock.patch('upapi.requests_oauthlib.OAuth2Session.delete', autospec=True)
    @mock.patch('upapi.requests_oauthlib.requests.Response', autospec=True)
    @mock.patch('upapi.requests_oauthlib.requests.Response.raise_for_status')
    def test_disconnect(self, mock_raise, mock_response, mock_delete):
        """
        Verify that a disconnect sets the token and oauth to None, or raises the correct Exceptions.

        :param mock_raise: mock OAuth lib Response function
        :param mock_response: mock OAuth lib Response object
        :param mock_delete: mock OAuth lib function
        """
        self._saver_test(self._disconnect_test, test_args=[mock_response, mock_delete], saver_args=[None])

    @mock.patch('upapi.requests_oauthlib.requests.Response', autospec=True)
    @mock.patch('upapi.requests_oauthlib.requests.Response.raise_for_status')
    def test__raise_for_status(self, mock_raise, mock_response):
        """
        Verify that exceptions are raised for the proper response code.

        :param mock_raise: mock OAuth lib Response function
        :param mock_response: mock OAuth lib Response object
        """
        mock_response.raise_for_status = mock_raise

        #
        # ok_statuses should not raise
        #
        mock_response.status_code = httplib.CREATED
        try:
            self.up._raise_for_status([httplib.OK, httplib.CREATED], mock_response)
        except Exception as exc:
            self.fail('_raise_for_status unexpectedly threw {}'.format(exc))
        mock_raise.assert_not_called()

        #
        # 40x/50x should raise from requests_oauthlib
        #
        mock_response.status_code = httplib.NOT_FOUND
        mock_raise.side_effect = requests.exceptions.HTTPError
        self.assertRaises(
            mock_raise.side_effect,
            self.up._raise_for_status,
            [httplib.OK, httplib.CREATED],
            mock_response)

        #
        # Anything else should raise from the SDK.
        #
        mock_response.status_code = httplib.ACCEPTED
        mock_raise.side_effect = None
        mock_raise.reset_mock()
        self.assertRaises(
            upapi.UnexpectedAPIResponse,
            self.up._raise_for_status,
            [httplib.OK, httplib.CREATED],
            mock_response)
        mock_raise.assert_called_with()


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
    """
    Unit tests for upapi.refresh_token
    """

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
    """
    Unit tests for upapi.disconnect
    """

    @mock.patch('upapi.requests_oauthlib.OAuth2Session.delete', autospec=True)
    def test_disconnect(self, mock_delete):
        """
        Verify that a disconnect makes the global token None.

        :param mock_delete: mock OAuth lib function
        """
        upapi.token = {'access_token': 'access_token'}
        mock_response = mock.Mock(spec='upapi.requests_oauthlib.Response')
        mock_response.status_code = httplib.OK
        mock_delete.return_value = mock_response
        upapi.disconnect()
        self.assertIsNone(upapi.token)
