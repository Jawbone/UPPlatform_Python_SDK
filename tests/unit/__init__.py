"""
Dummy data for Resource testcases.
"""
import mock
import unittest
import upapi.base
import upapi.scopes


class TestResource(unittest.TestCase):

    def setUp(self):
        """
        Initialize some data for an UP app.
        """
        self.app_id = 'app_id'
        self.app_secret = 'app_secret'
        self.app_redirect_uri = 'app_redirect_uri'
        self.app_scope = [upapi.scopes.MOVE_READ, upapi.scopes.SLEEP_READ]
        self.token = {
            "access_token": "access_token",
            "token_type": "Bearer",
            "expires_in": 31536000,
            "refresh_token": "refresh_token"}
        self.credentials = mock.Mock(spec='oauth2client.client.OAuth2Credentials')
        self.credentials.token_response = self.token
        self.credentials.authorize = mock.Mock(spec_set='oauth2client.client.OAuth2Credentials.authorize')
        self.credentials.set_store = mock.Mock(spec_set='oauth2client.client.OAuth2Credentials.set_store')
        self.creds_storage = mock.Mock(spec_set='oauth2client.client.Storage')
        self.mock_creds_saver = mock.Mock(spec=['credentials'])
        self.mock_token_saver = mock.Mock(spec=['token'])

        #
        # Common objects.
        #
        self.up = upapi.base.UpApi(self.app_id, self.app_secret, self.app_redirect_uri)
        self.upcreds = upapi.base.UpApi(
            self.app_id,
            self.app_secret,
            self.app_redirect_uri,
            user_credentials=self.credentials)
        self.upstore = upapi.base.UpApi(
            self.app_id,
            self.app_secret,
            self.app_redirect_uri,
            credentials_storage=self.creds_storage)


class TestUserResource(TestResource):

    def setUp(self):
        """
        Initialize for a regular Resource test and add User object specifics.
        """
        super(TestUserResource, self).setUp()

        with mock.patch('upapi.user.User.get', autospec=True):
            self.user = upapi.user.User(
                self.app_id,
                self.app_secret,
                app_redirect_uri=self.app_redirect_uri,
                user_credentials=self.credentials)


class TestSDK(unittest.TestCase):

    def setUp(self):
        """
        Initialize upapi values.
        """
        upapi.client_id = 'client_id'
        upapi.client_secret = 'client_secret'
        upapi.redirect_uri = 'redirect_uri'
        upapi.token = None
        upapi.credentials = None

        self.token = {
            "access_token": "access_token",
            "token_type": "Bearer",
            "expires_in": 31536000,
            "refresh_token": "refresh_token"}
        self.credentials = mock.Mock(spec='oauth2client.client.OAuth2Credentials')
