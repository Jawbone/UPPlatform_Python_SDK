"""
Unit tests for upapi.base.UpApi
"""
import datetime
import httplib
import mock
import requests
import test.unit
import upapi.base
import upapi.endpoints
import upapi.exceptions
import upapi.meta
import upapi.scopes


class TestUpApi(test.unit.TestResource):

    @mock.patch('upapi.base.requests_oauthlib.OAuth2Session')
    def test__refresh_oauth(self, mock_oauth):
        """
        Verify that _refresh_oauth creates the session according to the parameters.

        :param mock_oauth: mock session object
        """
        #
        # No token saver -> no auto refresh
        #
        upapi.base.UpApi(self.app_id, self.app_secret, app_redirect_uri=self.app_redirect_uri)
        mock_oauth.assert_called_with(
            client_id=self.app_id,
            redirect_uri=self.app_redirect_uri,
            scope=None,
            token=None)

        #
        # Token saver -> auto refresh
        #
        up = upapi.base.UpApi(
            self.app_id,
            self.app_secret,
            app_redirect_uri=self.app_redirect_uri,
            app_token_saver=self.mock_saver)
        mock_oauth.assert_called_with(
            client_id=self.app_id,
            redirect_uri=self.app_redirect_uri,
            scope=None,
            token=None,
            auto_refresh_url=upapi.endpoints.TOKEN,
            auto_refresh_kwargs={'client_id': self.app_id, 'client_secret': self.app_secret},
            token_updater=self.mock_saver)

        #
        # Check User-Agent
        #
        self.assertTrue(up.oauth.headers['User-Agent'].startswith(upapi.base.USERAGENT))

    def test_redirect_uri(self):
        """
        Verify overriding a redirect url refreshes OAuth.
        """
        default_oauth = self.up.oauth

        #
        # Setting the redirect URI should refresh the oauth object.
        #
        override_url = 'override_url'
        self.up.redirect_uri = override_url
        self.assertEqual(self.up.redirect_uri, override_url)
        self.assertIsNot(self.up.oauth, default_oauth)

    def test_token(self):
        """
        Verify that setting the token property refreshes the oatuh
        """
        default_oauth = self.up.oauth

        #
        # Setting the redirect URI should refresh the oauth object.
        #
        self.up.token = self.token
        self.assertEqual(self.up.token, self.token)
        self.assertIsNot(self.up.oauth, default_oauth)

    def _saver_test(self, test_func, token=None):
        """
        Helper function to verify when and how a token saver should be called.

        :param test_func: function that tests other code execution that conditionally calls token_saver
        :param token: expected token to check
        """
        #
        # self.up does not have a token_saver
        #
        test_func(self.up, token)
        self.mock_saver.assert_not_called()

        #
        # Now, test with a token_saver
        #
        up = upapi.base.UpApi(self.app_id, self.app_secret, app_token_saver=self.mock_saver)
        test_func(up, token)
        self.mock_saver.assert_called_once_with(token)

    @mock.patch('upapi.base.requests_oauthlib.OAuth2Session.fetch_token')
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
        self._saver_test(self._get_token_test)

    @mock.patch('upapi.base.requests_oauthlib.OAuth2Session.refresh_token')
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
            client_id=self.app_id,
            client_secret=self.app_secret)
        self.assertEqual(token, ret_token)

    def test_refresh_token(self):
        """
        Verify the requests_oauthlib call to refresh the token and that it updates the UpApi object.
        """
        self._saver_test(self._refresh_test)

    @mock.patch('upapi.base.requests_oauthlib.requests.Response', autospec=True)
    @mock.patch('upapi.base.requests_oauthlib.requests.Response.raise_for_status')
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
        self.up.response = mock_response
        try:
            self.up._raise_for_status([httplib.OK, httplib.CREATED])
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
            [httplib.OK, httplib.CREATED])

        #
        # Anything else should raise from the SDK.
        #
        mock_response.status_code = httplib.ACCEPTED
        mock_raise.side_effect = None
        mock_raise.reset_mock()
        self.assertRaises(
            upapi.exceptions.UnexpectedAPIResponse,
            self.up._raise_for_status,
            [httplib.OK, httplib.CREATED])
        mock_raise.assert_called_with()

    @mock.patch('upapi.base.requests_oauthlib.requests.Response.json')
    @mock.patch('upapi.base.requests_oauthlib.requests.Response', autospec=True)
    @mock.patch('upapi.base.requests_oauthlib.OAuth2Session.get')
    def test__request(self, mock_get, mock_response, mock_json):
        """
        Verify that _request sets up the meta object correctly and returns the response data.

        :param mock_get: mocked OAuth get call
        :param mock_response: mocked response object
        :param mock_json: mocked json conversion methdo
        :return:
        """
        resp_data = {
            'meta': {
                'user_xid': 'user_xid',
                'message': 'message',
                'code': 'code',
                'time': 1471463170},
            'data': 'data'}
        mock_json.return_value = resp_data
        mock_response.json = mock_json
        mock_response.status_code = httplib.OK
        mock_get.return_value = mock_response
        resource = 'https://up.resource'
        data = self.up._request(mock_get, resource)

        #
        # Verify meta object created successfully.
        #
        self.assertEqual(self.up.meta.user_xid, resp_data['meta']['user_xid'])
        self.assertEqual(self.up.meta.message, resp_data['meta']['message'])
        self.assertEqual(self.up.meta.code, resp_data['meta']['code'])
        self.assertEqual(
            self.up.meta.time,
            datetime.datetime.fromtimestamp(resp_data['meta']['time']))

        #
        # Verify the response data.
        #
        self.assertEqual(data, resp_data['data'])

    @mock.patch('upapi.base.UpApi._request', autospec=True)
    def test_get(self, mock_request):
        """
        Verify get uses the correct HTTP method

        :param mock_request: mocked _request method
        """
        resource = 'https://up.resource'
        self.up.get(resource)
        mock_request.assert_called_with(self.up, self.up.oauth.get, resource)

    @mock.patch('upapi.base.UpApi._request', autospec=True)
    def test_delete(self, mock_request):
        """
        Verify delete uses the correct HTTP method

        :param mock_request: mocked _request method
        """
        resource = 'https://up.resource'
        self.up.delete(resource)
        mock_request.assert_called_with(self.up, self.up.oauth.delete, resource)

    @mock.patch('upapi.base.UpApi.delete', autospec=True)
    def _disconnect_test(self, up, token, mock_delete):
        """
        Verifies the expected behavior of disconnect.

        :param up: the UpApi object
        :param token: dummy parameter so we can use _saver_test
        :param mock_delete: mock UpApi function
        """
        up.disconnect()
        mock_delete.assert_called_with(up, upapi.endpoints.DISCONNECT)
        self.assertEqual(up._token, token)
        self.assertIsNone(up._token)
        self.assertIsNone(up.oauth)

    def test_disconnect(self):
        """
        Verify that a disconnect sets the token and oauth to None, or raises the correct Exceptions.
        """
        self._saver_test(self._disconnect_test)
