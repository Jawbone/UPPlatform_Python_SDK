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
        self.token = {'access_token': 'access_token'}
        self.mock_saver = mock.Mock(spec=['token'])

        #
        # Common object with no saver.
        #
        self.up = upapi.base.UpApi(
            self.app_id,
            self.app_secret,
            app_redirect_uri=self.app_redirect_uri,
            app_scope=self.app_scope,
            app_token=self.token)
