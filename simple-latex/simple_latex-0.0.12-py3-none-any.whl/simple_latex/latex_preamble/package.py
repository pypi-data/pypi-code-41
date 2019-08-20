from .baseclass import PreambleBaseClass
from ..utils import transform_dict_to_kv_list

class Package(PreambleBaseClass):
    def __init__(self, package_name, options={}):
        super()
        if not isinstance(package_name, str) or not isinstance(options, dict):
            raise ValueError()

        self.package = package_name
        self.options = options

    def __repr__(self):
        if self.options:
            options_list = transform_dict_to_kv_list(self.options)
            return "\\usepackage[{}]{{{}}}\n".format(options_list, self.package)
        else:
            return "\\usepackage{{{}}}\n".format(self.package)
