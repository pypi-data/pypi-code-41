from setuptools import setup, find_packages
from dotcontrol import __version__ as version


setup(
	name='dotcontrol',
	version=version,
	packages=find_packages(),
	install_requires=['Click', 'toml'],
	entry_points={
		'console_scripts': [
			'.c=dotcontrol.cli:cli'
		]
	}
)
