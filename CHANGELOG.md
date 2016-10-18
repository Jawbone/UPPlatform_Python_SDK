# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) 
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]
### Added
- System tests
- Global ```upapi.credentials``` object if users prefer the oauth2client's credentials object to the regular access token.

### Changed
- Refactored OAuth from requests_oauthlib to oauth2client
- Refactored test directory to tests to avoid naming collisions

### Fixed
- ```upapi.get_token``` actually returns the token now

## [0.3] - 2016-08-31
### Added
- CHANGELOG.md!
- User, Friends, and Friend objects
- Meta objects created for every response
- Exceptions module
- Base unit test class for API resource objects

### Changed
- Refactored endpoints class to default to v.1.1 of the API
- Refactored UpApi class from \__init__.py to base.py to get rid of some circular import problems
- Split unit tests into test_upapi.py for SDK high level functions and test_base.py for testing UpApi


## [0.2] - 2016-08-09
### Added
- Calls to the token saver (if it exists) whenever a token gets updated.

### Changed
- More use of mocks in unit tests

## [0.1] - 2016-06-14
### Added
- Initial SDK handles OAuth flow and issuing OAuth requests
- UpApi object will be the base class for all API resources
- pip requirements.txt
- Unit tests!
- Modules for endpoints and scopes constants
