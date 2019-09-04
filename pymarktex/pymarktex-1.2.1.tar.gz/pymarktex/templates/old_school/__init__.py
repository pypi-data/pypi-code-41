# Internal modules #
from pymarktex import Template

###############################################################################
class HeaderTemplate(Template):
    """All the parameters to be rendered in the LaTeX header template"""
    def name(self):        return self.options.get('name')
    def status(self):      return self.options.get('status')
    def company(self):     return self.options.get('company')
    def subcompany(self):  return self.options.get('subcompany')
    def title(self):       return self.options.get('title')
    def image_left(self):  return self.options.get('image_left').unix_style
    def image_right(self): return self.options.get('image_right').unix_style

###############################################################################
class FooterTemplate(Template):
    """All the parameters to be rendered in the LaTeX footer template"""
    pass