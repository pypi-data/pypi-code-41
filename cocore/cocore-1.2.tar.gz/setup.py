from distutils.core import setup

setup(
  name = 'cocore',
  packages = ['cocore'],
  version = 1.2,
  license='MIT',
  description = 'Core features of common code utility',
  author = 'Paul Singman',
  author_email = 'paul.singman@equinox.com',
  url = 'https://github.com/equinoxfitness/datacoco.core',
  download_url = f'https://github.com/equinoxfitness/datacoco.core/archive/0.9.tar.gz',
  keywords = ['helper', 'config', 'logging', 'common'],   # Keywords that define your package best
  install_requires=[
      'requests==2.20.0',
      'grequests==0.3.0',
      'future==0.16.0',
      'boto3==1.9.203'
    ]
)
