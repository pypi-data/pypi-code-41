import argparse

import calusern

parser = argparse.ArgumentParser(description='Generate the HTML site from sources.')
parser.add_argument('--site_root', default='')

args = parser.parse_args()
site_root = args.site_root
gen = calusern.Generator('./data', 'public', site_root)
gen.run()
