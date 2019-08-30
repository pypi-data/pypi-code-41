"""
Run setup
"""

from setuptools import setup, find_packages
from predictor import __version__

setup(name='predictor',
      version=__version__,
      description='Serve up scikit-learn models for prediction',
      url='https://github.com/denver1117/predictor',
      download_url='https://pypi.org/project/predictor/#files',
      author='Evan Harris',
      author_email='emitchellh@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'flask>=0.12.2',
          'boto3>=1.4.0'
      ])
