from distutils.core import setup
from setuptools import find_packages

setup(
  name = 'graaf_tools',
  packages = find_packages(),
  version = '0.3.14',
  license='MIT',
  description = 'tools and code for research',
  author = 'Rafael Van Belle',
  author_email = 'rafael.vanbelle@gmail.com',
  url = 'https://github.com/raftie/graaf_tools',
  download_url = 'https://github.com/Raftie/graaf_tools/archive/v0.3.14.tar.gz',
  keywords = ['network'],
  install_requires=[
          'tqdm',
          'gensim',
          'networkx',
      ],
  classifiers=[
  ],
)
