from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
  name = 'aunnl',
  packages = ['aunnl'],
  version = '3.0.2',
  license='MIT',

  description = 'Another unnecessary neural network library',
  author = 'Aditya Radhakrishnan',
  author_email = 'adityaradk@gmail.com',
  long_description=long_description,
  long_description_content_type="text/markdown",
  url = 'https://github.com/adityaradk/aunnl',
  keywords = ['DEEP LEARNING', 'MACHINE LEARNING', 'NEURAL NETWORK'],
  install_requires=[
          'numpy',
          'scipy',
      ],
)
