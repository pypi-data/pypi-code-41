import pandas as pd
import pkg_resources

def _load_from_resource(resource_path):
    return pd.read_csv(pkg_resources.resource_filename(__name__,resource_path))

def _return_file(string):
    resource_path = '/'.join(('data',string + '.zip'))
    return _load_from_resource(resource_path)

def load_movies():
    return _return_file('movies')

def load_bond():
    return _return_file('bond')

def load_gapminder():
    return _return_file('gapminder')

def load_beauty():
    return _return_file('beauty')

def load_volcano_db():
    return _return_file('volcano_db')

def load_volcano():
    return _return_file('volcano')
