from setuptools import setup


setup(name='quwiki',
      version='0.0.1',
      description='Transform your Google Docs into a beautiful Wiki for your team.',
      platforms=['noarch'],
      license='Apache',
      packages=[
          'quwiki',
          'quwiki.sources',
      ],
      install_requires=[
          'google-api-python-client',
          'google-auth-httplib2',
          'google-auth-oauthlib',
          'pyyaml',
          'gitpython',
          'markdown',
          'beautifulsoup4',
          'python-slugify',
      ],
      scripts=[
          'bin/quwiki',
      ]
      )
