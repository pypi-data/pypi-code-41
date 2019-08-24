from distutils.core import setup
setup(
  name = 'async_pytube',
  packages = ['async_pytube'],
  version = '1.0.1',
  license='MIT',
  description = 'pytube 9.5.1 but async',
  author = 'Andrew',
  author_email = 'asyncpytubelib@gmail.com',
  url = 'https://github.com/Andrebcd4/async_pytube',
  download_url = 'https://github.com/Andrebcd4/async_pytube/archive/1.0.1.tar.gz',
  keywords = ['pytube', 'asynchronous'],
  install_requires=[
          'aiohttp',
          'aiofiles',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.7'
  ],
)