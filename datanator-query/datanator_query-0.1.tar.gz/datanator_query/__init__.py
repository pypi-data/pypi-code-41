from . import *
import pkg_resources

# read version
with open(pkg_resources.resource_filename('datanator_query', 'VERSION'), 'r') as file:
    __version__ = file.read().strip()