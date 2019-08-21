'''
Module to hold exceptions
'''

class ImageLoadException(Exception):
    '''Error when loading a picture'''
    pass

class MissingConfigException(Exception):
    '''Error when not all parameters are set properly'''
    pass
