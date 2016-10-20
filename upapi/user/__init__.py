"""
The User object represents data and interactions with the user endpoint.
https://jawbone.com/up/developer/endpoints/user
"""
import upapi.base
import upapi.endpoints
import upapi.meta
import upapi.user.friends


class User(upapi.base.UpApi):
    """
    The User object manages calls to the UP API user endpoint.
    """
    def __init__(self, *args, **kwargs):
        """
        Call the user endpoint and convert the response to a user object.

        :param args: pass through to base class
        :param kwargs: pass through to base class
        """
        self.args = args
        self.kwargs = kwargs
        self._friends = None
        super(User, self).__init__(*args, **kwargs)
        resp_data = self.get(upapi.endpoints.USER)
        for key, val in resp_data.iteritems():
            setattr(self, key, val)

    @property
    def friends(self):
        """
        If not cached yet, cache the Friends object. Return the Friends object.

        :return: a Friends object
        """
        if self._friends is None:
            self._friends = self.get_friends()
        return self._friends

    def get_friends(self):
        """
        Call the friends endpoint and convert the response to a Friends object.

        :return: a Friends object
        """
        return upapi.user.friends.Friends(*self.args, **self.kwargs)
