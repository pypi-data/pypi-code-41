from setuptools import setup

setup(name='apeeper',
	  version='0.3',
	  description='EC2 meta data service',
	  author='Thinkst Applied Research',
	  author_email='apeeper@thinkst.com',
	  packages=['apeeper'],
	  scripts=['bin/apeeperd','bin/apeeper_gunicorn_conf.py'],
	  install_requires=[
		  'python-iptables==0.13.0',
		  'gunicorn==19.9.0',
		  'Flask==1.0.2',
		  'requests==2.20.0',
		  'setproctitle==1.1.10'
	  ],
	  setup_requires=[
        'setuptools_git'
      ],
	  platforms='any',
	  license='GNU GPLv3',
	  include_package_data=True,
	  classifiers=[
        "Programming Language :: Python :: 2",
    ])
