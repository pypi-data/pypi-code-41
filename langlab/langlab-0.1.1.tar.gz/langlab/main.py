import pyloco

class LangLab(pyloco.Manager):
    _name_ = "langlab"
    _version_ = "0.1.1"
    _description_ = "Programming Language Laboratory"
    _long_description_ = """langlab : A base package for multiple programming language research tools.
"""
    _author_='Youngsung Kim'
    _author_email_ ='grnydawn@gmail.com'
    _license_ ='MIT'
    _url_='https://github.com/grnydawn/langlab'
    pyloco.Manager.load_default_task("buildapp.py", "runapp.py", "cleanapp.py")
