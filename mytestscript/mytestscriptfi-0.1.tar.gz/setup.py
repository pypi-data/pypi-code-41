#!/usr/bin/env python333 
# coding=utf-8
from setuptools import setup, find_packages
setup(
	name='mytestscript',
	version='0.1',
	packages = find_packages(),
	author='halazi',
	author_email='3033263880@qq.com',
	url='https://github.com/tenlives/mytestscript',
	license='MIT',
	include_package_data=True,
	entry_points ={
		'console_scripts':[
			'mytestscript = demo.test:main',
		],
	},
	zip_safe=False,
	classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'Topic :: Database',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    	python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
)
