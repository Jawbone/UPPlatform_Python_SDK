"""
The Friends and Friend objects represent resources from the friends endpoint:
https://jawbone.com/up/developer/endpoints/user
"""
import upapi.base


class Friends(upapi.base.UpApi):
    """
    The Friends object represents a list of Friend objects.
    """
    def __init__(self, *args, **kwargs):
        super(Friends, self).__init__(*args, **kwargs)
        friends_data = self.get(upapi.endpoints.USERFRIENDS)
        self.items = []
        for item in friends_data['items']:
            self.items.append(Friend(item))
        self.size = friends_data['size']


class Friend(object):
    """
    The Friend object holds the xid of a user's friend.
    """
    def __init__(self, friend_data):
        self.xid = friend_data['xid']
