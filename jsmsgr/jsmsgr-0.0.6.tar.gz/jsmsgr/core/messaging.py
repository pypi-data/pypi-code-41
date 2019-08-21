"""
Module with functions required to send messages to Semaphore.
"""
import logging
import uuid
from typing import Dict
from typing import List
from typing import Optional

from django_stomp.builder import build_publisher
from django_stomp.services.producer import Publisher
from django_stomp.services.producer import do_inside_transaction

from jsmsgr.core.msg_builders import build_email_contract
from jsmsgr.core.msg_builders import build_sms_contract
from jsmsgr.settings import JSMSGR_DESTINATION
from jsmsgr.settings import SEMAPHORE_SDK_PUBLISHER_NAME

logger = logging.getLogger(__name__)


def build_semaphore_contract(msg_dict: Dict) -> Dict:
    """
    Builds dict with user data to publish to semaphore destination.
    """
    # semaphore_body: Dict = {"body": {}}
    semaphore_body: Dict = {}

    if msg_dict["type"] == "sms":
        semaphore_body = build_sms_contract(msg_dict)

    if msg_dict["type"] == "email":
        semaphore_body = build_email_contract(msg_dict)

    logger.debug("Returning contract...")

    return semaphore_body


def build_publisher_for_semaphore() -> Publisher:
    """
    Builds a queue publisher to send msgs to Semaphore.
    """
    semaphore_publisher_id = f"{SEMAPHORE_SDK_PUBLISHER_NAME}-{str(uuid.uuid4())}"
    logger.debug(f"Got Semaphore's publisher name: {semaphore_publisher_id}")

    queue_publisher = build_publisher(semaphore_publisher_id)
    logger.debug(f"Returning publisher...")

    return queue_publisher


def send_message_to_semaphore_destination(msg_dict: Dict, queue_publisher: Publisher) -> None:
    """
    Sends message to semaphore destination.
    """
    semaphore_contract = build_semaphore_contract(msg_dict)
    queue_publisher.send(semaphore_contract, queue=JSMSGR_DESTINATION)


def send_message_list_to_semaphore_destination(
    msg_list: List[Dict], semaphore_publisher: Optional[Publisher] = None
) -> None:
    """
    Sends message to semaphore destination.
    """
    is_external_publisher = True

    if semaphore_publisher is None:
        is_external_publisher = False
        semaphore_publisher = build_publisher_for_semaphore()

        logger.debug("No publisher found. Built one for Semaphore's destination...")

    try:
        with do_inside_transaction(semaphore_publisher):
            for msg_dict in msg_list:
                logger.debug(f"Processing msg with transactions: {msg_dict}")
                send_message_to_semaphore_destination(msg_dict, semaphore_publisher)

    finally:
        if not is_external_publisher:
            logger.debug(f"Closing publisher connection because it's NOT external...")
            semaphore_publisher.close()
