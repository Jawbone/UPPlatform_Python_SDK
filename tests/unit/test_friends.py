"""
Unit tests for the Friends and Friend objects
"""
import mock
import tests.unit
import unittest
import upapi.endpoints
import upapi.user.friends


class TestFriends(tests.unit.TestResource):
    """
    Tests upapi.user.friends.Friends
    """
    
    @mock.patch('upapi.user.friends.Friends.get', autospec=True)
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
            user_credentials=self.credentials)
        mock_get.assert_called_with(friends, upapi.endpoints.USERFRIENDS)
        for index, friend in enumerate(friends.items):
            self.assertEqual(friend.xid, friends_data['items'][index]['xid'])
        self.assertEqual(friends.size, friends_data['size'])


class TestFriend(unittest.TestCase):
    """
    Tests upapi.user.friends.Friend
    """

    def test__init__(self):
        """
        Verify Friend object creation.
        """
        data = {'xid': 'xid'}
        test_friend = upapi.user.friends.Friend(data)
        self.assertEqual(test_friend.xid, data['xid'])
