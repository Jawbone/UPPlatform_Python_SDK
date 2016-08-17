"""
Unit tests for the Friends and Friend objects
"""
import mock
import test.unit
import upapi.user.friends


class TestFriends(test.unit.TestResource):
    
    @mock.patch('upapi.base.UpApi.get', autospec=True)
    def test___init__(self, mock_get):
        """
        Verify Friends object creation.

        :param mock_get: mocked UpApi get method
        """
        friends_data = {
            'items': [{'xid': '0'}, {'xid': '1'}],
            'size': 2
        }
        mock_get.return_value = friends_data
        friends = upapi.user.friends.Friends(
            self.app_id,
            self.app_secret,
            app_redirect_uri=self.app_redirect_uri,
            app_scope=self.app_scope,
            app_token=self.token)
        for index, friend in enumerate(friends.items):
            self.assertEqual(friend.xid, friends_data['items'][index]['xid'])
        self.assertEqual(friends.size, friends_data['size'])
