import logging
from ibmsecurity.utilities import tools

logger = logging.getLogger(__name__)

# URI for this module
uri = "/iam/access/v8/dynamic_clients"
requires_modules = ["mga"]
requires_version = "9.0.5.0"


def get_all(isamAppliance, sortBy=None, count=None, start=None, filter=None, check_mode=False, force=False):
    """
    Retrieve a list of API protection clients
    """
    return isamAppliance.invoke_get("Retrieve several dynamically registered clients",
                                    "{0}/{1}".format(uri, tools.create_query_string(filter=filter, sortBy=sortBy,
                                                                                    count=count, start=start)),
                                    requires_modules=requires_modules, requires_version=requires_version)


def get(isamAppliance, name, check_mode=False, force=False):
    """
    Retrieve a dynamically registered client
    """
    ret_obj = search(isamAppliance, name=name, check_mode=check_mode, force=force)
    client_id = ret_obj['data']
    warnings = ret_obj["warnings"]

    if client_id == {}:
        logger.info("Client {0} had no match, skipping retrieval.".format(name))
        warnings.append("Client Name {0} had no match.".format(name))
        return isamAppliance.create_return_object(warnings=warnings)
    else:
        return _get(isamAppliance, client_id)


def _get(isamAppliance, client_id):
    return isamAppliance.invoke_get("Retrieve a dynamically registered client", "{0}/{1}".format(uri, client_id),
                                    requires_modules=requires_modules, requires_version=requires_version)


def search(isamAppliance, name, check_mode=False, force=False):
    """
    Search API Protection Dynamic Client by name
    """
    ret_obj = get_all(isamAppliance)
    return_obj = isamAppliance.create_return_object()
    return_obj['warnings'] = ret_obj["warnings"]

    for obj in ret_obj['data']:
        if obj['name'] == name:
            logger.info("Found API Protection Dynamic Client {0} id: {1}".format(name, obj['id']))
            return_obj['data'] = obj['id']
            return_obj['rc'] = 0

    return return_obj


def delete(isamAppliance, name, check_mode=False, force=False):
    """
    Delete a dynamically registered client
    """
    ret_obj = search(isamAppliance, name, check_mode=check_mode, force=force)
    client_id = ret_obj['data']
    warnings = ret_obj["warnings"]

    if client_id == {}:
        logger.info("Client {0} not found, skipping delete.".format(name))
    else:
        if check_mode is True:
            return isamAppliance.create_return_object(changed=True, warnings=warnings)
        else:
            return isamAppliance.invoke_delete(
                "Delete a dynamically registered client", "{0}/{1}".format(uri, client_id),
                requires_modules=requires_modules, requires_version=requires_version, warnings=warnings)

    return isamAppliance.create_return_object(warnings=warnings)
