#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
		name="bumprevision-1",
		version="0.1.28",  # REV-CONSTANT:rev 5d022db7d38f580a850cd995e26a6c2f
		description='Bump revision utility',
		packages=['bumprevision', 'bumprevision.vcshelper'],
		entry_points={
				'console_scripts': ['bumprevision-1 = bumprevision.bump:main', ],
		},
		classifiers=[
				"Development Status :: 5 - Production/Stable",
				"Intended Audience :: Developers",
				"License :: OSI Approved :: MIT License",
				"Operating System :: POSIX",
				"Programming Language :: Python :: 2.7",
				"Programming Language :: Python :: 3.7",
		],
		license="MIT License",
)
