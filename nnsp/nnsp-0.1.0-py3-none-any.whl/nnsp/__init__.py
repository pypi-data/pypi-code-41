import pkg_resources

try:
    __version__ = pkg_resources.get_distribution('nnsp').version 
except Exeption:
    __version__ = '(not installed from setup.py)'
del pkg_resources 
    
