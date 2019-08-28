# Copyright 2019 by Kent Kawashima.  All rights reserved.

from collections import namedtuple, OrderedDict, Counter
import numpy as np

from .constants import GENETIC_CODE

# Creates an instance of Sequence object
Sequence = namedtuple('Sequence', ['name', 'description', 'sequence'])

# Read FASTA file into dictionary
def fasta_to_dict(path):
    name = ''
    desc = ''
    seq = ''
    d = OrderedDict()
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if seq:
                    d[name] = seq
                try:
                    name, desc = line[1:].split(maxsplit=2)
                except ValueError:
                    name = line[1:]
                seq = ''
            else:
                seq += line
        if seq:
            d[name] = seq
    return d

def fasta_to_seqobj_list(path):
    name = ''
    desc = ''
    seq = ''
    seq_list = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if seq:
                    seq_list.append(Sequence(name, desc, seq))
                try:
                    name, desc = line[1:].split(maxsplit=2)
                except ValueError:
                    name = line[1:]
                seq = ''
            else:
                seq += line
        if seq:
            seq_list.append(Sequence(name, desc, seq))
    return seq_list


# DNA -> amino acid
def translate_nucl_to_aa(nucl_seq):
    # Test if divisible by 3
    if len(nucl_seq) % 3 != 0:
        raise ValueError(f'Length of nucl_seq is not a multiple of 3: {len(nucl_seq)}')
    aa_list = [GENETIC_CODE[nucl_seq[i:i+3]]
               if nucl_seq[i:i+3] in GENETIC_CODE.keys() else 'X' # If not found amino acid is X
               for i in range(0, len(nucl_seq), 3)]
    return ''.join(aa_list)

def translate_fasta(nucl_path, aa_path):
    nucl_list = fasta_to_seqobj_list(nucl_path)
    aa_list = [
        Sequence(s.name, s.description, translate_nucl_to_aa(s.sequence))
        for s in nucl_list
    ]
    i = 0
    with open(aa_path, 'w') as f:
        for s in aa_list:
            if s.description:
                print(f'>{s.name} {s.description}', file=f)
            else:
                print(f'>{s.name}', file=f)
            print(s.sequence, file=f)
            i += 1
    return i
    
# Generate triplet
def codon_generator(nucl_seq):
    for j in range(0, len(nucl_seq), 3):
        if j+3 <= len(nucl_seq):
            yield nucl_seq[j:j+3]
