#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getopt
import sys
from fixalign import find_fix_small_exon

"""
The script is used to import fixalign package and run find_fix_small_exon function to find and fix small exon missed reads.
"""
def main():
	opts, args = getopt.getopt(sys.argv[1:], '-h-r:-a', ['help'])

	for opt_name, opt_value in opts:
    if opt_name in ('-h', '--help'):
        print("""
The script is used to fix small exon missing problem in ONT reads. It is based on python3 and fixalign package.

Usage: python3 run_fixalign [-h] ref.fa

            """)
        exit()

	delta_ratio_thd = 0.5

	ori_bam_path = "/home/zhen/project/small_exon/sequin/ori_aln/q7_above/sequin_mapped.bam"
	out_bam_path = "/home/zhen/project/small_exon/sequin/realign_result/only_exon/q7_above/realign_fa.bam"
	ref_fa_path = "/home/zhen/project/small_exon/sequin/chrom/chrIS.fa"
	annot_bed_path = "/home/zhen/project/small_exon/sequin/annotation/tx.bed"
	out_realign_region_path = "/home/zhen/project/small_exon/sequin/realign_region/q7_above/noannot_S100D0.5_sim_fa.txt"

	find_fix_small_exon(ori_bam_path, ref_fa_path, annot_bed_path, out_bam_path, out_realign_region_path,
                    	small_exon_size=100, flank_len=21, ignore_strand=True,
                    	delta_ratio_thd=0.5, simplify=True, float_flank_len=False, only_region=False)
