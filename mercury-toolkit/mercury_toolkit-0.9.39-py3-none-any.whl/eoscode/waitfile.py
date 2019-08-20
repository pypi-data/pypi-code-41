#!/usr/bin/env python

'''
Usage:
    waitfile <filename> --interval <interval_seconds> <command> [--max <max_triggers>] 
'''

import os, sys
import sh
import docopt
import time

def main(args):
    target_file = args['<filename>']
    wait_interval = int(args['<interval_seconds>'])
    command_string = args['<command>']
    max_triggers = -1
    if args['--max'] is True:
        max_triggers = int(args['<max_triggers>'])

    num_triggers = 0
    while True:
        if num_triggers == max_triggers:
            break

        time.sleep(wait_interval)
        if os.path.isfile(target_file):
            command = sh.Command(command_string)
            command()
            num_triggers += 1


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    main(args)