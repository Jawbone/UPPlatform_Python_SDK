"""
Unit tests for upapi.__init__
"""
import unittest
import upapi


class TestUpApi(unittest.TestCase):
    def setUp(self):
        """
        Create the UpApi object.
        """
        upapi.client_id = 'client_id'
        upapi.client_secret = 'client_secret'
        upapi.redirect_uri = 'redirect_uri'
        upapi.scope = ['scope0', 'scope1']
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

        #
        # Override properties
        #
        app_id = 'app_id'
        app_secret = 'app_secret'
        app_redirect_uri = 'app_redirect_uri'
        app_scope = 'app_scope'
        self.up = upapi.UpApi(
            app_id=app_id,
            app_secret=app_secret,
            app_redirect_uri=app_redirect_uri,
            app_scope=app_scope)
        self.assertEqual(self.up.app_id, app_id)
        self.assertEqual(self.up.app_secret, app_secret)
        self.assertEqual(self.up._redirect_uri, app_redirect_uri)
        self.assertEqual(self.up.app_scope, app_scope)

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

    # def test_get_up_tokens(self):
    #     default_up = self.up
    #
    #     TODO: mock the requests_oauthlib object
    #
    #     self.up.get_up_tokens()
    #     self.assertIsNot(self.up, default_up)
