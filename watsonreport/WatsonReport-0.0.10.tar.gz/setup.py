from distutils.core import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("version", "r") as vh:
    version = vh.read()

setup(
    name='WatsonReport',
    author="Kobe De Decker",
    author_email="kobededecker@gmail.com",
    description="watson reporting for imdc",
    version=version,
    packages=find_packages(),
    install_requires=['pandas', 'td-watson', 'openpyxl'],
    url="https://gitlab.com/kobededecker/watsonreport",
    entry_points="""
        [console_scripts]
        watsonreport=watsonReport.watsonReport:watsonReport
    """,
    license='MIT',
)