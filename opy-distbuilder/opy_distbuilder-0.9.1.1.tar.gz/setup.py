import os
from setuptools import setup
import codecs

def read (*paths):
	with codecs.open (os.path.join (*paths), 'r', encoding = 'utf-8') as aFile:
		return aFile.read()

exec( open('opy/_version.py').read() ) 

setup (
	name = 'opy_distbuilder',
	version = __version__,  # @UndefinedVariable
	description = 'Python obfuscator for the "Distribution Builder" library.' +
				  ' An officially endorsed fork from the Opy master.',
	long_description = (
		read ('README.rst') + '\n\n' +
		read ('LICENSE')
	),
	keywords = ['opy', 'obfuscator', 'obfuscation', 'obfuscate', 'distbuilder'],
	url = 'https://github.com/QQuick/Opy/tree/opy_distbuilder',
	license = 'Apache 2',
	author = 'Jacques de Hooge, BuvinJ',
	author_email = 'buvintech@gmail.com',
	packages = ['opy'],	
	include_package_data = True,
	install_requires = ['six'],
	classifiers = [
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Operating System :: OS Independent',		
		'License :: Other/Proprietary License',
		'Intended Audience :: Developers',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Natural Language :: English',
		'Development Status :: 4 - Beta'		
	],
)
