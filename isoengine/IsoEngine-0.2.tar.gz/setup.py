from distutils.core import setup
setup(
  name = 'IsoEngine',         # How you named your package folder (MyLib)
  packages = ['IsoEngine'],   # Chose the same as "name"
  version = '0.2',      # Start with a small number and increase it with every change you make
  license='gpl-3.0',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'IsoEngine is a Library that makes Isometric game programming in python easy',   # Give a short description about your library
  author = 'Thijs Boersma',                   # Type in your name
  author_email = 'thijs@kabelbw.de',      # Type in your E-Mail
  url = 'https://github.com/starminer99/isoengine',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/StarMiner99/IsoEngine/archive/0.2.tar.gz',    # I explain this later on
  keywords = ['Engine', 'Isometric', 'game'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pygame',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
