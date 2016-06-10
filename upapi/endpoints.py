"""
This module holds all the UP API routes used in the SDK.
"""
DOMAIN = 'https://jawbone.com'
AUTH_PATH = '%s/auth/oauth2' % DOMAIN

"""
OAuth Endpoints
"""
AUTH = '%s/auth' % AUTH_PATH
TOKEN = '%s/token' % AUTH_PATH

"""
Resource Endpoints
"""
DISCONNECT = '%s/nudge/api/v.1.0/users/@me/PartnerAppMembership' % DOMAIN
