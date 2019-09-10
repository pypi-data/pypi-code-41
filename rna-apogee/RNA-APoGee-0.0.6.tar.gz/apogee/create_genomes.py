import argparse
from apogee.seq_utils import create_personal_genome
from apogee.align import create_olego_index
import os.path
import vcf


DESC = '''Create versions of an input FASTA with sample-specific SNVs replacing reference bases.'''

fasta_help = '''FASTA file that will be used as the base for generating personal genomes.
For each sample in the input VCF, an individual genome will be created by substituting
the sample's SNVs into this base FASTA. SNVs will be considered only if the FILTER field
is PASS, and the genotype quality is greater than <min_gq>.
'''
outdir_help = '''Personal genome for sample <sample> will be in <outdir>/<sample>.fa'''
vcf_help = '''VCF with variant calls. Can have multiple samples.'''
samples_help = '''Comma separated list of samples from the input VCF. If provided,
only the personal genomes for these samples will be created, otherwise personal genomes
for all samples in the input VCF will be created.'''
chunk_help = '''How many bases to keep in memory. Reduce if running OOM.
'''


def main():
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument('--fasta', required=True, help=fasta_help)
    parser.add_argument('--vcf', required=True, help=vcf_help)
    parser.add_argument('--outdir', required=True, help=outdir_help)
    parser.add_argument('--samples', help=samples_help)
    parser.add_argument('--min_gq', help='Minimum genotype quality to consider a variant [%(default)s]',
                        type=int, default=20)
    parser.add_argument('--chunk', default=1e6, type=int, help=chunk_help + ' [%(default)s]')
    args = parser.parse_args()

    outreg = os.path.join(args.outdir, '{}.fa')
    if args.samples:
        samples = [s.strip() for s in args.samples.split(',')]
    else:
        reader = vcf.Reader(filename=args.vcf)
        samples = reader.samples

    create_personal_genome(args.fasta, args.vcf, outreg, samples=samples,
                           min_gq=args.min_gq, chunk_size=args.chunk,
                           verbose=True)
    for sample in samples:
        create_olego_index(outreg.format(sample))
    

if __name__ == '__main__':
    main()
