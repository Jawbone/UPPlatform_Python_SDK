# UPPlatform_Python_SDK
Python SDK for the [Jawbone UP API](https://jawbone.com/up/developer/)

***The SDK is still under active development, so expect frequent changes.***

This SDK provides an object-oriented interface for working with the UP APIs. The UP APIs provide an OAuth2 workflow for accessing protected resources, so this SDK makes heavy use of the [oauth2client](https://oauth2client.readthedocs.io/en/latest/) package (which makes life super easy).

## Getting Started
### Register your application
Visit the [UP Developer Portal](https://jawbone.com/up/developer/) and click [Sign In](https://jawbone.com/up/developer/auth/login) to login with your UP account (or to create a new account).

Once you have signed in, you can create a new application by clicking the **Create App** button on your [account page](https://jawbone.com/up/developer/account). Fill out the form with the specific details for your application. If you don't know what to put for the URLs, review the [Authentication documentation](https://jawbone.com/up/developer/authentication).

### Install the SDK
The SDK exists on [pypi](https://pypi.python.org/pypi/upapi), so the easiest way to install it is to use pip:
```bash
pip install upapi
```

### Initialize the SDK
```python
import upapi
import upapi.scopes

upapi.client_id = <Client Id>
upapi.client_secret = <App Secret>
upapi.redirect_uri = <OAuth redirect URL>
upapi.scope = [upapi.scopes.<Scope0>, upapi.scopes.<Scope1>,...]
upapi.credentials_storage = <Storage object>
```

You can find your **Client Id** and **App Secret** in your Application Details (click on your app in the bottom left of the nav on the UP Developer Portal).

**OAuth redirect URL** must be one of the URLs you specified when creating your application. If you have multiple URLs, you can change the value of ```upapi.redirect_uri``` as necessary.

The [```upapi.scopes```](https://github.com/Jawbone/UPPlatform_Python_SDK/blob/master/upapi/scopes.py) module provides a list of all the available scopes. You can find scope definitions in the [UP API Authentication documentation](https://jawbone.com/up/developer/authentication).

Set ```upapi.credentials_storage``` to an instance of [oauth2client.client.Storage](http://oauth2client.readthedocs.io/en/latest/source/oauth2client.client.html#oauth2client.client.Storage) to ensure tokens/credentials get saved when automatically refreshed. For more details, refer to the [Automatic Refresh and Storage Objects](#automatic-refresh-and-storage-objects) section.

#### Token vs. Credentials
In this context, a token is the access token returned by the [UP Authentication APIs](https://jawbone.com/up/developer/authentication) during the OAuth flow.

Credentials on the other hand refers to the [oauth2client.client.OAuth2Credentials](https://oauth2client.readthedocs.io/en/latest/source/oauth2client.client.html#oauth2client.client.OAuth2Credentials) object that the oauth2client library creates when using the library to retrieve the access token.

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

#### Get the access token and/or credentials
After the user grants access to your application, the UP API redirects the user back to the URL you specified with an **authorization_code**. You then need to exchange this code for an access token. Pass the entire URL to the ```get_token``` function to do this. Additionally, the ```get_token``` function will create a **credentials** object based on the access token. You can retrieve the credentials object from the ```upapi.credentials``` parameter.
```python
token = upapi.get_token(url)
credentials = upapi.credentials
```

### Returning Users
Once a user has granted your application access to UP data, you can save the access token or credentials object for re-use on subsequent interactions with the UP API.

#### Set Credentials (or Token)
After you have initialized the SDK according to the instructions above, all you need to do is set the value of the ```credentials``` parameter. 
```python
upapi.credentials = <credentials>
```
The SDK uses a credentials object rather than the token directly because the credentials object automatically tracks token expiration rather than requiring your application to handle it manually. However, if you would prefer to only interact with tokens, you can use the following helper functions, which will set/get an access token to/from the credentials object:
```python
upapi.set_access_token(<token>)
token = upapi.get_access_token()
```

Note: if this is the same session in which you authenticated this user, the SDK will automatically set the value of ```upapi.credentials``` when you call ```upapi.get_token```.

#### Refreshing Tokens/Credentials
The UP API OAuth2 tokens will expire after one year, so you will need to refresh them. Luckily, the SDK will refresh them for you automatically. Whenever the UP APIs return a ```401 Unauthorized``` response, the SDK will make two attempts to refresh the token and credentials. After refresh, the old values will stop working, so you should save the new ones for future requests.

##### Automatic Refresh and Storage Objects
Automatic token/credentials refresh occurs in the internal workings of the SDK, and the only way to know that a refresh occurred is to see if the value has changed. Rather than doing this manually, you can create a *Storage* object and assign it to ```upapi.credentials_storage```.
```python
upapi.credentials_storage = <Storage object>
```
When a Storage object exists, the SDK will use it to save the credentials whenever they are automatically refreshed. For more details on how to create a Storage object, refer to the [Storage documentation](https://developers.google.com/api-client-library/python/guide/aaa_oauth#storage).

##### Manual Refresh
You can always manually refresh tokens by calling ```upapi.refresh_token```:
```python
token = upapi.refresh_token()
```
This will use the existing value of ```upapi.credentials``` to return a new token as well as update ```upapi.credentials```.

#### Disconnecting Users
In certain instances, you will need to disconnect a user from your application and the UP API. The [Disconnection documentation](https://jawbone.com/up/developer/disconnection) provides details on when and how this can happen.
```python
upapi.disconnect()
```
This will use the existing value of ```upapi.credentials``` to send a disconnection request to the API and then clear the value of ```upapi.credentials```.

## User
The SDK creates [```User```](https://github.com/Jawbone/UPPlatform_Python_SDK/blob/master/upapi/user/__init__.py#L11) objects to represent the data available from the [User endpoint](https://jawbone.com/up/developer/endpoints/user). The easiest way to get the current user's object is to initialize the SDK and then run:
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
You can retrieve a user's friends list by accessing the ```friends``` property of the user object. ```friends``` is an object that contains the ```size``` of the friends list and the list itself under ```items```. Each element of the ```items``` list is a [```Friend```](https://github.com/Jawbone/UPPlatform_Python_SDK/blob/master/upapi/user/friends.py#L21) object.
```python
>>> friends = user.friends
>>> friends.size
2
>>> friends.items[1].xid
u'VkzWpOaqgeX'
```

If you ever need to renew a user's friends list, you can simply call ```get_friends```. This method will both return the latest friends list and set the ```friends``` property on the ```User``` object.
```python
>>> friends = user.friends
...
#something changes the friends list
...
>>> new_friends = user.get_friends()
>>> new_friends == user.friends
True
```

## UpApi
All the SDK objects that represent the API [Endpoints](https://jawbone.com/up/developer/endpoints) inherit from [```UpApi```](https://github.com/Jawbone/UPPlatform_Python_SDK/blob/master/upapi/__init__.py) objects to manage the OAuth connection and issue all requests to the UP API. If you want to manually manage the connections, requests, and objects, you can create ```UpApi``` (or any other) objects directly.

### Meta
All of the UP API endpoint responses contain a ```meta``` key that describes the response itself. All SDK objects convert this JSON to a [```Meta```](https://github.com/Jawbone/UPPlatform_Python_SDK/blob/master/upapi/meta.py) object. You can access the members of this object through the ```meta``` member. For example, here's how you would access ```meta``` data in a user object:
```python
>>> user.meta.user_xid
u'6xl39CsoVp2KirfHwVq_Fx'

>>> user.meta.code
200
```

## What's next?
The next steps for the SDK will be to add the remaining objects that represent each of the [resources in the UP API](https://jawbone.com/up/developer/endpoints).

For now, if you would like to use the SDK, you can establish the OAuth connection according to the instructions above. Then, you can issue requests through the ```UpApi``` object's ```http``` attribute, which is an instance of ```httplib2.Http```.
```python
up = upapi.UpApi()
resp, content = up.http.request('https://jawbone.com/nudge/api/v.1.1/users/@me/workouts', 'GET')
```

## Help!
If you have questions about the SDK or the UP API, check out the [docs](https://jawbone.com/up/developer/).

Can't find the answer, ask a question on [Stack Overflow using the jawbone tag](http://stackoverflow.com/questions/tagged/jawbone)

Still need help? Email apisupport @ jawbone.com
