from http import HTTPStatus
from typing import List
from uuid import UUID

import requests

from user_sdk.domain import (
    Session,
    CredentialType,
    UserProfile,
    User,
    UserRequest,
    UserDevice,
)
from user_sdk.error import (
    InvalidOTPError,
    UserAuthenticationError,
    NoSuchUser,
    ProfileAlreadyExists,
    ProfileCreationError,
    ProfileUpdateError,
    NoSuchProfile,
    UserAlreadyExists,
    UserCreationFailed,
    OTPSendFailure,
    NoRoleFound,
    InvalidRoleRequest,
    SessionNotFound,
)
from user_sdk.log import log


class UserService:
    def __init__(self, authentication_url, profile_url, authorization_url=None):
        self._authentication_url = authentication_url
        self._profile_url = profile_url
        self._authorization_url = authorization_url

    def login_with_username(self, username: str, password: str) -> Session:
        return self._login(
            cred_type=CredentialType.USERNAME, identity=username, password=password
        )

    def login_with_mobile(self, phone_number: str, otp: str) -> Session:
        return self._login(
            cred_type=CredentialType.MOBILE, identity=phone_number, otp=otp
        )

    def login_with_oauth(self, id_token: str) -> Session:
        return self._login(cred_type=CredentialType.OAUTH, identity=id_token)

    def _login(self, cred_type, identity, password=None, otp=None) -> Session:
        body = {"identity": identity, "credential_type": str(cred_type)}
        if cred_type == CredentialType.USERNAME:
            body["password"] = password
        elif cred_type == CredentialType.MOBILE:
            body["otp"] = otp
        request_url = f"{self._authentication_url}/api/v1/sign_in"
        response = requests.post(request_url, json=body)
        log(
            message="login",
            request_url=request_url,
            request_body=body,
            status_code=response.status_code,
            response=response.text,
        )
        if response.status_code == HTTPStatus.CREATED:
            return Session.from_dict(response.json()["data"])
        if response.status_code == HTTPStatus.BAD_REQUEST:
            error_type = response.json()["error"]["type"]
            if error_type == "INVALID_PASSWORD" or error_type == "INVALID_OTP":
                raise InvalidOTPError
        raise UserAuthenticationError(response.json()["error"])

    def get_user_from_session(self, session_id: str) -> Session:
        response = requests.get(
            f"{self._authentication_url}/api/v1/sessions/{session_id}"
        )
        if response.status_code == HTTPStatus.OK:
            return Session.from_dict(response.json()["data"])
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NoSuchUser

        self._raise_response_error(response)

    def attach_device(self, user_device: UserDevice):
        request_url = f"{self._profile_url}/api/v1/devices"
        request_json = user_device.to_dict()
        response = requests.post(request_url, json=request_json)
        log(
            message="attach_device",
            request_url=request_url,
            status_code=response.status_code,
            response=response.text,
            request_body=request_json,
        )

        if response.status_code == HTTPStatus.CREATED:
            return UserDevice.from_dict(response.json()["data"])

        if response.status_code == HTTPStatus.CONFLICT:
            return

        self._raise_response_error(response)

    def create_profile(self, profile: UserProfile) -> UserProfile:
        request_url = f"{self._profile_url}/api/v1/profiles"
        response = requests.put(request_url, json={"profile": profile.to_dict()})
        log(
            message="create_profile",
            request_url=request_url,
            request_body=profile.to_dict(),
            status_code=response.status_code,
            response=response.text,
        )

        if response.status_code == HTTPStatus.CREATED:
            return UserProfile.from_dict(response.json()["data"])
        if response.status_code == HTTPStatus.CONFLICT:
            raise ProfileAlreadyExists()
        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise ProfileCreationError(response.json().get("error"))

        self._raise_response_error(response)

    def bulk_upsert_profiles(self, profiles: List[UserProfile]) -> List[UserProfile]:
        request_url = f"{self._profile_url}/api/v1/profiles/bulk"
        request_json = {"profiles": [profile.to_dict() for profile in profiles]}
        response = requests.put(request_url, json=request_json)
        log(
            message="bulk_upsert_profiles",
            request_url=request_url,
            request_body=request_json,
            status_code=response.status_code,
            response=response.text,
        )

        if response.status_code == HTTPStatus.OK:
            return [
                UserProfile.from_dict(profile) for profile in response.json()["data"]
            ]
        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise ProfileCreationError(response.json().get("error"))

        self._raise_response_error(response)

    def update_profile(self, user_id: UUID, profile: dict) -> UserProfile:
        request_url = f"{self._profile_url}/api/v1/new/profiles/{user_id}"
        response = requests.patch(url=request_url, json=profile)
        log(
            message="update_profile",
            request_url=request_url,
            status_code=response.status_code,
            response=response.text,
            request_body=profile,
        )
        if response.status_code == HTTPStatus.OK:
            return UserProfile.from_dict(response.json().get("data"))
        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise ProfileUpdateError(response.json().get("error"))
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NoSuchProfile

        self._raise_response_error(response)

    def get_user_profile(self, id: UUID) -> UserProfile:
        request_url = f"{self._profile_url}/api/v1/profiles/{id}"
        response = requests.get(request_url)
        log(
            message="get_user_profile",
            request_url=request_url,
            status_code=response.status_code,
            response=response.text,
        )
        if response.status_code == HTTPStatus.OK:
            return UserProfile.from_dict(response.json().get("data"))
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NoSuchProfile

        self._raise_response_error(response)

    def get_user_profiles(self, ids: List[UUID]) -> List[UserProfile]:
        request_url = f"{self._profile_url}/api/v1/profiles/by_user_ids"
        response = requests.get(request_url, params={"ids": ",".join(map(str, ids))})
        log(
            message="get_user_profile",
            request_url=request_url,
            status_code=response.status_code,
            response=response.text,
        )
        if response.status_code == HTTPStatus.OK:
            return [UserProfile.from_dict(up) for up in response.json()["data"]]

        self._raise_response_error(response)

    def create_user(self, user_request: UserRequest):
        request_url = f"{self._authentication_url}/api/v1/users"

        response = requests.post(request_url, json=user_request.to_dict())
        log(
            message="create_user",
            request_url=request_url,
            status_code=response.status_code,
            response=response.text,
            request_body=user_request.to_dict(),
        )

        if response.status_code == HTTPStatus.CREATED:
            return User.from_dict(response.json().get("data"))
        if response.status_code == HTTPStatus.CONFLICT:
            raise UserAlreadyExists
        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise UserCreationFailed(response.json().get("error"))
        else:
            raise OTPSendFailure(response.json().get("error"))

    def bulk_create_users(self, user_requests: List[UserRequest]):
        request_json = {"users": [ur.to_dict() for ur in user_requests]}
        request_url = f"{self._authentication_url}/api/v1/users/bulk"
        response = requests.post(request_url, json=request_json)
        log(
            message="bulk_create_users",
            request_url=request_url,
            status_code=response.status_code,
            response=response.text,
            request_body=request_json,
        )

        if response.status_code == HTTPStatus.OK:
            return [User.from_dict(user) for user in response.json().get("data")]
        if response.status_code == HTTPStatus.CONFLICT:
            raise UserAlreadyExists
        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise UserCreationFailed(response.json().get("error"))
        else:
            raise OTPSendFailure(response.json().get("error"))

    def generate_otp(self, credential_type: str, identity):
        cred_type = CredentialType(credential_type)
        body = {"credential_type": cred_type.name, "identity": identity}
        request_url = f"{self._authentication_url}/api/v1/sessions/otp"
        response = requests.post(request_url, json=body)
        log(
            message="generate_otp",
            request_url=request_url,
            status_code=response.status_code,
            response=response.text,
            request_body=body,
        )
        if response.status_code != HTTPStatus.ACCEPTED:
            raise OTPSendFailure

    def get_by_email(self, email: str) -> User:
        response = requests.get(
            f"{self._authentication_url}/api/v1/users/by_identity/%s" % email
        )
        if response.status_code == HTTPStatus.OK:
            return User.from_dict(response.json().get("data"))
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NoSuchUser

        self._raise_response_error(response)

    def get_by_mobile_number(self, mobile_number: str) -> User:
        response = requests.get(
            f"{self._authentication_url}/api/v1/users/by_identity/%s" % mobile_number
        )
        if response.status_code == HTTPStatus.OK:
            return User.from_dict(response.json().get("data"))
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NoSuchUser

        self._raise_response_error(response)

    def get_by_identities(self, identities: List[str]) -> List[User]:
        response = requests.get(
            f"{self._authentication_url}/api/v1/users/by_identities",
            params={"identities": ",".join(identities)},
        )
        if response.status_code == HTTPStatus.OK:
            return [User.from_dict(u) for u in response.json().get("data")]

        self._raise_response_error(response)

    def get_by_ids(self, ids: List[str]) -> List[User]:
        response = requests.get(
            f"{self._authentication_url}/api/v1/users/by_user_ids",
            params={"ids": ",".join(ids)},
        )
        if response.status_code == HTTPStatus.OK:
            return [User.from_dict(u) for u in response.json().get("data")]

        self._raise_response_error(response)

    def get_user(self, user_id: UUID) -> User:
        response = requests.get(f"{self._authentication_url}/api/v1/users/{user_id}")
        if response.status_code == HTTPStatus.OK:
            return User.from_dict(response.json()["data"])
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NoSuchUser

        self._raise_response_error(response)

    def get_user_role(self, email: str, panel: str) -> str:
        response = requests.get(
            f"{self._authorization_url}/api/v1/role",
            params=dict(email=email, panel=panel),
        )

        if response.status_code == HTTPStatus.OK:
            return response.json()["data"]["role"]

        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NoRoleFound("No role found for this email on panel")

        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise InvalidRoleRequest("Either Panel name or email format is invalid")

        self._raise_response_error(response)

    def delete_session(self, session_id: str):
        response = requests.delete(
            f"{self._authentication_url}/api/v1/sessions/{session_id}"
        )
        if response.status_code == HTTPStatus.OK:
            return response.json()["data"]
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise SessionNotFound

        self._raise_response_error(response)

    def fetch_sessions_by_phone_number(self, phone_number: str) -> List[Session]:
        response = requests.get(
            f"{self._authentication_url}/api/v1/sessions/by_phone_number/{phone_number}"
        )
        if response.status_code == HTTPStatus.OK:
            sessions = response.json()["data"]
            return [Session.from_dict(s_dict) for s_dict in sessions]
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise NoSuchUser

        self._raise_response_error(response)

    def _raise_response_error(self, response):
        raise RuntimeError(
            f"""
            Invalid response.

            Status code: {response.status_code}
            Text:

            {response.text}
        """
        )
