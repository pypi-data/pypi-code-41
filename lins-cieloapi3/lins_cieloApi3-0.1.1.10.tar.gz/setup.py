from setuptools import find_packages
from distutils.core import setup

def get_version():
    return open('version.txt', 'r').read().strip()

setup(
    author='Halyson Sampaio',
    author_email='halyson@lojaspompeia.com.br',
    description='Pacote customizado da sdk python da cielo, https://github.com/DeveloperCielo/API-3.0-Python',
    license='MIT',
    name='lins_cieloApi3',
    packages=find_packages(),
    url='https://bitbucket.org/grupolinsferrao/pypck-lins-cieloapi3/',
    version=get_version(),
    zip_safe=False
)