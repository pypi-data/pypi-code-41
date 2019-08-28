# Copyright 2019 by Kent Kawashima.  All rights reserved.

import os
import numpy as np
from .utils import fasta_to_seqobj_list
from .mafft import mafft_align_codons
from .conspos import encode_codon_aln_pos

def codon_mafft_conspos(
    nucl_path, aln_path, use_aln='einsi', aln_iterations=1000,
    consistent_marker='C', inconsistent_marker='N', 
    consistent_threshold=1.0, # every body has to have template pattern -> 1. Threshold for consistency
    marker_name='conspos_marker', marker_location=0,
    ):
    # Perform mafft alignment for global, local, and affine gap methods
    # This is for CDS
    # TODO: For introns change functions here to call mafft_ginsi_align, mafft_linsi_align and mafft_einsi_align.
    ginsi_aln_path = os.path.join(
        os.path.dirname(aln_path), os.path.basename(nucl_path) + '.ginsi.cod')
    linsi_aln_path = os.path.join(
        os.path.dirname(aln_path), os.path.basename(nucl_path) + '.linsi.cod')
    einsi_aln_path = os.path.join(
        os.path.dirname(aln_path), os.path.basename(nucl_path) + '.einsi.cod')

    mafft_align_codons(
        nucl_path, ginsi_aln_path + '.faa.aln', ginsi_aln_path + '.fna.aln',
        aln_method='ginsi', aln_iterations=aln_iterations)
    mafft_align_codons(
        nucl_path, linsi_aln_path + '.faa.aln', linsi_aln_path + '.fna.aln',
        translate=False, aln_method='linsi', aln_iterations=aln_iterations)
    mafft_align_codons(
        nucl_path, einsi_aln_path + '.faa.aln', einsi_aln_path + '.fna.aln',
        translate=False, aln_method='einsi', aln_iterations=aln_iterations)

    # Create position arrays for each alignment
    aln_list = {
        'ginsi': fasta_to_seqobj_list(ginsi_aln_path + '.fna.aln'),
        'linsi': fasta_to_seqobj_list(linsi_aln_path + '.fna.aln'),
        'einsi': fasta_to_seqobj_list(einsi_aln_path + '.fna.aln'),
    }
    aln_d = {
        'ginsi': {s.name: s.sequence for s in aln_list['ginsi']},
        'linsi': {s.name: s.sequence for s in aln_list['linsi']},
        'einsi': {s.name: s.sequence for s in aln_list['einsi']},
    }
    aln_array = {
        'ginsi': encode_codon_aln_pos(aln_d['ginsi']),
        'linsi': encode_codon_aln_pos(aln_d['linsi']),
        'einsi': encode_codon_aln_pos(aln_d['einsi']),
    }
    
    # Here we can break this function into two functinos.
    # input is array of aligments
    
    # Create the cospos marker sequence
    if use_aln not in aln_array.keys():
        raise ValueError(
            'Invalid alignment type. Select "ginsi", "linsi", or "einsi" '
            'for global, local, and affine-gap scoring alignemnt type respectively.'
        )
    template_array = aln_array[use_aln]
    # Initialize conspos marker as an array of zero with the same length as alignments
    conspos_array = np.zeros(template_array.shape[-1]) 
    for array in aln_array.values():
#         np.array([
#             [T, T, T, F],
#             [T, T, F, F],
#             [T, T, T, F]
#         ])
#         -> 
#         np.array([T, T, F, F]) by np.all(template_array == array, axis=0) # axis=0 is necessary
#         np.array([T, T, F, F]) ... np.array([1, 1, 0, 0]) is summed to conspos_array while looping
        conspos_array += np.all(template_array == array, axis=0)
    
    marker_seq = ''.join([
        consistent_marker 
        if v >= consistent_threshold*len(aln_array) else inconsistent_marker
        for v in conspos_array
    ])
    # Enhancement that can be done
#     if v == len() -> consistent
#     elif v > threshold and v < len() -> so so consistent
#     else inconsistent
     
    # Write to file
    with open(aln_path, 'w') as f:
        if marker_location not in [0, -1]:
            raise ValueError('Invalid marker_location. Set value to 0 to place the marker '
                             'at the beginning of the alignment '
                             'or -1 to place the marker at the end.')
        if marker_location == 0:
            print(f'>{marker_name}', file=f)
            print(f'{marker_seq}', file=f)
        for s in aln_list[use_aln]:
            if s.description:
                print(f'>{s.name} {s.description}', file=f)
            else:
                print(f'>{s.name}', file=f)
            print(f'{s.sequence}', file=f)
        if marker_location == -1:
            print(f'>{marker_name}', file=f)
            print(f'{marker_seq}', file=f)
    
    return fasta_to_seqobj_list(aln_path)

