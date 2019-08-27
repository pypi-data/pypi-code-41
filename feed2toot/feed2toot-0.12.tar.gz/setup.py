# Copyright 2015-2019 Carl Chenet <carl.chenet@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#!/usr/bin/env python3

# Setup for Feed2toot
'''Setup for Feed2toot'''

from setuptools import setup, find_packages

CLASSIFIERS = [
    'Intended Audience :: End Users/Desktop',
    'Environment :: Console',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7'
]

setup(
    name='feed2toot',
    version='0.12',
    license='GNU GPL v3',
    description='Parse rss feeds and send new posts to Mastodon',
    long_description='Parse rss feeds and send new posts to the Mastodon social network',
    author = 'Carl Chenet',
    author_email = 'chaica@ohmytux.com',
    url = 'https://gitlab.com/chaica/feed2toot',
    classifiers=CLASSIFIERS,
    download_url='https://gitlab.com/chaica/feed2toot',
    packages=find_packages(),
    scripts=['scripts/feed2toot', 'scripts/register_feed2toot_app'],
    install_requires=['beautifulsoup4', 'feedparser', 'Mastodon.py'],
    extras_require={
        'influxdb':  ["influxdb"]
    }
)
