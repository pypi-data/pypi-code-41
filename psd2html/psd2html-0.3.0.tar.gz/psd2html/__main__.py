import argparse
import logging
import os

from psd2html import psd2html

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def main():
    logging.info('Starting conversion...')
    args = parse_args()
    if args:
        logging.info('Converting ' + args.input + ' to ' + args.output)
        psd2html(args.input, args.output)
    else:
        logger.info('Terminating...')


def parse_args():
    parser = argparse.ArgumentParser(description='Convert PSD file to HTML')

    parser.add_argument(
        'input', type=str, help='Input PSD file path')
    parser.add_argument(
        'output', type=str, nargs='?', default='',
        help='Output file or directory. When directory is specified, filename'
             ' is automatically inferred from input')

    args = parser.parse_args()
    prefix, ext = os.path.splitext(args.input)
    if ext != '.psd':
        logger.warning('File extension not supported.')
        return None
    args.output = generate_output_path(args)
    return args


def generate_output_path(args):
    prefix, ext = os.path.splitext(args.output)
    if ext.lower() != '.html':
        if not prefix:
            prefix, ext = os.path.splitext(args.input)
        if prefix.endswith('/'):
            filename, ext = os.path.splitext(args.input)
            prefix = prefix + filename
        return prefix + ".html"
    else:
        return args.output


if __name__ == '__main__':
    main()
