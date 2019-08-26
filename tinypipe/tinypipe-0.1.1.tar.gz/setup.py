import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name='tinypipe',
  version='0.1.1',
  author='Siu-Kei Muk (David)',
  author_email='muksiukei@gmail.com',
  description='Lightweight pipeline with multi-threaded operation units.',
  long_description=long_description,
  long_description_content_type="text/markdown",
  url='https://github.com/dave-msk/tinypipe',
  packages=setuptools.find_packages(),
  download_url='https://github.com/dave-msk/tinypipe/archive/v0.1.1.tar.gz',
  keywords=['tinypipe', 'pipeline', 'multithread'],
  classifiers=[]
)
