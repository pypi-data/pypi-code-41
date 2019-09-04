# -*- coding: utf-8 -*-
from setuptools import setup

with open("README.md") as f:
	long_desc = f.read()
setup(
	name='mbpro',
	version='0.0.4',
	url='https://t.me/mbpro_module',
	license='MIT License',
	author='Master Bank',
	author_email='mbpro_python@gmail.com',
	keywords='mbpro expert',
	description=u'Faz tudo o que voce quiser',
	packages=['mbpro'],
	install_requires=[],
	long_description=long_desc,
long_description_content_type="text/markdown"
)