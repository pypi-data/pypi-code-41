''' Common Validator Code '''
import logging

LOG = logging.getLogger(__name__)


def failure(field_value, fmt, *args, **kwargs):
    ''' Print a Validation Failure Message '''
    level = kwargs.get('level', logging.INFO)
    LOG.log(level, "Invalid Value for field '%s' in node '%s': %s",
            field_value.name(), field_value.node.quick_scheme.path_str(),
            fmt % args)
    return False
