from setuptools import setup

setup(
    name='torrent-client',    # This is the name of your PyPI-package.
    version='1.2',
    packages=['torrent_client', 'torrent_client/algorithms', 'torrent_client/control', 'torrent_client/network', 'torrent_client/network/tracker_clients'],                          # Update the version number for new releases
    scripts=['torrent_cli.py'],
    author='OpenWorm.org authors and contributors',
    author_email='jaideepnseth@gmail.com',
    description='A Python BitTorrent client for downloading from torrents. ',
    long_description='This is the component for downloading contents described by a DataSource torrent_file_informational',                # The name of your scipt, and also the command you'll be using for calling it
    install_requires=[
            'async-timeout==2.0.0',
            'bencodepy==0.9.5',
            'bitarray==0.8.1',
            'chardet==3.0.4',
            'multidict==3.3.2',
            'sip',
            'yarl==0.14.2',
            'aiohttp==2.3.3',
        ]
)
