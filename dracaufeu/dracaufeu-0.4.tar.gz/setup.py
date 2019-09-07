from distutils.core import setup
from setuptools import setup, find_packages

setup(
  name = 'dracaufeu',
  packages = find_packages(),
  version = '0.4',
  license='MIT',
  description = 'Pytorch extension package for personal use',
  author = 'Etienne Meunier',
  author_email = 'etiennemeunier@live.fr',
  url = 'https://github.com/Etienne-Meunier/dracaufeu',
  download_url = 'https://github.com/Etienne-Meunier/dracaufeu/archive/v_04.tar.gz',
  keywords = ['Pytorch', 'DeepLearning'],
  install_requires=[],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
