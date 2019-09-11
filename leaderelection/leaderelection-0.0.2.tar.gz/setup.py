import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
  name = 'leaderelection',
  packages = ['leaderelection'],
  version = '0.0.2',
  license = 'GPL3',
  description = 'Kubernetes leader election',
  long_description_content_type = 'text/markdown',
  long_description = README,
  author = 'Joel Damata',
  author_email = 'joel.damata94@gmail.com',
  url = 'https://github.com/jdamata',
  download_url = 'https://github.com/jdamata/k8s-leader-election-py/archive/0.0.2.tar.gz',
  keywords = ['Kubernetes', 'Controller', 'Leader', 'Election'],
  install_requires=[
          'kubernetes',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
  ],
)
