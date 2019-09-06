from distutils.core import setup
setup(
  name = 'bullet_journal',
  packages = ['bullet_journal'],
  version = '0.1',
  license='MIT',
  description = 'Tools to make bullet journaling simple and easy',
  author = 'Pinxiu Gong',
  author_email = 'pinxiu.gong@gmail.com',
  url = 'https://github.com/pinxiu/bullet_journal',
  download_url = 'https://github.com/pinxiu/bullet_journal/archive/v_01.tar.gz',
  keywords = ['bullet', 'journal', 'tool', 'command line'],
  install_requires=[
          'validators',
          'beautifulsoup4',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)
