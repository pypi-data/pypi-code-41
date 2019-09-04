# Internal modules #
from pymarktex import Template

###############################################################################
class HeaderTemplate(Template):
    """All the parameters to be rendered in the LaTeX header template"""
    def title(self):       return self.options.get('title')
    def image_path(self):  return self.options.get('image_path').unix_style

###############################################################################
class FooterTemplate(Template):
    """All the parameters to be rendered in the LaTeX footer template"""
    pass