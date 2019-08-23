#!/usr/bin/python3

# Copyright (c) 2016, Teriks
# All rights reserved.

# rightgif.py is part of giftoa

# giftoa is distributed under the following BSD 3-Clause License

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived 
#    from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import urllib.request
import urllib.parse
import urllib.error
import json
import sys
import os


__author__ = 'Teriks'
__copyright__ = 'Copyright (c) 2016 Teriks'
__license__ = 'Three Clause BSD'
__version__ = '1.0.1.1'



arg_parser = argparse.ArgumentParser(
    prog='rightgif',

    description=
    'A simple https://rightgif.com client, returns a URL to the "right gif" when given query text.  '
    'This program is part of giftoa, See: https://github.com/Teriks/giftoa',

    epilog=
    'The rightgif query text is the only accepted argument, it may be given with or without quotes.'
)


arg_parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))


arg_parser.add_argument('querytext', type=str, nargs='+',
                         help='The query text to use to find the right GIF, quotes are '
                              'not required when using spaces.')


def main():
    args = arg_parser.parse_args()


    query_text = " ".join(args.querytext)


    post_data = urllib.parse.urlencode({'text': query_text}).encode('utf-8')

    request = urllib.request.Request('https://rightgif.com/search/web', 
                                   data=urllib.parse.urlencode({'text': query_text}).encode('utf-8'), 
                                   headers={'User-Agent': 'Mozilla/5.0'})

    try:
        response=urllib.request.urlopen(request).read().decode('utf-8')
        json_response=json.loads(response)
    except urllib.error.URLError as e:
        print('Request Error: {reason}'.format(reason=e.reason), file=sys.stderr)
        exit(1)
    except ValueError as e:
        print('Error decoding JSON response: "{response}", Reason: "{reason}"'.format(response=response, reason=reason), file=sys.stderr)
        exit(1) 

    print(json_response["url"])


if __name__ == '__main__':
    sys.exit(main())
