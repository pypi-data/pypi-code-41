"""
Module with the public API required to use the sdk on another applications.
"""
import logging
from typing import Dict
from typing import Optional

from django_stomp.services.producer import Publisher
from jsmsgr.core.messaging import send_message_list_to_semaphore_destination

logger = logging.getLogger(__name__)


def send_msgs_to_user(msgs_dict: Dict, semaphore_publisher: Optional[Publisher] = None):
    """
    Sends msgs to the user.

    Example of msgs list with SMS and email:

    {
        "msgs": [
            {
                "msg": "bla bla bla",
                "type": "sms", "
                external_id": "uuid123",
                "callback_mo_destination": "queue/mo",
                "to_user_id": "toUuid123"   # sends SMS to this user
            },
            {
                "msg": "<strong>Hello world!</strong>",
                "subject": "sub1",
                "type": "email"
                "to_user_id": "toUuid123"   # sends an EMAIL to this user
            }
        ]
    }

    """
    logger.debug(f"Got validated msgs...")

    try:
        send_message_list_to_semaphore_destination(msgs_dict["msgs"], semaphore_publisher=semaphore_publisher)
    except BaseException as e:
        logger.error("An exception occure while sending msg to the user...")
        logger.exception(e)


def send_msg_to_user(msg_dict: Dict, semaphore_publisher: Optional[Publisher] = None):
    """
    Sends msg to the user.

    Example of SMS:

        {
            "msg": "bla bla bla",
            "type": "sms", "
            "external_id": "uuid123",
            "callback_mo_destination": "queue/mo",
            "to_user_id": "toUUID123"  # sends SMS to this user
        }

    Example of email:

        {
            "msg": "<strong>Hello world!</strong>",
            "subject": "sub1",
            "type": "email",
            "to_user_id": "toUUID123"  # sends an EMAIL to this user
        }
    """
    logger.debug(f"Got validated msg...")
    try:
        send_message_list_to_semaphore_destination([msg_dict], semaphore_publisher=semaphore_publisher)
    except BaseException as e:
        logger.error("An exception occure while sending msg to the user...")
        logger.exception(e)
