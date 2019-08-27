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

'''Build the message'''

# standard libraires imports
import logging

# external liraries imports
from bs4 import BeautifulSoup

# app libraries imports
from feed2toot.addtags import AddTags
from feed2toot.removeduplicates import RemoveDuplicates
from feed2toot.tootpost import TootPost

def build_message(entrytosend, tweetformat, rss):
    '''populate the rss dict with the new entry'''
    tweetwithnotag = tweetformat.format(**entrytosend)
    # remove duplicates from the final tweet
    dedup = RemoveDuplicates(tweetwithnotag)
    # only append hashtags if they exist
    # remove last tags if tweet too long
    if 'hashtags' in rss:
        addtag = AddTags(dedup.finaltweet, rss['hashtags'])
        finaltweet = addtag.finaltweet
    else:
        finaltweet = dedup.finaltweet

    # strip html tags
    finaltweet = BeautifulSoup(finaltweet, 'html.parser').get_text()
    return finaltweet

def send_message_dry_run(config, entrytosend, finaltweet):
    '''simulate sending message using dry run mode'''
    if entrytosend:
        logging.warning('Would toot with visibility "{visibility}": {toot}'.format(
            toot=finaltweet,
            visibility=config.get(
                'mastodon', 'toot_visibility',
                fallback='public')))
    else:
        logging.debug('This rss entry did not meet pattern criteria. Should have not been sent')

def send_message(config, clioptions, options, entrytosend, finaltweet, cache, rss):
    '''send message'''
    storeit = True
    if entrytosend and not clioptions.populate:
        logging.debug('Tooting with visibility "{visibility}": {toot}'.format(
            toot=finaltweet,
            visibility=config.get(
                'mastodon', 'toot_visibility',
                fallback='public')))
        twp = TootPost(config, options, finaltweet)
        storeit = twp.storeit()
    else:
        logging.debug('populating RSS entry {}'.format(rss['id']))
    # in both cas we store the id of the sent tweet
    if storeit:
        cache.append(rss['id'])
