from setuptools import setup

setup(name='setup-xedge-device',
      version='0.1.2',
      description='Command line to setup xedge-device',
      url='https://dev.azure.com/xompass/xompass-xedge/_git/xompass-xedge-device',
      author='Rodolfo Castillo Mateluna',
      author_email='rodolfo@xompass.com',
      install_requires=[
          'requests==2.22.0',
          'docker==4.0.2',
      ],
      scripts=['bin/setup-xedge-device'],
      zip_safe=False)
