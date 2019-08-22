import io
import os
from setuptools import setup


# pip workaround
os.chdir(os.path.abspath(os.path.dirname(__file__)))


# Need to specify encoding for PY3, which has the worst unicode handling ever
with io.open('README.rst', encoding='utf-8') as fp:
    description = fp.read()
setup(name='reproserver',
      version='0.0',
      py_modules=['reproserver'],
      description="A web application reproducing ReproZip packages in the cloud",
      author="Remi Rampin",
      author_email='remirampin@gmail.com',
      maintainer="Remi Rampin",
      maintainer_email='remirampin@gmail.com',
      url='https://www.reprozip.org/',
      project_urls={
          'Homepage': 'https://gitlab.com/ViDA-NYU/reproserver',
          'Say Thanks': 'https://saythanks.io/to/remram44',
          'Source': 'https://gitlab.com/ViDA-NYU/reproserver',
          'Tracker': 'https://gitlab.com/ViDA-NYU/reproserver/issues',
      },
      long_description=description,
      license='BSD-3-Clause',
      keywords=['reprozip', 'reprounzip', 'docker', 'kubernetes',
                'reproducibility', 'reproducible-research', 'linux', 'science',
                'nyu'])
