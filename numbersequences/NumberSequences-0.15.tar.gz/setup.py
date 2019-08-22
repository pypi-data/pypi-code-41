from distutils.core import setup
import setuptools

with open('README.rst') as f:
    readme = f.read()

setup(
  name = 'NumberSequences',        
  packages = ['NumberSequences'],  
  version = '0.15',      
  license='MIT',        
  description = 'Tools for working with number sequences',   
  long_description = readme,
  long_description_content_type = 'text/markdown',
  author = 'Robbie Dee',                   
  author_email = 'admin@staticola.com',    
  url = 'https://pypi.org/project/NumberSequences/',   
  download_url = '',    
  keywords = ['MATH', 'NUMBERS', 'FUN'],   
  install_requires = [],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      
    'Topic :: Scientific/Engineering :: Mathematics',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',   
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
