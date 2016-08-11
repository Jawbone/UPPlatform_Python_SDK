"""
PubSub object for registering/disconnecting user-specific webhooks and processing incoming PubSub event notifications.
"""
class PubSub(object):

    def __init__(self, payload):
        """
        Convert payload of a pubsub callback into pubsub objects

        :param payload: body of the pubsub callback request
        """
        super(PubSub, self).__init__()