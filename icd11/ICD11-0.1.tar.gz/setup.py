from distutils.core import setup
setup(
  name = 'ICD11',         # How you named your package folder (MyLib)
  packages = ['ICD11'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='cc0-1.0',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'API wrapper for the WHO ICD11 API',   # Give a short description about your library
  author = 'Vladimir Guevara-Gonzalez',                   # Type in your name
  author_email = 'vlad2789@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/salviStudent/ICD11',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/salviStudent/ICD11/archive/v0.1.tar.gz',    # I explain this later on
  keywords = ['TEXTMINING', 'BIOMEDICAL', 'ICD11'],   # Keywords that define your package best
  install_requires=['requests'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',    # Again, pick a license    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
