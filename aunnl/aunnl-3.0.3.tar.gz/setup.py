from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
  name = 'aunnl',
  packages = ['aunnl'],
  version = '3.0.3',
  license='MIT',

  description = 'Another Unnecessary Neural Network Library',
  author = 'Aditya Radhakrishnan',
  author_email = 'adityaradk@gmail.com',
  long_description=long_description,
  long_description_content_type="text/markdown",
  url = 'https://github.com/adityaradk/aunnl',
  keywords = ['Deep Learning', 'Machine Learning', 'Artificial Neural Networks'],
  install_requires=[
          'numpy',
          'scipy',
      ],
)

# First, clear older versions from dist
# Then, run:
# python setup.py sdist bdist_wheel
# After the package is created, run the following command to upload:
# python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

# To update packagers and uploaders, run:
# python -m pip install --user --upgrade setuptools wheel
# python -m pip install --user --upgrade twine

# For more info, visit https://packaging.python.org/tutorials/packaging-projects/
