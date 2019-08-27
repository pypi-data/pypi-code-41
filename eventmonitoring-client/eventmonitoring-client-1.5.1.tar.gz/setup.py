from setuptools import setup, find_packages

setup(
    name='eventmonitoring-client',
    version='1.5.1',
    packages=find_packages(),
    install_requires = [
        'requests>=2.18.2',
        'django>=2.0.7',
        'zappa>=0.47.1'
    ],
)