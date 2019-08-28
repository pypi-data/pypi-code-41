# -*- coding:utf-8 -*-
from .signals import after_preuser_add as after_preuser_add_signal
from .signals import after_preuser_pay as after_preuser_pay_signal
from .utils import after_preuser_add, after_preuser_pay
from .models import UserShareImage


class Moderator(object):
    """
    Handles moderation of a set of models.

    An instance of this class will maintain a list of one or more
    models registered for comment moderation, and their associated
    moderation classes, and apply moderation to all incoming comments.

    To register a model, obtain an instance of ``Moderator`` (this
    module exports one as ``moderator``), and call its ``register``
    method, passing the model class and a moderation class (which
    should be a subclass of ``CommentModerator``). Note that both of
    these should be the actual classes, not instances of the classes.

    To cease moderation for a model, call the ``unregister`` method,
    passing the model class.

    For convenience, both ``register`` and ``unregister`` can also
    accept a list of model classes in place of a single model; this
    allows easier registration of multiple models with the same
    ``CommentModerator`` class.

    The actual moderation is applied in two phases: one prior to
    saving a new comment, and the other immediately after saving. The
    pre-save moderation may mark a comment as non-public or mark it to
    be removed; the post-save moderation may delete a comment which
    was disallowed (there is currently no way to prevent the comment
    being saved once before removal) and, if the comment is still
    around, will send any notification emails the comment generated.

    """

    def __init__(self):
        self.connect()

    def connect(self):
        """
        Hook up the moderation methods to pre- and post-save signals
        from the comment models.

        """
        #
        # after_preuser_add_signal.connect(after_preuser_add, sender=UserShareImage)
        # after_preuser_pay_signal.connect(after_preuser_pay, sender=UserShareImage)

        # 通过二维码注册为peruser
        # preuser_add.connect(user_qrcode_reg,sender=)
