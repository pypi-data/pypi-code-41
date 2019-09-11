import pyfasta
import vcf
from . import vcf_utils as vu
import sys
import numpy as np


def open_fasta(fasta_file):
    fasta = pyfasta.Fasta(fasta_file)
    new_fasta = {k.split()[0]: fasta[k] for k in fasta.keys()}
    return new_fasta


def create_personal_genome(fasta_file, vcf_file, outreg='./{}.fa',
                           samples=None, contigs=None, chunk_size=1e6,
                           min_gq=20, verbose=True):
    
    fasta = open_fasta(fasta_file)
    reader = vcf.Reader(filename=vcf_file)

    if samples is None:
        samples = reader.samples
    else:
        if len(set(samples).difference(reader.samples)) > 0:
            raise ValueError('Some of the specified samples are not present in the input VCF')

    if contigs is None:
        contigs = fasta.keys()

    out_fastas = [open(outreg.format(s), 'w') for s in samples]

    for chrom in contigs:
        chrom_len = len(fasta[chrom])
        nchunks = int(np.ceil(chrom_len / float(chunk_size)))
        
        for ci in range(nchunks):
            if verbose:
                print('{}: chunk {} of {}'.format(chrom, ci + 1, nchunks), file=sys.stderr)
            chunk_start = int(ci * chunk_size)
            chunk_stop = int(min(chrom_len, chunk_start + chunk_size))
            
            seq = fasta[chrom][chunk_start:chunk_stop]
            sample_seqs = [list(str(seq)) for _ in samples]
            
            try:
                rec_iter = reader.fetch(str(chrom), chunk_start, chunk_stop)
                for i, rec in enumerate(rec_iter):
                    if not vu.rec_is_passing(rec):
                        continue

                    pos = rec.POS - 1
                    adj_pos = pos - chunk_start

                    if len(rec.REF) != 1:
                        continue  # SNVs only

                    if len(rec.ALT) != 1:
                        continue  # Ignore multi-allelic sites
                    
                    alt = str(rec.ALT[0])
                    if len(alt) != 1:
                        continue  # SNVs only

                    for si in range(len(samples)):
                        geno = rec.genotype(samples[si])
                        qual = float(vu.get_rec_field(geno, 'GQ', 0.0))
                        gt = vu.get_rec_gt(geno)
                        if qual < min_gq or gt == 0:
                            continue
                        sample_seqs[si][adj_pos] = alt
            
            except ValueError:
                # The input VCF might not have variants for all the contigs
                pass

            for si in range(len(samples)):
                if ci == 0:
                    out_fastas[si].write('>{}\n'.format(chrom))
                out_fastas[si].write('{}'.format(''.join((sample_seqs[si]))))
                if ci == nchunks - 1:
                    out_fastas[si].write('\n')

    for f in out_fastas:
        f.close()
    reader._reader.close()
