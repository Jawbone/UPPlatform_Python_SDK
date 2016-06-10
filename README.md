# UPPlatform_Python_SDK
Python SDK for the [Jawbone UP API](https://jawbone.com/up/developer/)

***The SDK is still under active development, so expect frequent changes.***

This SDK provides an object-oriented interface for working with the UP APIs. The UP APIs provide an OAuth2 workflow for accessing protected resources, so this SDK makes heavy use of the [Requests-OAuthlib](http://requests-oauthlib.readthedocs.io/) package (which makes life super easy).

## Getting Started
### Register your application
Visit the [UP Developer Portal](https://jawbone.com/up/developer/) and click [Sign In](https://jawbone.com/up/developer/auth/login) to login with your UP account (or to create a new account).

Once you have created your account, you can create a new application by clicking the **Create App** button on your [account page](https://jawbone.com/up/developer/account). Fill out the form with the specific details for your application. If you don't know what to put for the URLs, review the [Authentication documentation](https://jawbone.com/up/developer/authentication).

### Install the SDK
***When active development stops, we will put this on pypi. For now, installation is a bit manual.***

1. Download/clone/fork this repository into your application's PYTHONPATH.
1. Install the dependencies.
```bash
pip install -r upapi/requirements.txt
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

**OAuth redirect URL** must be one of the URLs you specified when creating your application. If you have multiple URLs, you do not need to set this parameter and instead specify a URL when calling ```get_redirect_url```

The ```upapi.scopes``` module provides a list of all the avaialable scopes. You can find scope definitions in the [UP API Authentication documentation](https://jawbone.com/up/developer/authentication).

The SDK can automatically refresh any expired access tokens. To do so, you must provide a **token_saver** function, which the SDK call with the value of the new token. For more details, refer to the [Requests-OAuthlib documentation](http://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html#third-recommended-define-automatic-token-refresh-and-update).

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

If your application has multiple OAuth redirect URLs, then you can pass one of them as the ```override_url``` parameter of ```get_redirect_url```.

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
The UP API OAuth2 tokens will expire after one year, so you will need to refresh them.
```python
upapi.refresh_token()
```
This will use the existing value of ```upapi.token``` to get a new token and then set it as the new value of ```upapi.token```.

#### Disconnecting Users
In certain instances, you will need to disconnect a user from your application and the UP API. The [Disconnection documentation](https://jawbone.com/up/developer/disconnection) provides details on when and how this can happen.
```python
upapi.disconnect
```
This will use the existing value of ```upapi.token``` to send a disconnection request to the API and then clear the value of ```upapi.token```.

## UpApi
The SDK creates ```UpApi``` objects to manage the OAuth connection and issue all requests to the UP API. By default, an ```UpApi``` object initializes itself with the global values you have already set in the ```upapi``` module. However, if you want to manage the OAuth connect yourself, you can create your own ```UpApi``` objects.
```python
up = upapi.UpApi(
  app_id = <Client Id>
  app_secret = <App Secret>
  app_redirect_uri = <OAuth redirect URL>
  app_scope = [upapi.scopes.<Scope0>, upapi.scopes.<Scope1>,...]
  app_token_saver = <token_saver>
  app_token = <token>)
```

For more details, read the documentation in the code.

## What's next?
The next steps for the SDK will be to add objects to represent each of the [resources in the UP API](https://jawbone.com/up/developer/endpoints).

For now, if you would like to use the SDK, you can establish the OAuth connection according to the instructions above. Then, you can issue requests through the UpApi object's ```oauth``` attribute, which is an instance of ```requests_oauthlib.OAuth2Session```.
```python
up = upapi.UpApi()
resp = up.oauth.get('https://jawbone.com/nudge/api/v.1.1/users/@me')
resp.json()
```

## Help!
If you have questions about the SDK or the UP API, check out the [docs](https://jawbone.com/up/developer/).

Can't find the answer, ask a question on [Stack Overflow using the jawbone tag](http://stackoverflow.com/questions/tagged/jawbone)

Still need help? Email apisupport @ jawbone.com
