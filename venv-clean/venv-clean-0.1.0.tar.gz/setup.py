import os
import codecs
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


def read(*folders):
    with codecs.open(os.path.join(here, *folders), encoding='utf-8') as f:
        return f.read()


def get_requirements(file_name):
    requires_file = read('requirements', file_name)
    return requires_file.splitlines()


long_description = read('README.rst')

setup(
    name='venv-clean',
    version='0.1.0',
    description='Finds python virtual environments in your machine. '
                'Displays disk usage and other data, and allows you '
                'to delete them.',
    long_description=long_description,
    url='https://github.com/jcapona/venv-clean',
    author='Jorge Capona',
    author_email='jcapona@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: System',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='python venv virtual environment env manage',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=get_requirements('app_reqs.txt'),
    test_suite='tests',
    setup_requires=get_requirements('test_reqs.txt'),
    extras_require={},
    package_data={},
    data_files=[],
    entry_points={
            'console_scripts': [
                'venv-clean = venv_clean.__main__:main'
            ]
        }
)
