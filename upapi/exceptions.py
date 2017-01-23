"""
Exceptions that the SDK will throw.
"""


class UnexpectedAPIResponse(Exception):
    """
    UpApi raises this for API responses other than expected (according to the documentation)
    """
    pass


class MissingCredentials(Exception):
    """
    Raised when trying to act on behalf of the user without setting the Credentials object.
    """
    pass