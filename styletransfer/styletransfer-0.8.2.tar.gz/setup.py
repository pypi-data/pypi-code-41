import pathlib
import os
from setuptools import setup, find_packages
from setuptools.command.easy_install import easy_install
from distutils.util import convert_path

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

#Load the meta data from the module to have one source for the version and other data
meta = {}
aboutPath = convert_path('styletransfer/__about__.py')
with open(aboutPath) as aboutFile:
    exec(aboutFile.read(), meta)

#Load the requirements form the file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

#Inject the install option for PyTorch
normal_run_setup_fn = easy_install.run_setup
def setup_hook(self, setup_script, setup_base, args):
    #Only trigger for torch or torchvision and if running on Windows
    if setup_script.find('/torch') > -1 and setup_script.endswith('setup.py') and os.name == 'nt':
        args.insert(0,'--install-option="-f https://download.pytorch.org/whl/torch_stable.html"')
    normal_run_setup_fn(self, setup_script, setup_base, args)
easy_install.run_setup = setup_hook

setup(
    name=meta['__title__'],
    version=meta['__version__'],
    description=meta['__summary__'],
    author=meta['__author__'],
    author_email=meta['__email__'],
    license=meta['__license__'],
    long_description=README,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=("tests",)),
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False
)
