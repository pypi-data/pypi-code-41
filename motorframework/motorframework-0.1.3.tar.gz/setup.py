from distutils.core import setup
setup(
  name = 'motorframework',
  packages = ['motorframework'], 
  version = '0.1.3',
  license='MIT',
  description = 'Motor Framework', 
  url = 'https://github.com/super-mario-x/motorframework',
  download_url = 'https://github.com/super-mario-x/motorframework/archive/v0.1.3.tar.gz',
  keywords = ['motor', 'framework', 'motorframework'],
  install_requires=[
          'validators',
          'robotframework',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.6',
  ],
)