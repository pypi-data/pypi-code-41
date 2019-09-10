import numpy as np
import subprocess
import pysam


def create_olego_index(fasta, algo='bwtsw'):
    subprocess.check_call(['olegoindex', '-a', algo, fasta])


def olego_align(fastq1, fastq2=None, index=None, threads=1, out_bam1=None,
                out_bam2=None, out_bam=None, mem=2):
    '''Align single or paired-end data with OLego.

    Creates a position-sorted BAM file (out_bam).
    
    Arguments:
    - fastq1: Read1 fastq
    - fastq2: (Optional) If this is provided, data are assumed to be paired-end.
    In this case, you must specify out_bam1 and out_bam2 where the aligned read1
    and read2 will be stored, prior to merging into out_bam.
    - out_bam: Final position sorted BAM.
    - index: OLego index.
    - threads: Threads for OLego and sorting.
    - mem: Memory for samtools sorting.
    '''

    def call_olego(fq, bam):
        p1 = subprocess.Popen(['olego', '-v', '-t', str(threads),
                               '-M', '4', index, fq], stdout=subprocess.PIPE)
        # convert to BAM (olego will output sam to stdout)
        p2 = subprocess.Popen(['samtools', 'view', '-b', '-'],
                              stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        # Sort with 16 threads and 2Gb of memory per thread
        p3 = subprocess.Popen(['samtools', 'sort', '-o', bam,
                               '-m', '{}G'.format(mem),
                               '--threads', str(threads), '-'],
                              stdin=p2.stdout, stdout=subprocess.PIPE)
        p2.stdout.close()
        _ = p3.communicate()

    if fastq2 is None:
        call_olego(fastq1, out_bam)
    else:
        if out_bam1 is None or out_bam2 is None:
            raise ValueError('You must specify a location for each of the read1 and read2 bams')
        call_olego(fastq1, out_bam1)
        call_olego(fastq2, out_bam2)
        subprocess.check_call(['samtools', 'merge', out_bam, out_bam1, out_bam2])

    subprocess.check_call(['samtools', 'index', out_bam])


def name_sort_bam(in_bam, out_bam, threads=1, mem=2):
    cmd = ['samtools', 'sort', '-n', '-m', '{}G'.format(mem),
           '-o', out_bam, '--threads', str(threads), in_bam]
    subprocess.check_call(cmd)


def position_sort_bam(in_bam, out_bam, threads=1, mem=2):
    cmd = ['samtools', 'sort', '-m', '{}G'.format(mem),
           '-o', out_bam, '--threads', str(threads), in_bam]
    subprocess.check_call(cmd)
    subprocess.check_call(['samtools', 'index', out_bam])


def choose_random_pair(p1, p2):
    return p1 if np.random.rand() < 0.5 else p2


def get_is_unmapped(r):
    return int(r.is_unmapped or r.mapq == 0)


def get_mismatches(r):
    try:
        return r.get_tag('NM')
    except KeyError:
        return 0


def merge_bams(ref_bam_file, alt_bam_file, out_file, is_paired=True):
    """Takes two name-sorted bams and returns a merged bam with one occurrence of each read-pair.
    It doesn't matter which file is specified as reference.
    """
    ref_bam = pysam.AlignmentFile(ref_bam_file, 'rb')
    alt_bam = pysam.AlignmentFile(alt_bam_file, 'rb')
    out_bam = pysam.AlignmentFile(out_file, 'wb', template=ref_bam)

    npairs = 0

    while True:
        try:
            if is_paired:
                ref_pair = (next(ref_bam), next(ref_bam))
                alt_pair = (next(alt_bam), next(alt_bam))
            else:
                ref_pair = (next(ref_bam),)
                alt_pair = (next(alt_bam),)
        except StopIteration:
            break

        npairs += 1
        if is_paired:
            assert ref_pair[0].qname == ref_pair[1].qname
            assert alt_pair[0].qname == alt_pair[1].qname
        assert ref_pair[0].qname == alt_pair[0].qname

        ref_unmapped = get_is_unmapped(ref_pair[0]) + (get_is_unmapped(ref_pair[1]) if is_paired else 0)
        alt_unmapped = get_is_unmapped(alt_pair[0]) + (get_is_unmapped(alt_pair[1]) if is_paired else 0)
        ref_mismatches = get_mismatches(ref_pair[0]) + (get_mismatches(ref_pair[1]) if is_paired else 0)
        alt_mismatches = get_mismatches(alt_pair[0]) + (get_mismatches(alt_pair[1]) if is_paired else 0)
        
        if ref_unmapped == 2 and alt_unmapped == 2:
            sel_pair = choose_random_pair(ref_pair, alt_pair)
        elif ref_unmapped > alt_unmapped:
            sel_pair = alt_pair
        elif ref_unmapped < alt_unmapped:
            sel_pair = ref_pair
        elif ref_mismatches > alt_mismatches:
            sel_pair = alt_pair
        elif ref_mismatches < alt_mismatches:
            sel_pair = ref_pair
        else:
            sel_pair = choose_random_pair(ref_pair, alt_pair)
            
        out_bam.write(sel_pair[0])
        if is_paired:
            out_bam.write(sel_pair[1])

    ref_bam.close()
    alt_bam.close()
    out_bam.close()
