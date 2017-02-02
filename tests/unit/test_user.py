"""
Unit tests for the User object
"""
import mock
import tests.unit
import upapi.endpoints
import upapi.user


class TestUser(tests.unit.TestUserResource):
    """
    Tests upapi.user
    """

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
            user_credentials=self.credentials)
        mock_get.assert_called_with(user, upapi.endpoints.USER)
        self.assertEqual(user.first, user_data['first'])
        self.assertEqual(user.last, user_data['last'])
        self.assertIsNone(user._friends)

    @mock.patch('upapi.user.User.get_friends', autospec=True)
    def test_friends(self, mock_get_friends):
        """
        Verify call to create Friends object

        :param mock_get_friends: mocked friends getter
        """
        mock_get_friends.return_value = mock.Mock('upapi.user.friends.Friends', autospec=True)

        #
        # Verify _friends is None. Then call the property and verify it gets set.
        #
        self.assertIsNone(self.user._friends)
        first_friends = self.user.friends
        mock_get_friends.assert_called_once_with(self.user)
        self.assertEqual(first_friends, mock_get_friends.return_value)
        self.assertEqual(self.user._friends, first_friends)

        #
        # Call friends property again and verify that the endpoint is not hit again.
        #
        second_friends = self.user.friends
        mock_get_friends.assert_called_once_with(self.user)
        self.assertEqual(first_friends, second_friends)

    @mock.patch('upapi.user.friends.Friends', autospec=True)
    def test_get_friends(self, mock_friends):
        """
        Verify call to create Friends object

        :param mock_friends: mocked Friends object
        """
        #
        # _friends should start as None
        #
        self.assertIsNone(self.user._friends)

        #
        # Get friends and verify the call and that _friends is set.
        #
        mock_friends.return_value = mock.Mock()
        self.user.get_friends()
        mock_friends.assert_called_with(*self.user.args, **self.user.kwargs)
        self.assertEqual(self.user._friends, mock_friends.return_value)
