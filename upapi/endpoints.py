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

"""
User-specific resources
"""
USER = '{}/users/@me'.format(RESOURCE)
USERBANDEVENTS = '{}/bandevents'.format(USER)
USERBODYEVENTS = '{}/body_events'.format(USER)
USERHEARTRATES = '{}/heartrates'.format(USER)
USERGENERIC = '{}/generic_events'.format(USER)
USERGOALS = '{}/goals'.format(USER)
USERMEALS = '{}/meals'.format(USER)
USERMOODS = '{}/mood'.format(USER)
USERMOVES = '{}/moves'.format(USER)
USERREFRESH = '{}/refreshToken'.format(USER)
USERSETTINGS = '{}/settings'.format(USER)
USERSLEEPS = '{}/sleeps'.format(USER)
USERTIMEZONE = '{}/timezone'.format(USER)
USERTRENDS = '{}/trends'.format(USER)
USERFRIENDS = '{}/friends'.format(USER)
USERWORKOUTS = '{}/workouts'.format(USER)
PUBSUB = '{}/pubsub'.format(USER)
DISCONNECT = '{}/PartnerAppMembership'.format(USER)

"""
Data-specific resources
"""
XID = '{xid}'
UPDATE = '/partialUpdate'
GRAPH = '/image'
TICKS = '/ticks'
BODYEVENTS = '{}/body_events/{}'.format(RESOURCE, XID)
GENERICEVENTS = '{}/generic_events/{}'.format(RESOURCE, XID)
GENERICUPDATE = '{}{}'.format(GENERICEVENTS, UPDATE)
MEALS = '{}/meals/{}'.format(RESOURCE, XID)
MEALSUPDATE = '{}{}'.format(MEALS, UPDATE)
MOODS = '{}/mood/{}'.format(RESOURCE, XID)
MOVES = '{}/moves/{}'.format(RESOURCE, XID)
MOVESGRAPH = '{}{}'.format(MOVES, GRAPH)
MOVESTICKS = '{}{}'.format(MOVES, TICKS)
SLEEPS = '{}/sleeps/{}'.format(RESOURCE, XID)
SLEEPSGRAPH = '{}{}'.format(SLEEPS, GRAPH)
SLEEPSPHASES = '{}{}'.format(SLEEPS, TICKS)
WORKOUTS = '{}/workouts/{}'.format(RESOURCE, XID)
WORKOUTSGRAPH = '{}{}'.format(WORKOUTS, GRAPH)
WORKOUTSTICKS = '{}{}'.format(WORKOUTS, TICKS)
WORKOUTSUPDATE = '{}{}'.format(WORKOUTS, UPDATE)