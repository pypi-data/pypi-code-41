"""
Define the workflow to run BLAST
"""
from os import environ
import logging

from emmtyper.objects.blast import BLAST


logging.basicConfig(level=environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__name__)


def get_matches(
    query,
    blast_db,
    dust,
    percent_identity,
    culling_limit,
    mismatch,
    align_diff,
    gap,
    tool_path,
):
    """
    Run BLAST and return a temporary file with matches
    """
    blast_matches = query.split("/")[-1].split(".")[0] + ".tmp"

    blast = BLAST(
        db=blast_db,
        query=query,
        dust=dust,
        perc_identity=percent_identity,
        culling_limit=culling_limit,
        output_stream=blast_matches,
        header=False,
        mismatch=mismatch,
        align_diff=align_diff,
        gap=gap,
        tool_path=tool_path,
    )

    blast.run_blastn_pipeline()

    return blast_matches
