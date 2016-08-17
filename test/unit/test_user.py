"""
Unit tests for the User object
"""
import mock
import test.unit
import upapi.endpoints
import upapi.user


class TestUser(test.unit.TestResource):

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
            app_token=self.token)
        mock_get.assert_called_with(user, upapi.endpoints.USER)
        self.assertEqual(user.first, user_data['first'])
        self.assertEqual(user.last, user_data['last'])
