"""
All API responses contain meta data particular to the API request.
"""
import datetime


class Meta(object):
    """
    The Meta object holds data about the API response itself.
    """
    def __init__(self, user_xid, message, code, time):
        """
        Create a meta object by passing in the meta dict.

        :param user_xid: User's XID
        :param message: response message
        :param code: HTTP response code
        :param time: unixtime
        """
        self.user_xid = user_xid
        self.message = message
        self.code = code
        self.time = datetime.datetime.fromtimestamp(time)
