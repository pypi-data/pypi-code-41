import os
from setuptools import setup, find_packages

root_dir = os.path.dirname(os.path.abspath(__name__))


def package_dir(package_name):
    global root_dir
    __package_dir = os.path.join(root_dir, 'venv', 'Lib', 'site-packages')
    return os.path.join(__package_dir, package_name)


with open(os.path.join(root_dir, 'requirements.txt'), 'r') as f:
    # Put you dependencies in requirements.txt
    packages = [dependency for dependency in f.readlines()]


setup(
    name='sdkBraspag',
    version='0.0.2',
    author='Diego Faria',
    author_email='diego.rdfaria@gmail.com',
    packages=find_packages(),
    #package_dir={package: package_dir(package) for package in packages},
    description='Projeto de SDK para o Split de Pagamentos',
    long_description='Projeto de SDK para o Split de Pagamentos',
    url='',
    license='MIT',
    keywords='SDK Braspag Split',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ]

)