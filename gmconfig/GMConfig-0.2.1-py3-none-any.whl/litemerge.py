from gmconfig.utils import createLogger

logger = createLogger("litemerge")


def liteMerge(current_object: dict, merge_object: dict) -> dict:

    for key, value in merge_object.items():

        if current_object.get(key) and isinstance(value, dict):
            logger.debug("Key (dict) :: " + key)

            current_value = current_object.get(key, {})
            current_object[key] = liteMerge(current_value, value)
        else:
            current_object[key] = value

    return current_object
