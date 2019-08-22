"""
rstwatch: Watch directories for changes to .rst files and generate html

Usage:
    rstwatch [options] <directory>...

Options:
    --exit                  Exit after first pass, instead of repeat scanning
    --interval=SECONDS  Seconds to delay between directory scans [default: 2.0]
    --log-config=FILENAME   (Optional) Custom logging configuration file
    --refresh               Regenerate all html files on first scan
    --writer=WRITER_NAME    Docutils writer name. [default: html5]

For log configuration file format, see:
https://docs.python.org/3/library/logging.config.html#configuration-file-format
"""
import logging
import logging.config
import sys

import docopt

from .api import RSTWatch

log = logging.getLogger('rstwatch')


def main():
    args = docopt.docopt(__doc__)
    if args['--log-config']:
        logging.config.fileConfig(args['--log-config'])
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.INFO)
    try:
        interval = float(args['--interval'])
        directories = args['<directory>']
        watcher = RSTWatch(directories,
                           interval=interval,
                           writer=args['--writer'])
        watcher.run(refresh=args['--refresh'], one_time=args['--exit'])
    except KeyboardInterrupt:
        log.info("Stopped by Ctrl-C signal.")


if __name__ == '__main__':
    sys.exit(main())
