import setuptools
import unittest

def my_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(start_dir='moleculekit', pattern='*.py')
    return test_suite

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

if __name__ == '__main__':
    with open('README.md', 'r') as fh:
        long_description = fh.read()

    setuptools.setup(
        name='moleculekit',
        version='0.1.24',
        author='Acellera',
        author_email='info@acellera.com',
        description='A molecule reading/writing and manipulation package.',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/acellera/moleculekit/',
        classifiers=[
            'Programming Language :: Python :: 3.6',
            'Operating System :: POSIX :: Linux',
        ],

        packages=setuptools.find_packages(include=['moleculekit*'], exclude=['test-data', '*test*', ]),

        package_data={
            'moleculekit': ['lib/*/*', 'vmd_wrapper', 'logging.ini'],
        },

        test_suite='setup.my_test_suite',
        install_requires=requirements
    )