from setuptools import setup
from abadon_sdk import ABADON_SDK_VERSION


setup(
  name='abadon_sdk',
  version=ABADON_SDK_VERSION,
  description='Abadon SDK',
  long_description='Abadon SDK',
  python_requires='>=2.7',
  url='https://momenta.ai',
  author='MyronLu',
  author_email='myronlu1005@gmail.com',

  classifiers=[
    'Programming Language :: Python',
    'Programming Language :: Python :: Implementation',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development :: Libraries'
  ],
  keywords='Abadon SDK',

  packages=["abadon_sdk"],
)
