from setuptools import setup, find_packages


def get_requirements():
    with open("requirements.txt") as fp:
       return [line.strip() for line in fp if line]


setup(
    name='agentk',
    version='0.1.0',
    url='https://gitlab.com/kubic-ci/k',
    author='Yauhen Yakimovich',
    author_email='eugeny.yakimovitch@gmail.com',
    description='"AGENT" K is a complete minimalistic kubectl "doner"-wrap',
    packages=find_packages(),
    install_requires=get_requirements(),
    scripts=['k'],
)
