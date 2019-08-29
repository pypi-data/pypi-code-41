# Copyright (C) 2019 Xiaoyong Guo - All Rights Reserved
# guoxiaoyong@guoxiaoyong.com
# guo.xiaoyong@gmail.com

import getopt
import logging
import sys


def read_text_file(filename, encoding):
    with open(filename, encoding=encoding) as infile:
        lines = infile.readlines()
    return lines


def write_text_file(filename, lines, encoding):
    with open(filename, 'w', encoding=encoding) as outfile:
        outfile.writelines(lines)


def convert_to_unix_line_break(lines):
    new_lines = [ln.rstrip() + '\n' for ln in lines]
    return new_lines


def convert_tab_to_space(lines, tabwidth=2):
    spaces = ' ' * tabwidth
    new_lines = [ln.replace('\t', spaces) for ln in lines]
    return new_lines


def convert(filename, config):
    lines = read_text_file(filename, encoding=config['src_encoding'])
    lines = convert_to_unix_line_break(lines)
    lines = convert_tab_to_space(lines, tabwidth=config['tabwidth'])
    write_text_file(filename, lines, encoding=config['dst_encoding'])


HELP_MSG = """
Usage: toutf8 files
  -t\t tabwidth, default value: 2
  -s\t source file encoding, default value: gbk
  -d\t destination file encoding, default value: utf8
  -h\t print help message.
"""

def print_help():
  print(HELP_MSG)


def translate_config(params):
    key_map = {
      '-t': 'tabwidth',
      '-s': 'src_encoding',
      '-d': 'dst_encoding',
      '-h': 'help',
    }
    config = {key_map[key]: val for key, val in params}
    config.setdefault('tabwidth', 2)
    config['tabwidth'] = int(config['tabwidth'])
    config.setdefault('src_encoding', 'gbk')
    config.setdefault('dst_encoding', 'utf8')
    return config


def main(argv=None):
    argv = argv or sys.argv
    try:
      params, files = getopt.gnu_getopt(argv[1:], 's:d:t:h')
      config = translate_config(params)
    except getopt.GetoptError:
      config = {'help': True}

    if config.get('help') is not None:
        print_help();
        return

    if not files:
        print('Please specify filenames.')
        return

    for filename in files:
        convert(filename,  config)
        logging.info('converted: %s', filename)


if __name__ == '__main__':
    logging.basicConfig(
        level='DEBUG',
        format='%(levelname)8s %(asctime)s %(name)s] %(message)s')
    main(sys.argv)
