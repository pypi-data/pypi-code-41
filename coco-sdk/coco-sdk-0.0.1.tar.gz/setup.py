import os

from setuptools import setup
from setuptools import find_packages

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()

long_description = read("README.md")

setup(name='coco-sdk',
      version='0.0.1',
      description='CoCo(Conversational Components) SDK for building modular chatbots',
      long_description=long_description,
      author='Chen Buskilla',
      author_email='chen@buskilla.com',
      url='https://github.com/conversationalcomponents/coco-sdk-py',
      license='MIT',
      install_requires=['requests'],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.7',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      packages=find_packages(),
      python_requires=">=3.7"
)
