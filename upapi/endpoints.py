"""
This module holds all the UP API routes
"""
DOMAIN = 'https://jawbone.com'
AUTH_PATH = '%s/auth/oauth2' % DOMAIN

#
# OAuth endpoints
#
AUTH = '%s/auth' % AUTH_PATH
TOKEN = '%s/token' % AUTH_PATH

#
# Resource endpoints
#
DISCONNECT = '%s/nudge/api/v.1.0/users/@me/PartnerAppMembership' % DOMAIN
