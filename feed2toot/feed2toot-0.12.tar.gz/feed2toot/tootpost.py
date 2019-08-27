# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
# Copyright © 2015-2019 Carl Chenet <carl.chenet@ohmytux.com>
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

"""Checks an RSS feed and posts new entries to Mastodon."""

# 3rd party libraries imports
from mastodon import Mastodon

class TootPost:
    '''TootPost class'''

    def __init__(self, config, options, toot):
        '''Constructore of the TootPost class'''
        self.config = config
        self.options = options
        self.store = True
        self.toot = toot
        self.main()

    def main(self):
        '''Main of the TweetPost class'''
        mastodon = Mastodon(
            client_id=self.config.get('mastodon', 'client_credentials'),
            access_token=self.config.get('mastodon', 'user_credentials'),
            api_base_url=self.config.get('mastodon', 'instance_url')
        )
        toot_visibility = self.config.get('mastodon', 'toot_visibility', fallback='public')
        if 'custom' in self.options['media']:
            mediaid = mastodon.media_post(self.config['media']['custom'])
            mastodon.status_post(self.toot, media_ids=[mediaid], visibility=toot_visibility)
        else:
            mastodon.status_post(self.toot, visibility=toot_visibility)

    def storeit(self):
        '''Indicate if the tweet should be stored or not'''
        return self.store
