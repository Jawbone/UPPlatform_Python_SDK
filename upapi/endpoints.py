"""
This module holds all the UP API routes used in the SDK.
https://jawbone.com/up/developer/endpoints
"""
DOMAIN = 'https://jawbone.com'
AUTH_PATH = '{}/auth/oauth2'.format(DOMAIN)

"""
OAuth Endpoints
"""
AUTH = '{}/auth'.format(AUTH_PATH)
TOKEN = '{}/token'.format(AUTH_PATH)

"""
Resource Endpoints
"""
DISCONNECT = '{}/nudge/api/v.1.0/users/@me/PartnerAppMembership'.format(DOMAIN)
