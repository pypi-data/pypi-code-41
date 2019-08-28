from distutils.core import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='WatsonReport',
    author="Kobe De Decker",
    author_email="kobededecker@gmail.com",
    description="watson reporting for imdc",
    version='0.0.8',
    packages=find_packages(),
    install_requires=['pandas', 'td-watson', 'openpyxl'],
    url="https://gitlab.com/kobededecker/watsonreport",
    entry_points="""
        [console_scripts]
        watsonreport=watsonReport.watsonReport:watsonReport
    """,
    license='MIT',
)