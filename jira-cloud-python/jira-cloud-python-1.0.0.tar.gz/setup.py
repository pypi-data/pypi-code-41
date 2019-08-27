import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='jira-cloud-python',
      version='1.0.0',
      description='API wrapper for Jira Cloud written in Python',
      long_description=read('README.md'),
      long_description_content_type="text/markdown",
      url='https://github.com/ingmferrer/jira-cloud-python',
      author='Miguel Ferrer',
      author_email='ingferrermiguel@gmail.com',
      license='MIT',
      packages=['jiracloud'],
      zip_safe=False)
