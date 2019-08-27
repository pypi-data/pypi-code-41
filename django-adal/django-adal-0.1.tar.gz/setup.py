from setuptools import setup

setup(
    name='django-adal',
    version='0.1',
    packages=['django_adal'],
    url='https://github.com/GoVanguard/django_adal',
    license='GPL V3',
    author='Shane Scott',
    author_email='sscott@gvit.com',
    description='Very simple authentication module for python2 / django / Azur AD - Office365 using MS ADAL Lib. Forked from Lucterios2/django_auth_adal.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=["Django>=1.11.22", "adal>=1.2.0"],
)
