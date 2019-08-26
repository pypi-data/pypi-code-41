# -*- coding: utf-8 -*-
"""Notification system module.

Usage:
- Add reation methods that are executed when a new notification arrives
  using addReactionMethod; The message is directly passed to each and
  every method.
- Throw a new notification using newNotification; the message is passed to the
  reactionMethods.
- If needed, remove methods again using removeReactionMethod.
"""

from typing import Callable

reactionMethods = []
notifications = []


def addReactionMethod(method, throwArchived: bool = False):
    """Add method to reaction methods executed when on notification.

    Args:
        throwArchived (bool): True if archived notificaions should be thrown.
            If true, all archived notifications are passed once to the newly
            added reaction method. Default: False.
    """
    reactionMethods.append(method)
    if throwArchived:
        for m in notifications:
            newNotification(m, archive=False)


def removeReactionMethod(method: Callable):
    """Remove method from reactionMethods.
    
    Args:
        method (Callable): Method to be removed from list of methods.
    """
    i = reactionMethods.index(method)
    del reactionMethods[i]


def newNotification(message: str, archive: bool = True):
    """Throw new notification.
    
    Args:
        message (str): Message to be thrown.
        archive (bool): Whether this notification should be archived.
            Default: True.
    """
    if archive:
        notifications.append(message)
    for m in reactionMethods:
        m(message)
