import re
from setuptools import setup, find_packages

long_description = """
PDF conversion package
"""

# Retrieve version number
VERSIONFILE = "pdf/convert/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE))

setup(
    install_requires=[
        'PyMuPDF',
        'pdfconduit-modify>=2.2.2',
        'pdfconduit-transform>=1.2.1',
        'pdfconduit-utils>=1.1.1',
    ],
    name='pdfconduit-convert',
    version=verstr,
    packages=find_packages(),
    namespace_packages=['pdf'],
    include_package_data=True,
    url='https://github.com/mrstephenneal/pdfconduit',
    license='',
    author='Stephen Neal',
    author_email='stephen@stephenneal.net',
    description='PDF toolkit for preparing documents for distribution.',
    long_description=long_description,
)
