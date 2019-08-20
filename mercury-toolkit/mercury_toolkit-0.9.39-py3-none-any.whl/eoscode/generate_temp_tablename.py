#!/usr/bin/env python

'''
Usage:
    generate_temp_tablename [--prefix=<prefix>]
'''

import uuid
import datetime
import docopt


def main(args):
    prefix = ''
    if args['--prefix'] is not None:
        prefix = args['--prefix']
    base_name = str(uuid.uuid4()).replace('-', '_')
    print('%s%s' % (prefix, base_name))


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    main(args)