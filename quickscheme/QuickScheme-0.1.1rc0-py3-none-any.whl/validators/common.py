''' Common Validator Code '''
import logging

LOG = logging.getLogger(__name__)


def failure(field_value, fmt, *args, level=logging.INFO):
    ''' Print a Validation Failure Message '''
    LOG.log(level, "Invalid Value for field '%s' in node '%s': %s",
            field_value.name(), field_value.node.quick_scheme.path_str(),
            fmt % args)
    return False
