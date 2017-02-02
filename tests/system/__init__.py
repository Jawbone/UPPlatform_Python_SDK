"""
This script performs end-to-end system tests. To run it:
1. Create a test application at https://jawbone.com/up/developer
2. Enter upsims and create a test user for your test application
3. Run the OAuth flow with the test user to capture a token
4. Create other upsim users and have them add your original test user as friends in the app.
5. Using the keys, token, and test user data, create a client_secrets.json file in the tests/system directory.

Format of client_secrets.json:

{
  "web": {
    "client_id": <Client Id>,
    "client_secret": <App Secret>,
    "redirect_uris": [<OAuth redirect URLs>],
    "auth_uri": "https://jawbone.com/auth/oauth2/auth",
    "token_uri": "https://jawbone.com/auth/oauth2/token"
  },
  "test_user": {
    "token": {
      "access_token": <access_token>,
      "token_type": "Bearer",
      "expires_in": 31536000,
      "refresh_token": <refresh_token>
    },
    "storage_filename": "test_user.creds",
    "xid": "",
    "first": "",
    "last": "",
    "image": "",
    "weight": "",
    "height": ""
    "friends": [<friend_xid>,...]
  }
}

"""
import datetime
import httplib
import json
import oauth2client.file
import os.path
import traceback
import upapi
import upapi.base
import upapi.scopes
import urllib


#
# Test Data from the secrets file
#
with open('client_secrets.json') as secret_file:
    secrets = json.loads(secret_file.read())

#
# Templates for reporting.
#
SUMMARY = """
{total} tests
{successes} successes
{fails} failures
"""

ASSERTFAIL = """Values not equal
ACTUAL:   {}
EXPECTED: {}
"""


class TestSystem(object):
    """
    Base class for system tests.

    test_data holds global counters for test runs.
    """
    test_data = {
        'total': 0,
        'successes': 0,
        'fails': 0}

    def __init__(self, name):
        """
        Create a system test with the given name.

        :param name: human readable name of the test
        """
        self.name = name
        self.test_user = secrets['test_user']

    @staticmethod
    def assert_equal(actual, expected):
        """
        Verify actual == expected

        :param actual: real value
        :param expected: expected value
        """
        assert actual == expected, ASSERTFAIL.format(actual, expected)

    @staticmethod
    def assert_none(actual):
        """
        Verify actual is None

        :param actual: real value
        """
        assert actual is None, ASSERTFAIL.format(actual, 'None')

    @staticmethod
    def assert_not_none(actual):
        """
        Verify actual is not None

        :param actual: real value
        """
        assert actual is not None, ASSERTFAIL.format(actual, 'not None')

    @staticmethod
    def assert_datetime_within(actual, expected=None, window=2):
        """
        Verify that a datetime is between expected and (expected +/- window).

        :param actual: datetime
        :param expected: expected datetime (defaults to now)
        :param window: allowable number of seconds in the past (default 2)
        """
        if expected is None:
            now = datetime.datetime.now()
        else:
            now = expected
        delta = datetime.timedelta(seconds=window)
        assert (now - delta) <= actual <= now + delta, ASSERTFAIL.format(actual, 'within {}s of {}'.format(window, now))

    @staticmethod
    def assert_time_within(actual, expected, window=1):
        """
        Verify that a unixtime is between expected and (expected - window)

        :param actual: unix timestamp
        :param expected: expected timestamp
        :param window: allowable number of seconds in the past (default 1)
        """
        assert (expected - window) <= actual <= expected, ASSERTFAIL.format(actual, 'within {}s of {}'.format(
            window,
            expected))

    @staticmethod
    def assert_in(actual, options):
        """
        Verify that actual appears within options

        :param actual: real value
        :param options: list of possible values
        """
        assert actual in options, ASSERTFAIL.format(actual, 'in {}'.format(options))

    def assert_meta(self, meta):
        """
        Verify that the response metadata is correct.

        :param meta: the response meta object
        """
        self.assert_equal(meta.user_xid, self.test_user['xid'])
        self.assert_equal(meta.message, httplib.responses[httplib.OK])
        self.assert_equal(meta.code, httplib.OK)
        self.assert_datetime_within(meta.time, window=11)

    def run(self):
        """
        Run test and update counters and failure report if necessary.
        """
        self.test_data['total'] += 1
        try:
            self._run()
        except AssertionError:
            self.test_data['fails'] += 1
            print 'FAILED: {}\n\n'.format(self.name), traceback.format_exc()
        else:
            self.test_data['successes'] += 1
            print 'PASSED: {}'.format(self.name)

    def _run(self):
        """
        Implement this function in a subclass to run the test and verify the outcome.
        """
        raise NotImplementedError()

    @classmethod
    def print_report(cls):
        """
        Generate output of the test run.
        """
        print SUMMARY.format(
            total=cls.test_data['total'],
            successes=cls.test_data['successes'],
            fails=cls.test_data['fails'])


class TestGetRedirectUrl(TestSystem):
    """
    Test upapi.get_redirect_url
    """
    def __init__(self):
        """
        Set the expected redirect URL
        """
        self.expected_url = (
            'https://jawbone.com/auth/oauth2/auth?scope=extended_read&redirect_uri={}&response_type=code&' +
            'client_id={}&access_type=offline').format(
            urllib.quote_plus(upapi.redirect_uri),
            upapi.client_id)
        super(TestGetRedirectUrl, self).__init__('upapi.get_redirect_url')

    def _run(self):
        """
        Verify redirect URL generated correctly.
        """
        redirect_url = upapi.get_redirect_url()
        self.assert_equal(redirect_url, self.expected_url)


class TestSetGetAccessToken(TestSystem):
    """
    Test upapi.set_access_token and upapi.get_access_token
    """
    def __init__(self):
        super(TestSetGetAccessToken, self).__init__('upapi.set/get_access_token')

    def _run(self):
        """
        Verify that set correctly sets the credentials object and that get returns the token.
        """
        #
        # Token was already set during upapi initialization, so verify credentials
        #
        creds = upapi.credentials
        self.assert_equal(creds.access_token, secrets['test_user']['token']['access_token'])
        self.assert_equal(creds.client_id, upapi.client_id)
        self.assert_equal(creds.client_secret, upapi.client_secret)
        self.assert_equal(creds.refresh_token, secrets['test_user']['token']['refresh_token'])

        #
        # Expiry should match expires_in.
        #
        next_year = datetime.datetime.now()
        next_year = next_year + datetime.timedelta(seconds=secrets['test_user']['token']['expires_in'])
        self.assert_datetime_within(creds.token_expiry, expected=next_year)

        self.assert_equal(creds.token_uri, secrets['web']['token_uri'])
        self.assert_equal(creds.user_agent, upapi.base.USERAGENT)
        self.assert_none(creds.revoke_uri)
        self.assert_equal(creds.token_response, secrets['test_user']['token'])
        self.assert_equal(creds.scopes, set(upapi.scope))
        self.assert_none(creds.token_info_uri)

        #
        # Getter should give back the original token
        #
        self.assert_equal(upapi.get_access_token(), secrets['test_user']['token'])


class TestStorage(TestSystem):
    """
    Test use of credentials storage object during auto-refresh.
    """
    def __init__(self):
        """
        Clear the storage if it exists.
        """
        if os.path.isfile(secrets['test_user']['storage_filename']):
            upapi.credentials_storage.locked_delete()
        super(TestStorage, self).__init__('upapi.credentials_storage')

    def _run(self):
        """
        Trigger auto-refresh on the token. Verify storage object gets updated.
        """
        bad_token = secrets['test_user']['token'].copy()
        bad_token['access_token'] = ''
        upapi.set_access_token(bad_token)
        upapi.get_user()

        #
        # Verify creds
        #
        stored_creds = upapi.credentials_storage.locked_get()
        self.assert_equal(stored_creds.access_token, upapi.credentials.access_token)
        self.assert_equal(stored_creds.client_id, upapi.client_id)
        self.assert_equal(stored_creds.client_secret, upapi.client_secret)
        self.assert_equal(stored_creds.refresh_token, upapi.credentials.refresh_token)
        self.assert_datetime_within(stored_creds.token_expiry, upapi.credentials.token_expiry)
        self.assert_equal(stored_creds.token_uri, upapi.credentials.token_uri)
        self.assert_equal(stored_creds.user_agent, upapi.credentials.user_agent)
        self.assert_none(stored_creds.revoke_uri)
        self.assert_equal(stored_creds.token_response, upapi.credentials.token_response)
        self.assert_equal(stored_creds.scopes, upapi.credentials.scopes)
        self.assert_none(stored_creds.token_info_uri)


class TestRefreshToken(TestSystem):
    """
    Test upapi.refresh_token
    """
    def __init__(self):
        """
        Grab the old token
        """
        self.old_token = upapi.get_access_token()
        super(TestRefreshToken, self).__init__('upapi.refresh_token')

    def _run(self):
        """
        Verify token and credentials refreshed correctly.
        """
        upapi.refresh_token()

        #
        # Verify token
        #
        new_token = upapi.get_access_token()
        self.assert_not_none(new_token['access_token'])
        self.assert_equal(new_token['token_type'], self.old_token['token_type'])
        self.assert_time_within(new_token['expires_in'], self.old_token['expires_in'])
        self.assert_equal(new_token['refresh_token'], self.old_token['refresh_token'])

        #
        # Verify credentials
        #
        new_creds = upapi.credentials
        self.assert_not_none(new_creds.access_token)
        self.assert_equal(new_creds.client_id, upapi.client_id)
        self.assert_equal(new_creds.client_secret, upapi.client_secret)
        self.assert_equal(new_creds.refresh_token, self.old_token['refresh_token'])

        #
        # Expiry is next year give or take a few hours
        #
        next_year = datetime.datetime.now()
        next_year = next_year.replace(year=next_year.year + 1)
        self.assert_datetime_within(new_creds.token_expiry, expected=next_year, window=5*60*60)

        self.assert_equal(new_creds.token_uri, secrets['web']['token_uri'])
        self.assert_equal(new_creds.user_agent, upapi.base.USERAGENT)
        self.assert_none(new_creds.revoke_uri)
        self.assert_equal(new_creds.token_response, new_token)
        self.assert_equal(new_creds.scopes, set(upapi.scope))
        self.assert_none(new_creds.token_info_uri)


class TestUser(TestSystem):
    """
    Test upapi.get_user
    """
    def __init__(self):
        super(TestUser, self).__init__('upapi.get_user')

    def _run(self):
        user = upapi.get_user()
        self.assert_meta(user.meta)
        self.assert_equal(user.xid, self.test_user['xid'])
        self.assert_equal(user.first, self.test_user['first'])
        self.assert_equal(user.last, self.test_user['last'])
        self.assert_equal(user.image, self.test_user['image'])
        self.assert_equal(user.weight, self.test_user['weight'])
        self.assert_equal(user.height, self.test_user['height'])


class TestFriends(TestSystem):
    """
    Test upapi.get_user.friends
    """
    def __init__(self):
        """
        Set the expected friend data.
        """
        super(TestFriends, self).__init__('upapi.get_user.friends')
        self.test_friends = self.test_user['friends']

    def _run(self):
        friends = upapi.get_user().friends
        self.assert_meta(friends.meta)
        self.assert_equal(friends.size, len(self.test_friends))
        for friend in friends.items:
            self.assert_in(friend.xid, self.test_friends)


#
# Tests to run. Order matters.
#
TESTS = [
    TestGetRedirectUrl,
    TestSetGetAccessToken,
    TestStorage,
    TestRefreshToken,
    TestUser,
    TestFriends]


if __name__ == '__main__':
    #
    # Initialize upapi.
    #
    upapi.client_id = secrets['web']['client_id']
    upapi.client_secret = secrets['web']['client_secret']
    upapi.redirect_uri = secrets['web']['redirect_uris'][0]
    upapi.scope = [upapi.scopes.EXTENDED_READ]
    upapi.credentials_storage = oauth2client.file.Storage(secrets['test_user']['storage_filename'])
    upapi.set_access_token(secrets['test_user']['token'])

    #
    # Run the tests.
    #
    for test_class in TESTS:
        test_class().run()

    #
    # Final report.
    #
    TestSystem.print_report()
