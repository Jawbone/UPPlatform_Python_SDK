"""
Unit tests for the User object
"""
import mock
import tests.unit
import upapi.endpoints
import upapi.user


class TestUser(tests.unit.TestResource):

    @mock.patch('upapi.user.User.get', autospec=True)
    def test___init__(self, mock_get):
        """
        Verify User object creation.

        :param mock_get: mock the UpApi get method
        """
        user_data = {'first': 'first', 'last': 'last'}
        mock_get.return_value = user_data
        user = upapi.user.User(
            self.app_id,
            self.app_secret,
            app_redirect_uri=self.app_redirect_uri,
            user_token=self.token)
        mock_get.assert_called_with(user, upapi.endpoints.USER)
        self.assertEqual(user.first, user_data['first'])
        self.assertEqual(user.last, user_data['last'])

    @mock.patch('upapi.user.User.get', autospec=True)
    @mock.patch('upapi.user.friends.Friends', autospec=True)
    def test_friends(self, mock_friends, mock_get):
        """
        Verify call to create Friends object

        :param mock_friends: mocked Friends object
        """
        user = upapi.user.User(
            self.app_id,
            self.app_secret,
            app_redirect_uri=self.app_redirect_uri,
            user_token=self.token)
        self.assertTrue(mock_get.called)
        user.friends
        mock_friends.assert_called_with(*user.args, **user.kwargs)
