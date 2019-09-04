"""Abstract models for one time passwords."""

__all__ = (
    "Device",
    "Challenge",
)

from django.db.models.base import Model
from django.db.models.deletion import CASCADE
from django.db.models.fields import BooleanField
from django.db.models.fields.related import OneToOneField


from rest_multi_factor.utils import get_user_model, get_token_model
from rest_multi_factor.models.meta import DeviceMeta
from rest_multi_factor.models.mixins import ChallengeMixin


User = get_user_model()
Token = get_token_model()


class Device(Model, metaclass=DeviceMeta):
    """
    Abstract Device Model.

    This model defines a multi factor option for a user.
    If a user doesn't have a device of a certain type of
    verification, then the type isn't available for the user.
    """

    class Meta:  # noqa: D106
        abstract = True
        ordering = ("id",)

    user = OneToOneField(User, on_delete=CASCADE)


class Challenge(Model, ChallengeMixin):
    """
    Abstract Challenge model.

    Subclasses of the Abstract Device model MUST create
    a Challenge for it. Subclasses of this model will act
    as the relation between a device and a auth token.
    """

    class Meta:  # noqa: D106
        abstract = True
        unique_together = ("token", "device")

    token = OneToOneField(Token, on_delete=CASCADE)

    confirm = BooleanField(default=False)
