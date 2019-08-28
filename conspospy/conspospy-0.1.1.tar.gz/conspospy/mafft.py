# Copyright 2019 by Kent Kawashima.  All rights reserved.

import os
import logging
import subprocess as proc

from .utils import fasta_to_seqobj_list, fasta_to_dict, Sequence, \
    translate_fasta, codon_generator
from .constants import GENETIC_CODE

# To call mafft
def mafft_align(infile, output_aln, iterations=1000, mafft_path='mafft', method='genafpair'):
    c = proc.run(
        f'{mafft_path} --{method} --maxiterate {iterations} '
        f'"{infile}" > "{output_aln}"',
        shell=True)
    return c

# For introns we can just use these three functions
# Global
def mafft_ginsi_align(infile, output_aln, iterations=1000, mafft_path='mafft'): 
    return mafft_align(
        infile, output_aln, iterations=iterations, mafft_path=mafft_path, method='globalpair')

# Local
def mafft_linsi_align(infile, output_aln, iterations=1000, mafft_path='mafft'):
    return mafft_align(
        infile, output_aln, iterations=iterations, mafft_path=mafft_path, method='localpair')

# Affine-gap
def mafft_einsi_align(infile, output_aln, iterations=1000, mafft_path='mafft'): 
    return mafft_align(
        infile, output_aln, iterations=iterations, mafft_path=mafft_path, method='genafpair')

# Position codons based on amino acid alignment and original nucleotide sequences
def align_codons_by_aa(nucl_path, aa_aln_path):
    nucl_list = fasta_to_seqobj_list(nucl_path)
    codon_aln_lst = []
    
    # Assume the order of items in nucleotide and amino acid sequences are the same.
    for i, aa_seq in enumerate(fasta_to_dict(aa_aln_path).values()): # Loop amino acid alignment read into dictionary
        nucl_seq = str(nucl_list[i].sequence) # Retrieve nucleotide sequence from Sequence object
        codon = codon_generator(nucl_seq) # Get gerator object
        try:
            codon_seq = ''.join([
                next(codon) if aa != '-' # If an amino acid is not gap, then return next codon from generator
                else '---' for aa in aa_seq]) # Otherwise return codon gap as "---"
        except StopIteration as e: # In case where amino acid seq is longer than nucleotide
            logging.error(
                f'Cannot make codon alignment from the following '
                f'nucleotide ({len(nucl_seq)}) and '
                f'amino acid ({len(aa_seq)}) sequences:\n{nucl_seq}\n{aa_seq}\n'
                f'Error: {type(e).__name__}\n{e}'
            )
            raise StopIteration('Number of codons is less than the number of amino acids '
                                'in the sequence.')
            
        # Output Sequence object has the same name and description as nucleotide Sequence
        # and amino acid alignment sequence is replaced with codon alignment sequence
        codon_aln_lst.append(
            Sequence(nucl_list[i].name, nucl_list[i].description, codon_seq)
        )
    # Returns a list of Sequence objects representing codon alignments
    return codon_aln_lst

# Translate CDS to protein seq -> Align by a method with MAFFT 
# -> Position codons with referring amino acid alignment
# This is for CDS, not needed for introns
def mafft_align_codons(
    nucl_path, # Input CDS FASTA path
    aa_path, # Where to amino acid alignment is saved
    codon_path, # Where to codon alignment is saved
    translate=True,
    aln_method='einsi', aln_iterations=1000):
    
    trl_path = os.path.join(
        os.path.dirname(aa_path), os.path.basename(nucl_path) + '.trl.faa')

    # Translate if necessary
    if translate:
        translate_fasta(nucl_path, trl_path)
    # Align by MAFFT
    if aln_method == 'ginsi':
        run_obj = mafft_ginsi_align(trl_path, aa_path, aln_iterations)
    elif aln_method == 'linsi':
        run_obj = mafft_linsi_align(trl_path, aa_path, aln_iterations)
    elif aln_method == 'einsi':
        run_obj = mafft_einsi_align(trl_path, aa_path, aln_iterations)
    else:
        raise ValueError(
            'Invalid alignment method. Select "ginsi", "linsi", or "einsi" '
            'for global, local, and affine-gap scoring alignemnt method respectively.'
        )
    
    # Realign nucleotide sequences by aligned aa sequences
    codon_aln_lst = align_codons_by_aa(nucl_path, aa_path)
    i = 0
    # Write aligned codon sequences
    with open(codon_path, 'w') as f:
        for s in codon_aln_lst:
            if s.description:
                print(f'>{s.name} {s.description}', file=f)
            else:
                print(f'>{s.name}', file=f)
            print(s.sequence, file=f)
            i += 1
    return i
