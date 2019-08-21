"""
Module with functions to build dicts to publish data.
"""
import logging
from typing import Dict

from jsmsgr.core.msg_processing import process_msg_content_replacements
from jsmsgr.support.user import get_user_data_for_msg_destination

logger = logging.getLogger(__name__)


def build_sms_contract(msg_dict: Dict) -> Dict:
    """
    Builds an SMS contract for Semaphore.
    """
    logger.debug("Building sms contract...")

    user_data = get_user_data_for_msg_destination(user_id=msg_dict.get("to_user_id"))
    first_phone_number = user_data.get("phones", [])[0]["number"]

    replaced_msg = process_msg_content_replacements(msg_dict["msg"], user_data)

    semaphore_body = {
        "body": {
            "message_type": "sms",
            "type": "add_message",
            "message_text": replaced_msg,
            "phone": first_phone_number,
            "external_id": msg_dict.get("external_id"),
            "callback_mo_destination": msg_dict.get("callback_mo_destination"),
        }
    }

    logger.debug(f"Got sms contract: {semaphore_body}")
    return semaphore_body


def build_email_contract(msg_dict: Dict) -> Dict:
    """
    Builds an EMAIL contract for Semaphore.
    """
    logger.debug("Building email contract...")

    user_data = get_user_data_for_msg_destination(user_id=msg_dict.get("to_user_id"))
    first_email = user_data.get("emails", [])[0]["email"]

    replaced_msg = process_msg_content_replacements(msg_dict["msg"], user_data)

    semaphore_body = {
        "body": {
            "message_type": "email",
            "text": replaced_msg,
            "destinations": [first_email],
            "subject": msg_dict["subject"],
            "ind_html": True,
        }
    }

    logger.debug(f"Got email contract: {semaphore_body}")
    return semaphore_body
