# UPPlatform_Python_SDK
Python SDK for the [Jawbone UP API](https://jawbone.com/up/developer/)

***The SDK is still under active development, so expect frequent changes.***

This SDK provides an object-oriented interface for working with the UP APIs. The UP APIs provide an OAuth2 workflow for accessing protected resources, so this SDK makes heavy use of the [Requests-OAuthlib](http://requests-oauthlib.readthedocs.io/) package (which makes life super easy).

## Getting Started
### Register your application
Visit the [UP Developer Portal](https://jawbone.com/up/developer/) and click [Sign In](https://jawbone.com/up/developer/auth/login) to login with your UP account (or to create a new account).

Once you have signed in, you can create a new application by clicking the **Create App** button on your [account page](https://jawbone.com/up/developer/account). Fill out the form with the specific details for your application. If you don't know what to put for the URLs, review the [Authentication documentation](https://jawbone.com/up/developer/authentication).

### Install the SDK
***When active development stops, we will put this on pypi. For now, installation is a bit manual.***

1. Download/clone/fork this repository into your application's PYTHONPATH.
1. Install the dependencies.
```bash
pip install -r upapi/requirements.txt
```

### Testing with HTTP
The UP APIs and this SDK require HTTPS urls for OAuth2, but most people do not have HTTPS set up in their local environments when developing applications. UP applications can have HTTP URLs as long as they are unpublished, and the SDK allows for HTTP as long as you set the ```OAUTHLIB_INSECURE_TRANSPORT``` environment variable. You can do this by doing one of the following:

####Set the environment variable in your shell
```bash
export OAUTHLIB_INSECURE_TRANSPORT=1
```

####Set the environment variable in Python (somewhere before you import the SDK)
```python
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
```

### Initialize the SDK
```python
import upapi
import upapi.scopes

upapi.client_id = <Client Id>
upapi.client_secret = <App Secret>
upapi.redirect_uri = <OAuth redirect URL>
upapi.scope = [upapi.scopes.<Scope0>, upapi.scopes.<Scope1>,...]
upapi.token_saver = <token_saver>
```

You can find your **Client Id** and **App Secret** in your Application Details (click on your app in the bottom left of the nav on the UP Developer Portal).

**OAuth redirect URL** must be one of the URLs you specified when creating your application. If you have multiple URLs, you can change the value of ```upapi.redirect_uri``` as necessary.

The [```upapi.scopes```](https://github.com/Jawbone/UPPlatform_Python_SDK/blob/master/upapi/scopes.py) module provides a list of all the available scopes. You can find scope definitions in the [UP API Authentication documentation](https://jawbone.com/up/developer/authentication).

#### Token Saver
If you specify a ```token_saver``` function, then the SDK will automatically call it whenever a token changes:
- fetching a new token
- refreshing an existing token
- disconnecting a token

Addtionally, when a ```token_saver``` exists, the SDK will automatically refresh an expired token.

The ```token_saver``` function should take the token as its only argument. On disconnect, the token passed in will be ```None```.

For more details, refer to the [Requests-OAuthlib documentation](http://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html#third-recommended-define-automatic-token-refresh-and-update).

## Authentication
The UP API uses OAuth2 to grant access to user data. For details, please read the [Authentication documentation](https://jawbone.com/up/developer/authentication).

### New Users
The first thing any application will need to do is have a user authenticate in the UP system and grant access to UP data. With the SDK,  this is a two step process:

1. Redirect the user to an app-specific login screen.
1. Convert a temporary authorization code into an access token.

#### Redirect to login
The SDK provides a helper function to generate an application-specific UP login URL.
```python
url = upapi.get_redirect_url()
```

#### Get the access token
After the user grants access to your application, the UP API redirects the user back to the URL you specified with an **authorization_code**. You then need to exchange this code for an access token. Pass the entire URL to the ```get_token``` function to do this.
```python
token = upapi.get_token(url)
```

### Returning Users
Once a user has granted your application access to UP data, you can save the access token for re-use on subsequent interactions with the UP API.

#### Set Token
After you have initialized the SDK according to the instructions above, all you need to do is set the value of the token parameter.
```python
upapi.token = <token>
```

Note: if this is the same session in which you authenticated this user, the SDK will automatically set the value of ```upapi.token``` when you call ```upapi.get_token```.

#### Refreshing Tokens
The UP API OAuth2 tokens will expire after one year, so you will need to refresh them. The easiest way to do this is to set ```upapi.token_saver```. Then, the SDK will automatically refresh expired tokens. However, you can always manually refresh a token.
```python
upapi.refresh_token()
```
This will use the existing value of ```upapi.token``` to get a new token and then set it as the new value of ```upapi.token```.

#### Disconnecting Users
In certain instances, you will need to disconnect a user from your application and the UP API. The [Disconnection documentation](https://jawbone.com/up/developer/disconnection) provides details on when and how this can happen.
```python
upapi.disconnect()
```
This will use the existing value of ```upapi.token``` to send a disconnection request to the API and then clear the value of ```upapi.token```.

## User
The SDK creates [```User```](https://github.com/Jawbone/UPPlatform_Python_SDK/blob/pdr-182/upapi/user/__init__.py) objects to represent the data available from the [User endpoint](https://jawbone.com/up/developer/endpoints/user). The easiest way to get the current user's object is to initialize the SDK and then run:
```python
user = upapi.get_user()
```
The ```data``` key of the User endpoint response gets converted from JSON into members of the newly created user object. The example response from the documentation would become:
```python
>>> user.xid
u'6xl39CsoVp2KirfHwVq_Fx'
>>> user.first
u'James'
>>> user.last
u'Franklin'
```

Remember that the amount of user data available depends on the scope--```basic_read``` vs. ```extended_read```--the user granted access.

### Friends
You can retrieve a user's friends list by accessing the ```friends``` property of the user object. ```friends``` is an object that contains the ```size``` of the friends list and the list itself under ```items```. Each element of the ```items``` list is a [```Friend```](https://github.com/Jawbone/UPPlatform_Python_SDK/blob/pdr-182/upapi/user/friends.py) object.
```python
>>> friends = user.friends
>>> friends.size
2
>>> friends.items[1].xid
u'VkzWpOaqgeX'
```
## UpApi
All the SDK objects that represent the API [Endpoints](https://jawbone.com/up/developer/endpoints) inherit from [```UpApi```](https://github.com/Jawbone/UPPlatform_Python_SDK/blob/master/upapi/__init__.py) objects to manage the OAuth connection and issue all requests to the UP API. If you want to manually manage the connections, requests, and objects, you can create ```UpApi``` (or any other) objects directly.

### Meta
All of the UP API endpoint responses contain a ```meta``` key that describes the response itself. All SDK objects convert this JSON to a [```Meta```](https://github.com/Jawbone/UPPlatform_Python_SDK/blob/pdr-182/upapi/meta.py) object. You can access the members of this object through the ```meta``` member. For example, here's how you would access ```meta``` data in a user object:
```python
>>> user.meta.user_xid
u'6xl39CsoVp2KirfHwVq_Fx'

>>> user.meta.code
200
```

## What's next?
The next steps for the SDK will be to add the remaining objects that represent each of the [resources in the UP API](https://jawbone.com/up/developer/endpoints).

For now, if you would like to use the SDK, you can establish the OAuth connection according to the instructions above. Then, you can issue requests through the ```UpApi``` object's ```oauth``` attribute, which is an instance of ```requests_oauthlib.OAuth2Session```.
```python
up = upapi.UpApi()
resp = up.oauth.get('https://jawbone.com/nudge/api/v.1.1/users/@me/workouts')
resp.json()
```

## Help!
If you have questions about the SDK or the UP API, check out the [docs](https://jawbone.com/up/developer/).

Can't find the answer, ask a question on [Stack Overflow using the jawbone tag](http://stackoverflow.com/questions/tagged/jawbone)

Still need help? Email apisupport @ jawbone.com
