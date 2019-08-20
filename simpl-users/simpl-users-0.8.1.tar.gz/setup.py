import os

from setuptools import setup, find_packages


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    readme = f.read()

setup(
    name='simpl-users',
    version="0.8.1",
    description='simpl-users provides Simpl Users',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Jeff Triplett',
    author_email='jeff@revsys.com',
    url='https://github.com/simplworld/simpl-users',
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        "django-username-email==2.2.4",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
    ],
)
