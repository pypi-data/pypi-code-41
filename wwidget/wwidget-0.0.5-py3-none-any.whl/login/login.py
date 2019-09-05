from jinja2 import FileSystemLoader, Environment

loader = FileSystemLoader('src/widget/login/templates')
env = Environment(loader=loader)

"""
Login widget provides different types of login form.
See available lists of login form type
Usage: LoginWidget(template='a_login.html', method='<POST, GET>', action='<Target URL>')

"""
class LoginWidget(object):
  def __init__(self, **options):
    """
    Regiter login forma

    """
    self.__available_templates = ['a_login.html', 'b_login.html']
    if 'template' in options and options['template'] in self.__available_templates:
      # Todo: Define available dictionary
      # Warn if method is not valid
      self.__available_methods = ['POST', 'GET']
      if 'method' in options and options['method'] not in self.__available_methods:
        raise TypeError(f"Invalid form method for {options['method']}")
      
      tpl = env.get_template(options['template'])
      self.output = tpl.render(**options) 
    else:
      raise KeyError(f"No template name {options['template']}")
