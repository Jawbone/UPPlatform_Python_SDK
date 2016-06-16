"""
This module holds all the UP API routes used in the SDK.
https://jawbone.com/up/developer/endpoints
"""
DOMAIN = 'https://jawbone.com'

"""
OAuth Endpoints
"""
AUTH_PATH = '{}/auth/oauth2'.format(DOMAIN)
AUTH = '{}/auth'.format(AUTH_PATH)
TOKEN = '{}/token'.format(AUTH_PATH)

"""
Resource Endpoints
"""
def user_path(version):
    """
    Generate a user resource path for the given API version

    :param version: API version
    :return: user resource path
    """
    return '/nudge/api/{}/users/@me'.format(version)

DISCONNECT = '{}{}/PartnerAppMembership'.format(DOMAIN, user_path('v.1.0'))
PUBSUB = '{}{}/pubsub'.format(DOMAIN, user_path('v.1.1'))
