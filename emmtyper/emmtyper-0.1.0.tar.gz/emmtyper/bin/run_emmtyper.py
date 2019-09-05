"""
For running emmtyper
"""

import logging
import pathlib
import os

import click

from emmtyper.__init__ import __version__ as version
from emmtyper.utilities import run_ispcr, run_blast
from emmtyper.objects.clusterer import Clusterer

DEFAULT_DB = pathlib.Path(__file__).parent.parent / "db" / "emm.fna"
DEFAULT_PRIMERS = pathlib.Path(__file__).parent.parent / "data" / "isPcrPrim.tsv"

logger = logging.getLogger(__name__)


@click.command()
@click.version_option(
    version=version, prog_name="emmtyper", message=("%(prog)s v%(version)s")
)
@click.argument("fasta", nargs=-1)
@click.option(
    "-w",
    "--workflow",
    default="blast",
    help="Choose workflow",
    type=click.Choice(["blast", "pcr"]),
    show_default=True,
)
@click.option(
    "-d",
    "--blast_db",
    default=os.environ.get("EMM_DB", DEFAULT_DB),
    help="Path to EMM BLAST DB",
    show_default=True,
)
@click.option(
    "-k",
    "--keep",
    is_flag=True,
    help="Keep BLAST and isPcr output files.",
    show_default=True,
)
@click.option(
    "-d",
    "--cluster-distance",
    default=500,
    help="Distance between cluster of matches to consider as different clusters.",
    show_default=True,
)
@click.option(
    "-o",
    "--output",
    default="stdout",
    help="Output stream. Path to file for output to a file.",
    show_default=True,
)
@click.option(
    "-f",
    "--output-format",
    default="short",
    help="Output format.",
    type=click.Choice(["short", "verbose", "visual"]),
)
@click.option(
    "--dust",
    default="no",
    help="[BLAST] Filter query sequence with DUST.",
    type=click.Choice(["yes", "no", "level window linker"]),
    show_default=True,
)
@click.option(
    "--percent-identity",
    default=95,
    help="[BLAST] Minimal percent identity of sequence.",
    show_default=True,
)
@click.option(
    "--culling-limit",
    default=5,
    help="[BLAST] Total hits to return in a position.",
    show_default=True,
)
@click.option(
    "--mismatch",
    default=4,
    help="[BLAST] Threshold for number of mismatch to allow in BLAST hit.",
    show_default=True,
)
@click.option(
    "--align-diff",
    default=5,
    help="[BLAST] Threshold for difference between alignment length and subject length in BLAST hit.",
    show_default=True,
)
@click.option(
    "--gap",
    default=2,
    help="[BLAST] Threshold gap to allow in BLAST hit.",
    show_default=True,
)
@click.option(
    "--blast-path",
    help="[BLAST] Specify full path to blastn executable.",
    show_default=True,
)
@click.option(
    "--primer-db",
    default=os.environ.get("EMM_PCR", DEFAULT_PRIMERS),
    help="[isPcr] PCR primer. Text file with 3 columns: Name, Forward Primer, Reverse Primer.",
    show_default=True,
)
@click.option(
    "--min-perfect",
    default=15,
    help="[isPcr] Minimum size of perfect match at 3' primer end.",
    show_default=True,
)
@click.option(
    "--min-good",
    default=15,
    help="[isPcr] Minimum size where there must be 2 matches for each mismatch.",
    show_default=True,
)
@click.option(
    "--max-size",
    default=2000,
    help="[isPcr] Maximum size of PCR product.",
    show_default=True,
)
@click.option(
    "--ispcr-path",
    help="[isPcr] Specify full path to isPcr executable.",
    show_default=True,
)
def main(
    fasta,
    workflow,
    blast_db,
    keep,
    cluster_distance,
    output,
    output_format,
    dust,
    percent_identity,
    culling_limit,
    mismatch,
    align_diff,
    gap,
    blast_path,
    primer_db,
    min_perfect,
    min_good,
    max_size,
    ispcr_path,
):
    """
    Welcome to emmtyper.

    Usage:

    emmtyper *.fasta
    """
    logger.info("Start running emmtyper on {} queries.".format(len(fasta)))
    for i, query in enumerate(fasta):
        if workflow == "pcr":
            query = run_ispcr.get_amplicons(
                query, str(primer_db), min_perfect, min_good, max_size, ispcr_path
            )

        blast_matches = run_blast.get_matches(
            query,
            str(blast_db),
            dust,
            percent_identity,
            culling_limit,
            mismatch,
            align_diff,
            gap,
            blast_path,
        )

        clusterer = Clusterer(
            blastOutputFile=blast_matches,
            distance=cluster_distance,
            output_stream=output,
            output_type=output_format,
        )
        clusterer()

        if not keep:
            os.remove(blast_matches)

    logger.info("Finished emmtyper.")


if __name__ == "__main__":
    main()
