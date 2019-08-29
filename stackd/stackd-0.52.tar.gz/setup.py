from distutils.core import setup
import setuptools
import sys
import site
from os import path
from setuptools.command.install import install
from subprocess import check_call
import logging

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger()


exec(open('stackd/version.py').read())

class PostInstallCommand(install):
  def run(self):

    setupCompletionScript = 'setup.completion-stackd.bash'
    systemScript = path.join(sys.prefix, 'bin', setupCompletionScript)
    userScript = path.join(site.getuserbase(), 'bin', setupCompletionScript)
    if path.isfile(systemScript):
      check_call([systemScript])
    elif path.isfile(userScript):
      check_call([systemScript])
    else:
      log.info("Unable to find setup.completion-stackd.bash at "+systemScript+" or "+userScript)
    install.run(self)

setup(
  name='stackd',
  version=__version__,
  description='STACKD - A docker swarm deploy helper according to environment',
  url='https://gitlab.com/youtopia.earth/bin/stackd',
  download_url='https://gitlab.com/youtopia.earth/bin/stackd/-/archive/master/stackd-master.tar.gz',
  keywords = ['docker', 'docker-stack', 'env'],
  author='Idetoile',
  author_email='idetoile@protonmail.com',
  license='MIT',
  packages=setuptools.find_packages(),
  cmdclass={
    'install': PostInstallCommand,
  },
  scripts=[
    'stackd/__main__.py',
    'bin/portainer-stack-up',
    'bin/docker-service-logs',
    'bin/docker-stack-volumes-cleanup',
    'bin/docker-stack-rm',
    'bin/completion-stackd.bash',
    'bin/setup.completion-stackd.bash',
  ],
  entry_points={
    'console_scripts': [
      'stackd = stackd.__main__:main'
    ]
  },
  install_requires=[
    'PyYAML',
    'wheel',
    'Jinja2'
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
  ],
)