import os
from setuptools import find_packages, setup
 
# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='urllib3_fixed',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',  # example license
    description='A city selector for django xadmin',
    long_description="A xadmin city selector",
	long_description_content_type='text/markdown',
    url='https://www.example.com/',
    author='wp',
    author_email='wpsmoly@gmail.com',
    classifiers=[
       
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)