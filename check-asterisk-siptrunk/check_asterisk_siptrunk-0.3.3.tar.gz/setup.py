from setuptools import setup, find_packages

setup(name='check_asterisk_siptrunk',
      description='Nagios plugin to check status of a SIP Peer via the Asterisk Management Interface (AMI)',
      version='0.3.3',
      url='https://gitlab.com/spike77453/check_asterisk_siptrunk',
      author='Christian Schürmann',
      author_email='spike@fedoraproject.org',
      license='GNU GPLv2+',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Plugins',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: System :: Networking :: Monitoring',
      ],
      packages=find_packages(),
      install_requires=[
          'nagiosplugin>=1.2',
          'pyst2>=0.5.1',
      ],
      scripts=['bin/check_asterisk_siptrunk.py'],
)
