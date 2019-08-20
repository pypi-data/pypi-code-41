from setuptools import find_packages, setup, Command

import sys
import uuid


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


ldclient_version='6.9.4'

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt')
test_reqs = parse_requirements('test-requirements.txt')
redis_reqs = parse_requirements('redis-requirements.txt')
consul_reqs = parse_requirements('consul-requirements.txt')
dynamodb_reqs = parse_requirements('dynamodb-requirements.txt')

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [ir for ir in install_reqs]
testreqs = [ir for ir in test_reqs]
redisreqs = [ir for ir in redis_reqs]
consulreqs = [ir for ir in consul_reqs]
dynamodbreqs = [ir for ir in dynamodb_reqs]


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        import subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

setup(
    name='launchdarkly-server-sdk',
    version=ldclient_version,
    author='LaunchDarkly',
    author_email='team@launchdarkly.com',
    packages=find_packages(),
    url='https://github.com/launchdarkly/python-server-sdk',
    description='LaunchDarkly SDK for Python',
    long_description='LaunchDarkly SDK for Python',
    install_requires=reqs,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
    ],
    extras_require={
        "redis": redisreqs,
        "consul": consulreqs,
        "dynamodb": dynamodbreqs
    },
    tests_require=testreqs,
    cmdclass={'test': PyTest},
)
