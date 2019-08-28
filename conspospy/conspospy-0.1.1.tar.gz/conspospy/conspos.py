# Copyright 2019 by Kent Kawashima.  All rights reserved.

import numpy as np

from .utils import codon_generator

def encode_seq_pos(seq_list):
    pos = 0
    gap_pos = -1
    pos_list = []
    for s in seq_list:
        gap_str = '-' * len(s)
        # Append -1 if gap, otherwise append position and increment
        if s == gap_str:
            pos_list.append(gap_pos)
            continue
        pos_list.append(pos)
        pos += 1
    return pos_list

# Represent an alignment as an array with position indices and -1 for gaps
def encode_codon_aln_pos(aln_d):
    pos_lists = []
    for key, seq in aln_d.items():
        nucl_seq = codon_generator(seq)
        pos_lists.append(encode_seq_pos(seq))
        
    # if seq_pos does not have the same lengths, numpy gives an error
    return np.array(pos_lists, dtype=np.int, order="F")
