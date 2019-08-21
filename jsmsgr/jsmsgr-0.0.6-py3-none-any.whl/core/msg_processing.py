"""
Module with functions to process messages.
"""
import logging
from typing import Dict

from jsmsgr.settings import SEMAPHORE_REPLACEMENT_TAG_USER

logger = logging.getLogger(__name__)


def process_msg_content_replacements(msg: str, user_data: Dict) -> str:
    """
    Perform replaces on the original message. If no replacements are found,
    it returns the original message.
    """
    logger.debug(f"Got msg to perform replaces... {msg}")

    replaced_msg = msg.replace(SEMAPHORE_REPLACEMENT_TAG_USER, user_data["name"])

    logger.debug(f"Got replaced_msg: {replaced_msg}")

    return replaced_msg
