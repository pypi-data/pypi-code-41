from distutils.core import setup
setup(
  name = 'klelk',
  packages = ['klelk'],
  version = '0.1',
  license='MIT',
  description = 'KLELK CTF library',
  author = 'Lefnui',
  #author_email = 'your.email@domain.com',      # Type in your E-Mail
  url = 'https://github.com/Lefnui/klelk',
  download_url = 'https://github.com/Lefnui/klelk/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['CTF', 'crypto'],
  install_requires=[
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
