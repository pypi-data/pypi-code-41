import os
from setuptools import setup

def read(fname):
		return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
		name = 'instagrump',
		packages = ['instagrump'],
		version = '1.2',
		license='MIT',
		description = 'Instagram public API wrapper',
		install_requires = ['requests', 'bs4'],
		author = 'Kelvin Ananda',
		author_email = 'ananda.kelvin@gmail.com',
		url = 'https://github.com/anandakelvin/instagrump', 
		keywords = ['Instagram', 'wrapper', 'public', 'API', 'scraping'],
		long_description=read('README.md'),
		long_description_content_type='text/markdown',
		classifiers=[
				"Development Status :: 5 - Production/Stable",
				"Topic :: Internet",
				"License :: OSI Approved :: MIT License",
		],
)