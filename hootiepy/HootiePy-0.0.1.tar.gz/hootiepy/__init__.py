from os.path import basename
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

import requests

BASE_PATH = "https://platform.hootsuite.com"


class Client(object):
    """A client for the Hootsuite OAuth2 REST API."""

    def __init__(self, application_id=None, application_secret=None,
                 access_token=None):
        self.application_id = application_id
        self.application_secret = application_secret
        self.access_token = access_token

    def get_authorization_url(self, state, redirect_uri, scope):
        """Get a URL  for users to authorize the application.

        :param str state: A string that will be passed to the redirect_url
        :param str redirect_uri: The URL to redirect after authorization
        :param list scopes: The scopes to grant the application
        :returns: str
        """
        qs = {
            "client_id": self.application_id,
            "scope": scope,
            "state": state,
            "response_type": "code",
            "redirect_uri": redirect_uri,
        }

        return BASE_PATH + "oauth2/auth/" + urlencode(qs)

    def get_current_user(self):
        """Fetch the data for the currently authenticated user.

        :returns: A dictionary with the users data ::

        "data":
        {
            "id": "15240789",
            "email": "jsmith@test.com",
            "isActive": true,
            "createdDate": "2013-05-29T13:27:24Z",
            "modifiedDate": "2013-05-29T13:27:24Z",
            "fullName": "Joe Smith",
            "companyName": "Hootsuite",
            "bio": "I am Joe Smith",
            "timezone": "America/Vancouver",
            "language": "en"
        }
        """

        return self._request("GET", "/v1/me")

    def get_current_user_organizations(self):
        """Get the organizations that the authenticated member is in.

        :returns: A dictionary with the users data ::
        "data":
        [
            {
                "id": "626731"
            }
        ]
        """

        return self._request("GET", "/v1/organizations")

    def get_current_user_social_profiles(self):
        """Get the authenticated member's social profiles

        :returns: A dictionary with the users data::

        "data":
        [
            {
                "id": "115185509"
                "type": "TWITTER",
                "socialNetworkId": "12345678",
                "socialNetworkUsername": null,
                "avatarUrl": null,
                "owner": "MEMBER",
                "ownerId": "1234354"
            }
        ]
        """

        return self._request("GET", "/v1/socialProfiles")

    def get_media_upload_link(self, file_size, mime_type):
        """Request upload link to upload media files.

        :param int file_size: Upload file size in bytes,
        :param str mime_type: Upload media mime type

        eg.
            {
                "sizeBytes": 383631,
                "mimeType": "video/mp4"
            }


        :returns: A dictionary with the AWS S3 link to upload the file to ::

        "data":
        {
            "id": "aHR0cHM6Ly9ob290c3VpdGUtdmlkZW8uczMuYW1hem9uYXdzLmNvbS9wcm9kdWN0aW9uLzEyMjU1MjQ0XzgyOTVmZjllLWFkOWYtNGNlNy1iOGE3LTgwNzI0NDAwYTBhZS5tcDQ=",
            "uploadUrl": "https://hootsuite-video.s3.amazonaws.com/production/12255244_01942650-3d42-42b8-a191-aa84eb45d105.mp4?AWSAccessKeyId=AKIAIM7ASX2JTE3ZFAAA&Expires=1471978770&Signature=b%2B196oEHxySdmE%2FC34ZRL6pXSAI%3D",
            "uploadUrlDurationSeconds": 1799
        }
        """

        json = {
            "sizeBytes": file_size,
            "mimeType": mime_type,
        }

        return self._request("POST", "/v1/media", json=json)

    def retrieve_media_upload_status(self, media_id):
        """Retrieves the status of a media upload to Hootsuite.

        :param str media_id: The Media ID to retrieve

        :returns: A dictionary with the media upload information

        "data":
        {
            "id": "aHR0cHM6Ly9ob290c3VpdGUtdmlkZW8uczMuYW1hem9uYXdzLmNvbS9wcm9kdWN0aW9uLzEyMjU1MjQ0XzgyOTVmZjllLWFkOWYtNGNlNy1iOGE3LTgwNzI0NDAwYTBhZS5tcDQ=",
            "state": "READY",
            "downloadUrl": "https://hootsuiteapis.s3-us-east-1.amazonaws.com/2147563588/5eb2d61a-1812-44d9-b1b2-a475d4238daf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIALK18ASHK1AS9DGAS%2F20160418%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20160418T215337Z&X-Amz-Expires=21&X-Amz-SignedHeaders=host&X-Amz-Signature=ea25ef6b4dabad49ec8a9cf0da2a227219222065f15a38dde2955312e2f1501d",
            "downloadUrlDurationSeconds": 1799
        }
        """

        return self._request("GET", "/v1/media/%s" % media_id)

    def retrieve_member(self, member_id):
        """Retrieves a member

        :param str member_id

        :returns: A dictionary with member information

        "data":
        {
            "id": "15240789",
            "email": "jsmith@test.com",
            "isActive": true,
            "createdDate": "2013-05-29T13:27:24Z",
            "modifiedDate": "2013-05-29T13:27:24Z",
            "fullName": "Joe Smith",
            "companyName": "Hootsuite",
            "bio": "I am Joe Smith",
            "timezone": "America/Vancouver",
            "language": "en"
        }
        """

        return self._request("GET", '/v1/members/%s' % member_id)

    def create_member(self, organization_ids, email, full_name, company_name,
                      bio, timezone, language):
        """Creates a member in a Hootsuite organization. Requires organization to manage
        members permission.

        :param list organization_ids: The organizations the member should be added to.
        :param str email: The member's email.
        :param str full_name: The member's name.
        :param str company_name: The member's company name.
        :param str bio: The member's bio.
        :param str timezone: The member's time zone. If not provided it will default to
                “America/Vancouver”. Valid values are defined at http://php.net/manual/en/timezones.php
        :param str language: The member's language. Valid Values:
                ["en" "ja" "fr" "it" "es" "de" "pt_BR" "pl" "id" "zh_CN" "zh_HK" "zh_TW" "nl" "ko" "ar" "ru" "th" "tr"]


        eg.
            {
            "organizationIds":
                [
                    "626731"
                ],
            "email": "jsmith@test.com",
            "fullName": "Joe Smith",
            "companyName": "Hootsuite",
            "bio": "I am Joe Smith",
            "timezone": "America/Vancouver",
            "language": "en"
            }

        :returns: dictionary of the newly created member.

        "data":
        {
            "id": "15240789",
            "email": "jsmith@test.com",
            "isActive": true,
            "createdDate": "2013-05-29T13:27:24Z",
            "modifiedDate": "2013-05-29T13:27:24Z",
            "fullName": "Joe Smith",
            "companyName": "Hootsuite",
            "bio": "I am Joe Smith",
            "timezone": "America/Vancouver",
            "language": "en"
        }
        """
        json = {
            "organizationIds": organization_ids,
            "email": email,
            "fullName": full_name,
            "companyName": company_name,
            "bio": bio,
            "timezone": timezone,
            "language": language
        }

        return self._request("POST", '/v1/members', json=json)

    def retrieve_member_organizations(self, member_id):
        """Retrieves the organization that the member is in.

        :param str member_id: The member ID

        :returns: a list of dictionaries for each organization the member is in.

        "data":
        [
            {
                "id": "626731"
            }
        ]
        """

        return self._request('GET', '/v1/members/%s/organizations' % member_id)



    def _request(self, method, path, json=None, form_data=None, files=None):
        """Make a signed request to the given route."""
        url = BASE_PATH + path
        print(url)
        headers = {
            "Accept": "application/json",
            "Accept-Charset": "utf-8",
            "Authorization": "Bearer %s" % self.access_token,
        }

        resp = requests.request(method, url, json=json, data=form_data,
                                files=files, headers=headers)
        print(resp.text)
        json = resp.json()
        print(json)
        if 200 <= resp.status_code < 300:
            try:
                return json["data"]
            except KeyError:
                return json

        raise HootiePyError("API request failed", json)


class HootiePyError(Exception):
    """Wrapper for exceptions generated by the Hootsuite API."""

    def __init__(self, message, resp={}):
        self.resp = resp
        try:
            error = resp["errors"][0]
        except KeyError:
            error = {}
        self.code = error.get("code", -1)
        self.msg = error.get("message", message)
        super(HootiePyError, self).__init__(self.msg)
