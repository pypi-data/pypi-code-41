from distutils.core import setup
import setuptools

with open('README.md', encoding="utf-8") as f:
    long_description = f.read()

setup(
  name = 'deprint',
  packages = ['deprint'],
  version = '0.2',
  license='MIT',
  description = 'Declarative Python fancy print statement',
  long_description = long_description,
  long_description_content_type = "text/markdown",
  author = 'Wattanit Hotrakool',
  author_email = 'wattanit@protonmail.com',
  url = 'https://github.com/rorasa/deprint',
  download_url = 'https://github.com/rorasa/deprint/archive/v_02.tar.gz',
  keywords = ['declarative', 'print', 'fancy', 'color'],
  python_requires='>=3',
#   install_requires=[ 
#       ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)