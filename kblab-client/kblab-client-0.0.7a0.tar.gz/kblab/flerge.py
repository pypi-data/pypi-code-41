#!/usr/bin/env python3

from sys import argv,exit
from json import load,dumps
from copy import copy,deepcopy

levels = [ 'Issue', 'Monograph', 'Part', 'Page', 'Area', 'Text' ]


def aggregate(structure, content, environment):
    ret = copy(environment)
    ret_content = []

    stack = [ structure ]
    while len(stack) > 0:
        element = stack.pop(0)

        for x in element if isinstance(element, list) else [ element ]:
            if x.get('@id', '') in content and content[x['@id']].get('content', '') != '':
                ret_content += [ content[x['@id']].get('content', '') ]

            if 'has_part' in x:
                stack.insert(0, x['has_part'])

    ret['content'] = ret_content

    return ret


def flerge(structure, content, meta, level='Text', ignore = []):
    ret = []
    ignore += [ 'has_part', 'content' ]

    stack = [ (deepcopy(meta), element) for element in structure ]
    while len(stack) != 0:
        environment,element = stack.pop(0)
        nenviron = copy(environment)
        nenviron.update({ key:value for key,value in element.items() if key not in ignore })        

        if element.get('@type', None) == level:
            ret += [ aggregate(element, content, nenviron) ]
        elif 'has_part' in element:
            for x in element['has_part'][::-1]:
                stack.insert(0, (nenviron, x))

    return ret

if __name__ == '__main__':
    if len(argv) < 4 or len(argv) > 6:
        print(f'usage: {argv[0]} <structure-file> <content-file> <meta-file> [level] [ignore]')
        exit(1)

    level = argv[4] if len(argv) > 4 else 'Text'
    ignore = argv[5].split(',') if len(argv) > 5 else []

    with open(argv[1], mode='rb') as sfile, open(argv[2], mode='rb') as cfile, open(argv[3], mode='rb') as mfile:
        structure = load(sfile)
        content = { x['@id']:x for x in load(cfile) }
        meta = load(mfile)

        print(dumps(flerge(structure, content, meta, level, ignore), indent=2))

