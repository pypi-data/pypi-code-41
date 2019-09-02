from distutils.core import setup
setup(
  name = 'centrySDK',         # How you named your package folder
  packages = ['centrySDK'],   # Chose the same as "name"
  version = 'v0.2.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Centry SDK for Python',   # Give a short description about your library
  author = 'Yerko Cuzmar',                   # Type in your name
  author_email = 'yerko.cuzmar@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/YerkoCuzmar/CentrySDK',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/YerkoCuzmar/CentrySDK/archive/v0.2.1.tar.gz',
  keywords = ['CENTRY', 'PYTHON', 'SDK'],   # Keywords that define your package best
  install_requires=['requests'
                    ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',    'License :: OSI Approved :: MIT License',   # Again, pick a license    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)