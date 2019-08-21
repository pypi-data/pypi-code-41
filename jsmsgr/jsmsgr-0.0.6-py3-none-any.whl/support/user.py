"""
Module with functions related to user services.
"""
import logging
from typing import Dict
from typing import Optional

from jsm_user_services.services.user import get_user_data_from_id
from jsm_user_services.services.user import get_user_data_from_server

logger = logging.getLogger(__name__)


def get_user_data_for_msg_destination(user_id: Optional[str] = None) -> Dict:
    """
    Gets user_data to get the destination of SMS and EMAIL messages.
    """
    if user_id:
        logger.debug("Getting user data from id...")
        user_data = get_user_data_from_id(user_id)

    else:
        logger.debug("Getting user data from server...")
        user_data = get_user_data_from_server()

    # standardized_user_data = {"name": user_data["name"], "phones": user_data["phones"], "emails": user_data["emails"]}

    logger.debug(f"Returning user_data: {user_data}")
    return user_data
