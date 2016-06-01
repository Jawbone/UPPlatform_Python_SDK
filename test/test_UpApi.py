"""
Unit tests for upapi.__init__
"""
import unittest
import upapi
import urlparse


def get_redirect_param(url):
    """
    Retrieve the redirect_uri parameter from the URL.

    :param url: URL to parse
    :return: the redirect_uri param
    """
    return urlparse.parse_qs(urlparse.urlparse(url).query)['redirect_uri'][0]


class TestGetRedirectUrl(unittest.TestCase):
    def test_get_redirect_url(self):
        """
        Unit tests for upapi.get_redirect_url

        :return: None
        """
        #
        # Explicit redirect_url
        #
        url = 'https://explicit.com'
        redirect_url = upapi.get_redirect_url(app_url=url)
        self.assertEqual(get_redirect_param(redirect_url), url)

        #
        # Global redirect uri
        #
        url = 'https://global.com'
        upapi.redirect_uri = url
        redirect_url = upapi.get_redirect_url()
        self.assertEqual(get_redirect_param(redirect_url), url)

        #
        # Override with redirect_url
        #
        url = 'https://override.com'
        redirect_url = upapi.get_redirect_url(app_url=url)
        self.assertEqual(get_redirect_param(redirect_url), url)
