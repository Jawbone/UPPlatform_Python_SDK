"""
Unit tests for upapi.base.UpApi
"""
import datetime
import httplib
import json
import mock
import tests.unit
import upapi.base
import upapi.endpoints
import upapi.exceptions
import upapi.meta
import upapi.scopes


class TestUpApi(tests.unit.TestResource):
    @mock.patch('datetime.datetime', autospec=True)
    @mock.patch('oauth2client.client.OAuth2Credentials', autospec=True)
    def test_token_to_creds(self, mock_creds, mock_dt):
        """
        Verify that token_to_creds instantiates an OAuth2Credentials object with the correct parameters.

        :param mock_creds: mocked OAuth2Credentials class
        """
        #
        # Remove some precision from now() so that we don't fail due to the amount of time it takes to verify the test.
        #
        mock_dt.now = mock.Mock()
        nowish = datetime.datetime.today()
        nowish.replace(second=0, microsecond=0)
        mock_dt.now.return_value = nowish

        self.up.token_to_creds(self.token)
        mock_creds.assert_called_with(
            self.token['access_token'],
            self.app_id,
            self.app_secret,
            self.token['refresh_token'],
            nowish + datetime.timedelta(seconds=self.token['expires_in']),
            upapi.endpoints.TOKEN,
            upapi.base.USERAGENT,
            token_response=self.token,
            scopes=self.up.app_scope)

    @mock.patch('oauth2client.client.OAuth2WebServerFlow', autospec=True)
    def test__refresh_flow(self, mock_flow):
        """
        Verify creation of flow object.

        :param mock_flow: mocked oauth object
        """
        upapi.base.UpApi(self.app_id, self.app_secret, self.app_redirect_uri)
        mock_flow.assert_called_with(
            self.app_id,
            client_secret=self.app_secret,
            scope=upapi.scopes.BASIC_READ,
            redirect_uri=self.app_redirect_uri,
            user_agent=upapi.base.USERAGENT,
            auth_uri=upapi.endpoints.AUTH,
            token_uri=upapi.endpoints.TOKEN)

    @mock.patch('httplib2.Http', autospec=True)
    def test__refresh_http(self, mock_http):
        """
        Verify that _refresh_http correctly creates the http object.

        :param mock_http: mock httplib class
        """
        #
        # No credentials, http is None
        #
        up = upapi.base.UpApi(self.app_id, self.app_secret, self.app_redirect_uri)
        self.assertIsNone(up.http)

        #
        # Credentials, authorize http
        #
        upapi.base.UpApi(
            self.app_id,
            self.app_secret,
            self.app_redirect_uri,
            user_credentials=self.credentials)
        mock_http.assert_called_with()
        self.credentials.authorize.assert_called()

    @mock.patch('upapi.base.UpApi.token_to_creds', autospec=True)
    def test___init__(self, mock_t2c):
        """
        Verify that UpApi creation correctly handles credentials and tokens passed in and that scope is defaulted.
        """
        #
        # Neither passed in, no call
        #
        upapi.base.UpApi(self.app_id, self.app_secret, self.app_redirect_uri)
        self.assertFalse(mock_t2c.called)

        #
        # Both passed in, no call
        # No scope, then default
        #
        up = upapi.base.UpApi(
            self.app_id,
            self.app_secret,
            self.app_redirect_uri,
            user_credentials=self.credentials,
            user_token=self.token)
        self.assertFalse(mock_t2c.called)
        self.assertEqual(up.app_scope, upapi.scopes.BASIC_READ)

        #
        # Only token passed in, call
        # Scope passed in, save it
        #
        up = upapi.base.UpApi(
            self.app_id,
            self.app_secret,
            self.app_redirect_uri,
            app_scope=self.app_scope,
            user_token=self.token)
        mock_t2c.assert_called_with(up, self.token)
        self.assertEqual(up.app_scope, self.app_scope)

    @mock.patch('upapi.base.UpApi._refresh_flow', autospec=True)
    def test_redirect_uri(self, mock_refresh):
        """
        Verify overriding a redirect url refreshes OAuth.
        """
        override_url = 'override_url'
        self.up.redirect_uri = override_url
        self.assertEqual(self.up.redirect_uri, override_url)
        mock_refresh.assert_called_with(self.up)

    @mock.patch('upapi.base.UpApi._refresh_http', autospec=True)
    def test_credentials(self, mock_refresh):
        """
        Verify setting credentials refreshes OAuth.
        """
        self.assertIsNone(self.up.credentials)
        self.up.credentials = self.credentials
        self.assertEqual(self.up.credentials, self.credentials)
        mock_refresh.assert_called_with(self.up)

    @mock.patch('oauth2client.client.OAuth2Credentials', autospec=True)
    @mock.patch('upapi.base.UpApi.token_to_creds', autospec=True)
    def test_token(self, mock_t2c, mock_creds):
        """
        Verify that setting the token sets the credentials and refreshes oauth.
        """
        #
        # Mock token_to_creds returning mocked credentials whose token_response is the token.
        #
        mock_creds.token_response = self.token
        mock_t2c.return_value = mock_creds

        #
        # Initially token is None, then setting it, should set creds, and the lookup will pull token_response.
        #
        self.assertIsNone(self.up.token)
        self.up.token = self.token
        mock_t2c.assert_called_with(self.up, self.token)
        self.assertEqual(self.up.credentials, mock_creds)
        self.assertEqual(self.up.token, self.token)

    def test_call_savers(self):
        """
        Verify that credential and token savers only get called if they exist.
        """
        #
        # No savers, no calls
        #
        self.up.call_savers()
        self.assertFalse(self.mock_creds_saver.called)
        self.assertFalse(self.mock_token_saver.called)

        #
        # Cred saver only
        #
        up = upapi.base.UpApi(
            self.app_id,
            self.app_secret,
            self.app_redirect_uri,
            credentials_saver=self.mock_creds_saver)
        up.call_savers()
        self.mock_creds_saver.assert_called_with(up.credentials)
        self.assertFalse(self.mock_token_saver.called)

        #
        # Token saver only
        #
        self.mock_creds_saver.reset_mock()
        up = upapi.base.UpApi(
            self.app_id,
            self.app_secret,
            self.app_redirect_uri,
            token_saver=self.mock_token_saver)
        up.call_savers()
        self.assertFalse(self.mock_creds_saver.called)
        self.mock_token_saver.assert_called_with(up.token)

        #
        # Both savers
        #
        up = upapi.base.UpApi(
            self.app_id,
            self.app_secret,
            self.app_redirect_uri,
            credentials_saver=self.mock_creds_saver,
            token_saver=self.mock_token_saver)
        up.call_savers()
        self.mock_creds_saver.assert_called_with(up.credentials)
        self.mock_token_saver.assert_called_with(up.token)

    @mock.patch('oauth2client.client.OAuth2WebServerFlow.step2_exchange', autospec=True)
    @mock.patch('upapi.base.UpApi.call_savers', autospec=True)
    def test_get_up_token(self, mock_savers, mock_exchange):
        """
        Verify that getting a token from API sets the credentials and calls the savers.

        :param mock_exchange: mocked flow call
        """
        mock_exchange.return_value = self.credentials
        callback_url = 'http://127.0.0.1:8080/dummy?state=state&code=code'
        token = self.up.get_up_token(callback_url)
        mock_exchange.assert_called_with(self.up.flow, 'code')
        self.assertEqual(self.up.credentials, self.credentials)
        self.assertEqual(self.up.token, self.token)
        self.assertEqual(token, self.token)
        mock_savers.assert_called_with(self.up)

    def _set_token_response(self, token):
        """
        Helper function to create a mock side-effect when refreshing a token.

        :param token: dict to use for the token_response
        :return: token setter
        """
        def setter(_):
            """
            Set the token.
            """
            self.upcreds.credentials.token_response = token

        return setter

    @mock.patch('oauth2client.client.OAuth2Credentials.refresh')
    @mock.patch('upapi.base.UpApi.call_savers', autospec=True)
    def test_refresh_token(self, mock_savers, mock_refresh):
        """
        Verify that refreshing the token updates the credentials and calls the savers.

        :param mock_savers: mocked token saver call
        :param mock_refresh: mocked token refresh call
        """
        #
        # Going to test the update to credentials.token_response, so set that and make it the mocked refresh
        # side-effect.
        #
        self.credentials.token_response = self.token
        new_token = {
            'access_token': 'new_access_token',
            "token_type": "Bearer",
            "expires_in": 31536000,
            "refresh_token": "refresh_token"}
        mock_refresh.side_effect = self._set_token_response(new_token)
        self.credentials.refresh = mock_refresh

        #
        # Now refresh.
        #
        self.upcreds.refresh_token()
        self.assertTrue(mock_refresh.called)
        self.assertEqual(self.upcreds.credentials.token_response, new_token)
        mock_savers.assert_called_with(self.upcreds)

    @mock.patch('httplib2.Response', autospec=True)
    def test__raise_for_status(self, mock_resp):
        """
        Verify that an exceptions gets raised for unexpected responses.

        :param mock_resp: mocked httplib Response
        """
        #
        # ok_statuses should not raise
        #
        mock_resp.status = httplib.CREATED
        self.up.resp = mock_resp
        self.up.content = ''
        try:
            self.up._raise_for_status([httplib.OK, httplib.CREATED])
        except Exception as exc:
            self.fail('_raise_for_status unexpectedly threw {}'.format(exc))

        #
        # Anything else should raise.
        #
        mock_resp.status = httplib.ACCEPTED
        self.assertRaises(
            upapi.exceptions.UnexpectedAPIResponse,
            self.up._raise_for_status,
            [httplib.OK, httplib.CREATED])

    @mock.patch('httplib2.Http.request', autospec=True)
    @mock.patch('httplib2.Response', autospec=True)
    def test__request(self, mock_resp, mock_request):
        """
        Verify that _request sets up the meta object correctly and returns the response data.

        :param mock_resp: mocked Response object
        :param mock_request: mocked Http.request method
        """
        mock_resp.status = httplib.OK
        resp_content = {
            'meta': {
                'user_xid': 'user_xid',
                'message': 'message',
                'code': 'code',
                'time': 1471463170},
            'data': 'data'}
        mock_request.return_value = (mock_resp, json.dumps(resp_content))
        self.upcreds.http.request = mock_request
        resource = 'https://up.resource'
        data = self.upcreds._request(resource)

        #
        # Verify meta object created successfully.
        #
        self.assertEqual(self.upcreds.meta.user_xid, resp_content['meta']['user_xid'])
        self.assertEqual(self.upcreds.meta.message, resp_content['meta']['message'])
        self.assertEqual(self.upcreds.meta.code, resp_content['meta']['code'])
        self.assertEqual(
            self.upcreds.meta.time,
            datetime.datetime.fromtimestamp(resp_content['meta']['time']))

        #
        # Verify the response data.
        #
        self.assertEqual(data, resp_content['data'])

    @mock.patch('upapi.base.UpApi._request', autospec=True)
    def test_get(self, mock_request):
        """
        Verify get uses the correct HTTP method

        :param mock_request: mocked _request method
        """
        resource = 'https://up.resource'
        self.up.get(resource)
        mock_request.assert_called_with(self.up, resource)

    @mock.patch('upapi.base.UpApi._request', autospec=True)
    def test_delete(self, mock_request):
        """
        Verify delete uses the correct HTTP method

        :param mock_request: mocked _request method
        """
        resource = 'https://up.resource'
        self.up.delete(resource)
        mock_request.assert_called_with(self.up, resource, method='DELETE')

    @mock.patch('upapi.base.UpApi.delete', autospec=True)
    @mock.patch('upapi.base.UpApi.call_savers', autospec=True)
    def test_disconnect(self, mock_savers, mock_delete):
        """
        Verify that a disconnect calls the API, refreshes, and calls the savers.
        """
        self.upcreds.disconnect()
        mock_delete.assert_called_with(self.upcreds, upapi.endpoints.DISCONNECT)
        self.assertIsNone(self.upcreds.credentials)
        mock_savers.assert_called_with(self.upcreds)
