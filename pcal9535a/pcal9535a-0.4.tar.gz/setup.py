from distutils.core import setup
setup(
  name = 'pcal9535a',
  packages = ['pcal9535a'],
  version = '0.4',
  license='MIT',
  description = 'A library to control NXP PCAL9535A GPIO expander',
  author = 'Denis Shulyaka',
  author_email = 'Shulyaka@gmail.com',
  url = 'https://github.com/Shulyaka/pcal9535a',
  download_url = 'https://github.com/Shulyaka/pcal9535a/archive/v0.4.tar.gz',
  keywords = ['PCAL9535A', 'I2C', 'GPIO', 'DIY'],
  install_requires=[
          'smbus-cffi',
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
