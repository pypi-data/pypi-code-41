import logging
import os.path

logger = logging.getLogger(__name__)

uri = "/extensions"
requires_modules = None
requires_version = None


def get(isamAppliance, check_mode=False, force=False):
    """
    Retrieve installed extensions list
    """
    return isamAppliance.invoke_get("Retrieve installed extensions list",
                                    "{0}/".format(uri))


def add(isamAppliance, extension, config_data=None, third_party_package=None, check_mode=False, force=False):
    """
    Installing an Extension
    """

    return isamAppliance.invoke_post_files(
        "Installing an Extension",
        "{0}/inspect".format(uri),
        [
            {
                'file_formfield': 'extension_support_package',
                'filename': extension,
                'mimetype': 'application/file'
            }
        ],
        {},
        requires_modules=requires_modules, requires_version=requires_version
    )


def search(isamAppliance, name, check_mode=False, force=False):
    """
    Search for the extension
    """

    ret_obj = get(isamAppliance)

    for obj in ret_obj['data']:
        if obj['name'] == name:
            return obj

    return None
