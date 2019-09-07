from setuptools import setup, find_packages


setup(
    name='agentk',
    version='0.1.1',
    url='https://gitlab.com/kubic-ci/k',
    author='Yauhen Yakimovich',
    author_email='eugeny.yakimovitch@gmail.com',
    description='"AGENT" K is a complete minimalistic kubectl "doner"-wrap',
    packages=find_packages(),
    install_requires=['sh>=1.12.13', 'pick>=0.6.4', 'clint>=0.5.1', 'ruamel-yaml>=0.15.35'],
    scripts=['k'],
)
