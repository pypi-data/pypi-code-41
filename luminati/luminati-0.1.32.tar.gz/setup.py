from distutils.core import setup
import os
long_description=open("luminati/README.md").read()
setup(
  name = 'luminati',         # How you named your package folder (MyLib)
  packages = ['luminati'],   # Chose the same as "name"
  package_data={
    'luminati': ['*.hy',"*.json","*.md"]
  },
  version = '0.1.32',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Luminati proxy done easy',   # Give a short description about your library
  long_description=long_description,
  long_description_content_type='text/markdown',
  author = 'ShinSheel',                   # Type in your name
  author_email = 'wladgavrilov@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/user/reponame',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['luminati', 'proxy', 'third party'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'requests',
          
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package

    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',

    'License :: OSI Approved :: MIT License',   # Again, pick a license

    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
