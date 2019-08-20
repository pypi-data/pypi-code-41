"""
A User model, used for authentication.
"""
import hashlib
import secrets
import typing as t
from asgiref.sync import async_to_sync

from piccolo.table import Table
from piccolo.columns import Varchar, Boolean


class BaseUser(Table):
    """
    Subclass this table in your own project, so Meta.db can be defined.
    """

    username = Varchar(length=100, unique=True)
    password = Varchar(length=255)
    email = Varchar(length=255, unique=True)
    active = Boolean(default=False)
    admin = Boolean(default=False)

    class Meta:
        # This is required because 'user' is a reserved keyword in SQL, so
        # using it as a tablename causes issues.
        tablename = "piccolo_user"

    def __init__(self, **kwargs):
        """
        Generating passwords upfront is expensive, so might need reworking.
        """
        password = kwargs.get("password", None)
        if password:
            kwargs["password"] = self.__class__.hash_password(password)
        super().__init__(**kwargs)

    @classmethod
    def get_salt(cls):
        return secrets.token_hex(16)

    ###########################################################################

    @classmethod
    def update_password_sync(cls, user: t.Union[str, int], password: str):
        return async_to_sync(cls.update_password)(user, password)

    @classmethod
    async def update_password(cls, user: t.Union[str, int], password: str):
        """
        The password is the raw password string e.g. password123.
        The user can be a user ID, or a username.
        """
        if type(user) == str:
            clause = cls.username == user
        elif type(user) == int:
            clause = cls.id == user  # type: ignore
        else:
            raise ValueError(
                "The `user` arg must be a user id, or a username."
            )

        password = cls.hash_password(password)
        await cls.update().values({cls.password: password}).where(clause).run()

    ###########################################################################

    @classmethod
    def hash_password(
        cls, password: str, salt: str = "", iterations: int = 10000
    ) -> str:
        """
        Hashes the password, ready for storage, and for comparing during
        login.
        """
        if salt == "":
            salt = cls.get_salt()
        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            bytes(password, encoding="utf-8"),
            bytes(salt, encoding="utf-8"),
            iterations,
        ).hex()
        return f"pbkdf2_sha256${iterations}${salt}${hashed}"

    def __setattr__(self, name: str, value: t.Any):
        """
        Make sure that if the password is set, it's stored in a hashed form.
        """
        if name == "password":
            if not value.startswith("pbkdf2_sha256"):
                value = self.__class__.hash_password(value)

        super().__setattr__(name, value)

    @classmethod
    def split_stored_password(cls, password: str) -> t.List[str]:
        elements = password.split("$")
        if len(elements) != 4:
            raise ValueError("Unable to split hashed password")
        return elements

    @classmethod
    def login_sync(cls, username: str, password: str) -> t.Optional[int]:
        """
        Returns the user_id if a match is found.
        """
        return async_to_sync(cls.login)(username, password)

    @classmethod
    async def login(cls, username: str, password: str) -> t.Optional[int]:
        """
        Returns the user_id if a match is found.
        """
        query = (
            cls.select()
            .columns(cls.id, cls.password)
            .where((cls.username == username))
            .first()
        )
        try:
            response = await query.run()
        except ValueError:
            # No match found
            return None

        stored_password = response["password"]

        algorithm, iterations, salt, hashed = cls.split_stored_password(
            stored_password
        )

        if (
            cls.hash_password(password, salt, int(iterations))
            == stored_password
        ):
            return response["id"]
        else:
            return None
