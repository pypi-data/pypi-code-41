#!python

#
# Copyright 2019, Julian Catchen <jcatchen@illinois.edu>
#
# This file is part of RADinitio.
#
# RADinitio is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RADinitio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RADinitio. If not, see <http://www.gnu.org/licenses/>.
#

import numpy as np
import msprime, sys, argparse, os, datetime, time
import radinitio as ri
print(ri.__file__)
program_name = os.path.basename(__file__)

#
# set command line variables:
p = argparse.ArgumentParser()
p.add_argument('-g', '--genome',     dest='geno',                                 help='Path to reference genome (fasta file)')
p.add_argument('-l', '--chrom-list', dest='clist',               default=None,    help='File containing a subsample of chromosomes to simulate')
p.add_argument('-o', '--output',     dest='outd',                                 help='Path to an output directory where all files will be written')
p.add_argument('-p', '--num-pop',    dest='npop',    type=int,   default=2,       help='Number of populations in the island model')
p.add_argument('-s', '--num-sam',    dest='nsam',    type=int,   default=10,      help='Number of samples sampled from each population')
p.add_argument('-n', '--eff-pop',    dest='ne',      type=float, default=5e3,     help='Effective population size of simulated demes')
p.add_argument('-b', '--lib-type',   dest='ltype',               default='sdRAD', help='Type of RAD library (sdRAD or ddRAD)')
p.add_argument('-e', '--enz',        dest='renz',                default='SbfI',  help='Restriction enzyme (SbfI, PstI, EcoRI, BamHI, etc.)')
p.add_argument('-d', '--dd-enz',     dest='ddenz',               default='MspI',  help='Second restriction enzyme for double digest (SbfI, PstI, EcoRI, BamHI, etc.)')
p.add_argument('-c', '--pcr-c',      dest='pcrc',    type=int,   default=0,       help='Number of PCR cycles')
p.add_argument('-v', '--coverage',   dest='cov',     type=int,   default=20,      help='Sequencing coverage (X)')
p.add_argument('-t', '--threads',    dest='threads', type=int,   default=1,       help='Number of threads')

args = p.parse_args()

# Overwrite the help/usage behavior.
p.format_usage = lambda : '''\
{prog} --genome path --outdir dir [--chrom-list path] [(demographic model options)] [(library options)] [--threads int]

Input/Output files:
    -g, --genome:     Path to reference genome (fasta file)
    -l, --chrom-list: File containing a subsample of chromosomes to simulate. Contains one chromosome id per line
    -o, --output:     Path to an output directory where all files will be written

Demographic model (simple island model)
    -p, --num-pop:    Number of populations in the island model  (default = 2)
    -s, --num-sam:    Number of samples sampled from each population  (default = 10)
    -n, --eff-pop     Effective population size of simulated demes  (default = 5e3)

Library preparation/sequencing:
    -b, --lib-type:   Library type (sdRAD or ddRAD)  (default = 'sdRAD')
    -e, --enz:        Restriction enzyme (SbfI, PstI, EcoRI, BamHI, etc.)  (default = 'SbfI')
    -d, --dd-enz:     Second restriction enzyme for double digest (MspI, MseI, AluI, etc.)  (default = 'MspI')
    -c, --pcr-c:      Number of PCR cycles  (default = 0)
    -v, --coverage:   Sequencing coverage  (default = 20)

Other:
    -t, --threads:  Number of threads  (default = 1)
'''.format(prog=program_name)
p.format_help = p.format_usage

# Check required arguments
for required in ['geno', 'outd']:
    if args.__dict__[required] is None:
        print('Required argument \'{}\' is missing.\n'.format(required), file=sys.stderr)
        p.print_help()
        sys.exit(1)

# Work on log file
outd = args.outd.rstrip('/')
# TODO: change this to file handle instead of overwriting stdout
log_file = open('{}/radinitio.log'.format(outd), "w")
print('{} version {} started on {}.'.format(program_name, ri.__version__, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), file=log_file)

#
# Genome options
#
# Generate chromosome set from chromosome list
genome_dict = None
if args.clist is not None:
    chrom_list = open(args.clist).read().split()
    # Generate genome dictionary and other genome variables
    genome_dict = ri.load_genome(args.geno, set(chrom_list))
else:
    # Generate genome dictionary and other genome variables
    genome_dict = ri.load_genome(args.geno)
print('\n{} - Loading genome...'.format(ri.elapsed()), file=log_file)
sys.stdout.flush()

#
# Msprime parameters
#
# General variables
npops = args.npop
ne = args.ne
samples = args.nsam
mig_r = 0.001
pops = []
# Population configurations for simple island model
for i in range(npops):
    pops.append(msprime.PopulationConfiguration(sample_size=samples*2, initial_size=ne, growth_rate=0.0))
# In case of single population
msprime_simulate_args = None
if npops == 1:
    msprime_simulate_args = dict(
    mutation_rate=7e-8,
    population_configurations=pops)
else:
    # Migration matrix for simple island model
    m = mig_r / (4 * (npops - 1)) # per generation migration rate
    mig_matrix = [ [ 0 if i == j else m
            for j in range(npops) ]
            for i in range(npops) ]
    # msprime simulate arguments
    msprime_simulate_args = dict(
        mutation_rate=7e-8,
        population_configurations=pops,
        migration_matrix=mig_matrix)

#
# RADinito class options
#
# Set mutation options
muts_opts = ri.MutationModel()
print('\n{} - {}'.format(ri.elapsed(), muts_opts), file=log_file)
sys.stdout.flush()
# set library options
library_opts = ri.LibraryOptions(library_type=args.ltype, renz_1=args.renz, renz_2=args.ddenz, coverage=args.cov)
print('\n{} - {}'.format(ri.elapsed(), library_opts), file=log_file)
sys.stdout.flush()
# pcr opts
#   Estimate the number of loci for PCR model
n_sequenced_reads = ri.avg_num_reads(genome_dict, library_opts)
#   Create model
pcr_opts = ri.PCRDups(pcr_c=args.pcrc, n_sequenced_reads=n_sequenced_reads)
print('\n{} - {}'.format(ri.elapsed(), pcr_opts), file=log_file)
sys.stdout.flush()

# Print msprime arguments
ri.print_msp_params(msprime_simulate_args, log_file)
# Print Chromosome information
print('\nSimulating over the following chromosomes (Name : Length (bp) : Recombination Rate):', file=log_file)
for chrom in sorted(genome_dict.keys()):
    chromosome = genome_dict[chrom]
    assert isinstance(chromosome, ri.Chromosome)
    print('    {}'.format(chromosome), file=log_file)

#
# Path variables
#
msprime_vcf_dir = '{}/msprime_vcfs'.format(outd)
popmap_file     = '{}/popmap.tsv'.format(outd)
ref_loci_dir    = '{}/ref_loci_vars'.format(outd)
master_vcf_dir  = '{}/ref_loci_vars'.format(outd)
rad_alleles_dir = '{}/rad_alleles'.format(outd)
rad_reads_dir   = '{}/rad_reads'.format(outd)

#
# Main simulation wrapper
#
# Run base simulations
ri.simulate(genome_dict=genome_dict,
            msprime_simulate_args=msprime_simulate_args,
            msprime_vcf_dir=msprime_vcf_dir,
            popmap_file=popmap_file,
            ref_loci_dir=ref_loci_dir,
            master_vcf_dir=master_vcf_dir,
            rad_alleles_dir=rad_alleles_dir,
            rad_reads_dir=rad_reads_dir,
            library_opts=library_opts,
            mutation_opts=muts_opts,
            pcr_opts=pcr_opts,
            log_file=log_file,
            threads=args.threads)

# Finish and report log
print('\n{} - {} version {} completed on {}.'.format(ri.elapsed(), program_name, ri.__version__, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), file=log_file)
sys.stdout.flush()
