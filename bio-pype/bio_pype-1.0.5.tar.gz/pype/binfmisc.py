import re
from itertools import count
from pype.misc import xopen

def fastq(f, n = -1):
    for i in  count():
        if i == n:
            break
        else:
            try:
                name = next(f).strip()
                read = next(f).strip()
                sep = next(f).strip()
                qual = next(f).strip()
                yield {'name': name, 'seq': read,
                       'qual': qual}
            except EOFError:
                break

def fastq_header_regex(regex_list_file=None):
    header = dict()
    if regex_list_file is None:        
        ##Default regexs##
        #standard illumina
        machine = '^@([A-Za-z0-9]+:[A-Za-z0-9]+)'
        flowcell = '([A-Za-z0-9-]+)'
        index = '([A-Z0-9+]+)$'
        lane = '([1-2])'
        sep = '.*?'
        any = '\\w+'
        alphanum = '[A-Z0-9]+'
        regex = []
        regex = (machine, sep, flowcell, sep, any, sep, any, sep, any, sep,
                 any, sep, lane, sep, alphanum, sep, any, sep, index)
        regex = re.compile(''.join(map(str, regex)))
        header['Illumina1'] = {'regex': regex, 'platform': 'Illumina'}
    else:
        #read regex from file
        with xopen(regex_list_file,'rt') as f:
            i = 0
            for line in f:
                platform, expression = line.strip().split('\t')                
                header['ID%i' % i] = {'regex': re.compile(expression), 'platform': platform}
                i += 1
    return header


def read_fastq_tag(fastq_file, header_regex, nlines=50000):
    headers = {'platform': dict(),
               'machine': dict(), 'flowcell': dict(),
               'lane': dict(), 'index': dict()}
    #Read and store first n headers, n=nlines
    with xopen(fastq_file,'rt') as f:
        fastq_iter = fastq(f, nlines)
        for i in fastq_iter:
            read_name = i['name']
            for rx in header_regex.keys():
                regex_i = header_regex[rx]
                m = regex_i['regex'].match(read_name)
                if m:
                    machine, flowcell, lane, index = m.groups()
                    headers = pair_tag_keys(headers, 'machine', machine)
                    headers = pair_tag_keys(headers, 'flowcell', flowcell)
                    headers = pair_tag_keys(headers, 'lane', lane)
                    headers = pair_tag_keys(headers, 'index', index)
                    headers = pair_tag_keys(headers, 'platform', regex_i['platform'])
                    break
    return headers


def pair_tag_keys(x, key, value):
    if value in x[key].keys():
        x[key][value] += 1
    else:
        x[key][value] = 1
    return x
