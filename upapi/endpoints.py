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
VERSION = 'v.1.1'
RESOURCE = '{}/nudge/api/{}'.format(DOMAIN, VERSION)
USER = '{}/users/@me'.format(RESOURCE)
FRIENDS = '{}/friends'.format(USER)
PUBSUB = '{}/pubsub'.format(USER)
DISCONNECT = '{}/PartnerAppMembership'.format(USER)
