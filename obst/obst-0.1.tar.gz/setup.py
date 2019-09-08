from distutils.core import setup
setup(
  name = 'obst',         # How you named your package folder (MyLib)
  packages = ['obst'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='GPL-3.0',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'a lightweight low performance lib to save metadata besides files and iterate through them',   # Give a short description about your library
  author = 'Alexander Rischka',                   # Type in your name
  author_email = 'alexander.rischka@t-online.de',      # Type in your E-Mail
  url = 'https://github.com/NineNein/obst',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/NineNein/obst/archive/v0.1.tar.gz',    # I explain this later on
  keywords = ['FILE', 'METADATA'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pandas',
          'fs',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',   # Again, pick a license
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)