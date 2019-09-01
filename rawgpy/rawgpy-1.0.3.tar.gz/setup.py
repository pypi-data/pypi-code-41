from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='rawgpy',
      version='1.0.3',
      description='RAWG.io python api wrapper',
      url='https://gitlab.com/laundmo/rawg-python-wrapper',
      author='laundmo',
      author_email='laurinschmidt2001@gmail.com',
      license='GPLv3',
      long_description=long_description,
      long_description_content_type="text/markdown",
      packages=['rawgpy', 'rawgpy.data_classes'],
      zip_safe=False,
          classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Operating System :: OS Independent",
      ],
      project_urls={
          'Documentation': 'https://rawgpy.readthedocs.io/en/latest/quickstart.html',
      })


# pip install -e .
# to install locally

# python setup.py sdist bdist_wheel
# twine upload dist/*
