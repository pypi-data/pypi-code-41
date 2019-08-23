"""
This is a python module provide reports of terraform plan
"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

dependencies = []
module_name = 'terraform-generate-report-plugin'
short_description = 'This is a python module provide reports ' \
                    'of terraform plan'

try:
    with open('DESCRIPTION.rst') as f:
        long_description = f.read()
except IOError:
    long_description = short_description


setup(
    name=module_name,
    version='0.0.1',
    url='https://github.com/ramitsurana/terraform-generate-report-plugin',
    license='MIT',
    author='Ramit Surana',
    author_email='ramitsurana@gmail.com',
    description=short_description,
    long_description=long_description,
    packages=['terraform-generate-report-plugin'],
    package_data={},
    platforms='any',
    install_requires=dependencies,
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
