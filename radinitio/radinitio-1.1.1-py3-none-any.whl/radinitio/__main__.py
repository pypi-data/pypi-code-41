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

import os, sys, argparse
import msprime
import radinitio as ri

usage = '''raditio version {}

radinitio --genome path --chromosomes path --out-dir dir [pipeline-stage] [(demographic model options)] [(library options)]

Pipeline stages (these options are mutually exclusive):
    --simulate-all       Run all the RADinitio stages (simulate a population, make a library, and sequence) (Default)
    --make-population    Simulate and process variants. Produces genome-wide VCF.
    --make-library-seq   Simulate and sequence a RAD library. Requires exising variants.
    --tally-rad-loci     Calculate the number of kept rad loci in the genome.

Input/Output files:
    -g, --genome:        Path to reference genome (fasta file, may be gzipped). (Required)
    -l, --chromosomes:   File containing the list of chromosomes (one per line) to simulate. (Required)
    -o, --out-dir:       Path to an output directory where all files will be written. (Required)

Demographic model (simple island model)
    -p, --n-pops:        Number of populations in the island model.  (default = 2)
    -n, --pop-eff-size:  Effective population size of simulated demes.  (default = 5000)
    -s, --n-seq-indv:    Number of individuals sampled from each population.  (default = 10)

Library preparation/sequencing:
    -b, --library-type:  Library type (sdRAD or ddRAD).  (default = 'sdRAD')
    -e, --enz:           Restriction enzyme (SbfI, PstI, EcoRI, BamHI, etc.).  (default = 'SbfI')
    -d, --enz2:          Second restriction enzyme for double digest (MspI, MseI, AluI, etc.).  (default = 'MspI')
    -m, --insert-mean:   Insert size mean in bp.  (default = 350)
    -t, --insert-stdev:  Insert size standard deviation in bp.  (default = 37)
    -c, --pcr-cycles:    Number of PCR cycles.  (default = 0)
    -v, --coverage:      Sequencing coverage.  (default = 20)
    -r, --read-length:   Sequence read length.  (default = 150)

make-library-seq()-specific options:
    --make-pop-sim-dir   Directory containing a previous radinitio.make_population run. Cannot be the same as out-dir.

Additional options:
    -V, --version:       Print program version.
    -h, --help:          Display this help message.
'''.format(ri.__version__)

def parse_args():
    p = argparse.ArgumentParser(prog='radinitio')
    s = p.add_mutually_exclusive_group() # For the different pipeline stages
    s.add_argument(      '--simulate-all',     action='store_true', default=True)
    s.add_argument(      '--make-population',  action='store_true')
    s.add_argument(      '--make-library-seq', action='store_true')
    s.add_argument(      '--tally-rad-loci',   action='store_true')
    p.add_argument('-g', '--genome',           required=True)
    p.add_argument('-l', '--chromosomes',      required=True)
    p.add_argument('-o', '--out-dir',          required=True)
    p.add_argument('-p', '--n-pops',           type=int, default=2)
    p.add_argument('-n', '--pop-eff-size',     type=float, default=5e3)
    p.add_argument('-s', '--n-seq-indv',       type=int, default=10)
    p.add_argument('-b', '--library-type',     default='sdRAD')
    p.add_argument('-e', '--enz',              default='SbfI')
    p.add_argument('-d', '--enz2',             default='MspI')
    p.add_argument('-m', '--insert-mean',      type=int, default=350)
    p.add_argument('-t', '--insert-stdev',     type=int, default=37)
    p.add_argument('-c', '--pcr-cycles',       type=int, default=0)
    p.add_argument('-v', '--coverage',         type=int, default=20)
    p.add_argument('-r', '--read-length',      type=int, default=150)
    p.add_argument(      '--make-pop-sim-dir', default=None)
    p.add_argument('-V', '--version',          action='version', version='radinitio version {}\n'.format(ri.__version__))

    # Overwrite the help/usage behavior.
    p.format_usage = lambda : usage
    p.format_help = p.format_usage

    # Check input arguments
    args = p.parse_args()
    args.out_dir = args.out_dir.rstrip('/')
    assert args.n_pops >= 1
    assert os.path.exists(args.genome)
    assert os.path.exists(args.chromosomes)
    if not os.path.exists(args.out_dir):
        sys.exit("Error: '{}': output directory does not exist.".format(args.out_dir))

    return args

def main():
    args = parse_args()

    # Some general options
    # ====================
    # Parse chromosomes
    chromosomes = open(args.chromosomes).read().split()
    recomb_rate = 3e-8
    # ===================
    # RADinito options
    muts_opts = ri.MutationModel()
    library_opts = ri.LibraryOptions(
        library_type = args.library_type,
        renz_1 = args.enz,
        renz_2 = args.enz2,
        insert_mu = args.insert_mean,
        insert_sigma = args.insert_stdev,
        coverage = args.coverage,
        read_len = args.read_length)

    #
    # Check stage arguments:
    # ======================
    # If only generating variants
    if args.make_population is True:
        # Define msprime population options
        msprime_simulate_args = ri.simple_msp_island_model(args.n_seq_indv, args.pop_eff_size, args.n_pops)
        # Call radinitio.make_population
        ri.make_population(
            out_dir = args.out_dir,
            genome_fa = args.genome,
            chromosomes = chromosomes,
            chrom_recomb_rates = recomb_rate,
            msprime_simulate_args = msprime_simulate_args,
            mutation_opts = muts_opts)

    #
    # =========================
    # If only tallying cutsites
    elif args.tally_rad_loci is True:
        # Call radinitio.tally_rad_loci
        ri.tally_rad_loci(
            out_dir = args.out_dir,
            genome_fa = args.genome,
            chromosomes = chromosomes,
            library_opts = library_opts)

    #
    # =========================================
    # If only generating library and sequencing
    # Previous run of `make-populations` needed
    elif args.make_library_seq is True:
        # Check inputs
        if args.make_pop_sim_dir is None:
            sys.exit('Need to specify `make_populations` directory when simulating library & sequencing')
        # Define pcr_options
        pcr_opts = ri.PCRDups(
            pcr_c = args.pcr_cycles,
            library_opts = library_opts)
        # Call radinitio.make-library_seq
        ri.make_library_seq(
            out_dir = args.out_dir,
            genome_fa = args.genome,
            chromosomes = chromosomes,
            make_pop_sim_dir = args.make_pop_sim_dir, 
            library_opts = library_opts,
            mutation_opts = muts_opts,
            pcr_opts = pcr_opts)

    #
    # =================================================
    # Default to running the whole pipeline - radinitio.simulate()
    else:
        # Define msprime population options
        msprime_simulate_args = ri.simple_msp_island_model(args.n_seq_indv, args.pop_eff_size, args.n_pops)
        # Define pcr_options
        pcr_opts = ri.PCRDups(
            pcr_c = args.pcr_cycles,
            library_opts = library_opts)
        # Call radinitio.simulate
        ri.simulate(
            out_dir = args.out_dir,
            genome_fa = args.genome,
            chromosomes = chromosomes,
            chrom_recomb_rates = recomb_rate,
            msprime_simulate_args = msprime_simulate_args,
            library_opts = library_opts,
            mutation_opts = muts_opts,
            pcr_opts = pcr_opts)

if __name__ == '__main__':
    main()
