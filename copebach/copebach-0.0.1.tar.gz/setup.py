from distutils.core import setup
setup(
	name = 'copebach',         # How you named your package folder (MyLib)
	packages = ['copebach'],   # Chose the same as "name"
	version = '0.0.1',      # Start with a small number and increase it with every change you make
	license='MIT',      # Chose a license from here: https://help.github.com/articles/licensing-a-repository
	description = 'shop client',   # Give a short description about your library
	author = 'kampretcode',                   # Type in your name
	author_email = 'manorder123@gmail.com',      # Type in your E-Mail
	url = 'https://github.com/Vaziria/copebach',   # Provide either the link to your github or to your website
	keywords = ['SOME', 'MEANINGFULL', 'KEYWORDS'],   # Keywords that define your package best
	classifiers=[
		'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
		'Intended Audience :: Developers',      # Define that your audience are developers
		'Topic :: Software Development :: Build Tools',
		'License :: OSI Approved :: MIT License',   # Again, pick a license
		'Programming Language :: Python :: 3.7'
	],
)