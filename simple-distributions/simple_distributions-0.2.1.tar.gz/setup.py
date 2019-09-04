from setuptools import setup

# read the contents of the README file
from os import path
package_folder = 'simple_distributions'
this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, package_folder, 'README.md'), 
    encoding='utf-8') as f:
    long_description = f.read()


setup(name='simple_distributions',
      version='0.2.1',
      description="A package for calculating probability density functions of common statistical distributions using numerical data and visualizing the results.",
      packages=['simple_distributions'],
      author = 'Dave Rench McCauley',
      author_email = 'drench56@gmail.com',
      long_description=long_description,
      long_description_content_type='text/markdown',
      zip_safe=False)