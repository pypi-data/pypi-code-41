"""Mixin classes for the main abstract devices."""

__all__ = (
    "ChallengeMixin",
)


class ChallengeMixin(object):
    """
    Mixin class that defines the basic structure of a Challenge.

    We use NotImplementedError's instead of ABC because
    django's Model doesn't implement ABC's and that would
    result in a metaclass conflict.
    """

    @property
    def device(self):  # pragma: no cover
        """
        Foreign key that points to the correct device.

        Each device SHOULD have only one type of Challenge.

        :return: The ForeignKey to the correct device
        :rtype: django.db.models.fields.related.ForeignKey
        """
        raise NotImplementedError("This property must be overridden")

    def dispatch(self):  # pragma: no cover
        """
        Dispatch the challenge with a value to be verified.

        If this challenge isn't dispatchable, then this method must be
        overridden as None.

        :return: The value that is used
        :rtype: str | int
        """
        raise NotImplementedError("This method must be implemented")

    def verify(self, value, save=True):  # pragma: no cover
        """
        Verify the value.

        This method also set's the confirm attribute of the model.

        :param value: The value of this challenge to verify
        :type value: str | int

        :param save: Whether this model should call self.save() or not
        :type save: bool

        :return: Whether the value is confirmed or not
        :rtype: bool
        """
        raise NotImplementedError("This method must be implemented")
