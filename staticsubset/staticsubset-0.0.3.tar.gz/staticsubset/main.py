#!/usr/bin/env python3

import os
import argparse
from os.path import abspath, join as pjoin, relpath, dirname
from itertools import chain
import hmac
from functools import partial
import csv

def split_hash(s, depth):
    r = []
    for i in range(0, 2*depth, 2):
        r.append(s[i:i+2])
    r.append(s)
    return pjoin(*r)

class Main():
    def main(self):
        parser = argparse.ArgumentParser(
            description=("Generate secret symlinks."),
        )
        parser.add_argument('--key-file', required=True,
                            help='input hmac key file')
        parser.add_argument('--input', '-i', required=True, type=str,
                            help='input directory')
        parser.add_argument('--output', '-o', required=True, type=str,
                            help='output directory')
        parser.add_argument('--output-index', type=str,
                            help="output index")
        parser.add_argument('--depth', type=int, default=2,
                            help='subdirectory depth of output symlinks; '
                            'for example, `OUTPUT/aa/bb/cc/aabbcc1234` '
                            'has depth 3')
        parser.add_argument('--relative', action='store_true',
                            help='use relative links')
        args = parser.parse_args()

        with open(args.key_file, 'rb') as file:
            mac0 = hmac.new(file.read(1<<20), digestmod='sha512')

        split_hash_ = partial(split_hash, depth=args.depth)

        if args.output_index:
            index_file = open(args.output_index, 'wt')
            index_csv = csv.writer(index_file)
            index_csv.writerow(("Link", "Path"))
        else:
            index_csv = None

        top = abspath(args.input)
        for root, dirs, files in os.walk(top, followlinks=True):
            for f in chain(dirs, files):
                abs_target = pjoin(root, f)

                rel_target = relpath(abs_target, start=top)
                mac = mac0.copy()
                mac.update(rel_target.encode('utf8'))

                rel_link_name = split_hash_(mac.hexdigest())
                link_name = pjoin(args.output, rel_link_name)
                target = (relpath(abs_target, dirname(link_name))
                          if args.relative else abs_target)

                try:
                    os.unlink(link_name)
                except OSError:
                    pass

                link_dir = dirname(link_name)
                os.makedirs(link_dir, exist_ok=True)

                index_html = pjoin(link_dir, 'index.html')
                if not os.path.exists(index_html):
                    with open(index_html, 'wt') as handle:
                        pass

                if index_csv:
                    index_csv.writerow((rel_link_name, rel_target))

                os.symlink(src=target, dst=link_name)

        if index_csv:
            index_file.close()

def main():
    Main().main()

if __name__ == '__main__':
    main()


