#/usr/bin/env python
# coding: utf8
from setuptools import setup, find_packages
from xserver import version

setup(
    name='xserver',
    version=version,
    description='xserver for deploying',
    author='Hepochen',
    author_email='hepochen@gmail.com',
    include_package_data=True,
    packages=find_packages(),

    install_requires = [
        'psutil',
        'netifaces', # ==0.10.7
        'python-crontab==2.3.4',
        'setuptools>=40.0.0',
        'pycrypto==2.6.1',
        #'fabric==1.10.1', # arm 系统上不支持，需要手工安装
        #'farbox_bucket',
        # for cryptography starts
        #'cryptography', # ==2.3
        #'setuptools>=40.0.0',
        #'ipaddress',
        #'enum34',
        # for cryptography ends
    ],

    entry_points={
        'console_scripts':[
            # for server
            'xserver = xserver.server.console:main',

            # xserver_build mongodb
            # xserver_build mongodb --version=3.4.5
            # xserver_build demo
            # xserver_build demo --version=0.0.2 --old_version=0.0.1 --update  "cmd1" "cmd2"
            # xserver_build pyweb --version=201908
            # xserver_build pyweb --version=2019 --update "RUN pip install farbox_bucket==40.0.0"
            # xserver_build farbox_bucket --version=latest --update "RUN pip install farbox_bucket==0.1499"
            # .etc
            'xserver_build = xserver.docker_image.console:main',

            # for server status
            'xserver_status = xserver.server_status.console:main',

            # for client
            #'xserver_client_restart = xserver.scripts.client.restart:main',

            # helpers
            'xserver_package = xserver.helper.console.package:main',
            'xserver_iptables = xserver.helper.console.iptables:main',


        ]
    },

    platforms = 'linux',
)