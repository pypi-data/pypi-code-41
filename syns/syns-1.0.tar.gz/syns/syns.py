#!/usr/bin/env python3
# Jan Fecht 2019
"""
Uses the openthesaurus API to access synonyms
Read more about the API at https://www.openthesaurus.de/about/api
"""
import requests
import argparse
import json
import sys

from pprint import pprint


API_URL="https://www.openthesaurus.de/synonyme/search"
VERSION="1.0"

class Search:
    """
    TODO:
      - following api options:
            substring
            substringFromResults
            substringMaxResults
            startswith
            supersynsets
            subsynsets
            baseform
      - add timeout for get request
    """

    def __init__(self, word, similar=True, max_results=0, verbose=False,
            superterms=True):
        self.word = word
        self.similar = similar
        self.max_results = max_results
        self.verbose = verbose
        self.result = None
        self.superterms=superterms

    def fetch_results(self):
        values = {
            "format":        "application/json",
            "q":             self.word,
            "similar":       str(self.similar).lower(),
            "supersynsets":  str(self.superterms).lower(),
                }
        try:
            r = requests.get(API_URL, params=values)
        except requests.ConnectionError:
            sys.stderr.write("Error fetching results\n")
            return False
        try:
            self.result = json.loads(r.text)
        except ValueError:
            sys.stderr.write("Got invalid result from server\n")
            return False
        return True

    def print_results(self, file=sys.stdout):
        if self.result is None:
            raise ValueError
        if self.similar:
            print("Did you mean {}?".format(", ".join(word['term'] for word in
                self.result['similarterms'])))
        sepchar = "\t" if self.superterms else ""
        for i,synset in enumerate(self.result['synsets']):
            if self.superterms:
                if len(synset['supersynsets']) > 0:
                    synset_name = synset['supersynsets'][0][0]['term']
                else:
                    synset_name = "Misc"
                print("{}:".format(synset_name), file=file)
            if self.verbose:
                lines=["{} - {}".format(word['term'], word['level']) if 'level' in word
                        else word['term']
                        for word in synset['terms']]
                print(sepchar + ("\n" + sepchar).join(lines))
            else:
                print(sepchar + ("\n" + sepchar).join(word['term'] for word in synset['terms']))
            if self.superterms and i != len(self.result['synsets']) - 1:
                print("")


def main():
    cli = argparse.ArgumentParser(description=__doc__, prog='Syns')
    cli.add_argument('word', metavar='WORD', type=str,
                    help='the word to find synonyms for')
    cli.add_argument('--similar', '-s', action='store_true',
                    help='Show similar terms')
    cli.add_argument('--hide-super', '-q', dest="super", action='store_true',
                    help='Whether to disable synonym grouping')
    cli.add_argument('--verbose', '-v', action='store_true',
                    help='Show more detailed information about the synonyms')
   ## cli.add_argument('--results', '-n', type=int, default=10,
   ##                 help='Maximum number of results (defaults to 10)')
    cli.add_argument('--version', action='version', version='%(prog)s \
            {}'.format(VERSION), help="Print current version")
    args = cli.parse_args()

    s = Search(args.word, similar=args.similar, max_results=0,
            verbose=args.verbose, superterms=(not args.super))
    ok = s.fetch_results()
    if ok:
        s.print_results()

if __name__ == "__main__":
    main()
