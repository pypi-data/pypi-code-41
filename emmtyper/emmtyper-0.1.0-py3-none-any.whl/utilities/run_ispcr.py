"""
Define the workflow to run PCR using isPcr
"""
from os import environ
import logging

from emmtyper.objects.ispcr import IsPCR


logging.basicConfig(level=environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__name__)


def get_amplicons(query, primer_db, min_perfect, min_good, max_size, tool_path):
    """
    Run isPcr and return temporary file with amplicons
    """
    pcr_amplicons = query.split("/")[-1].split(".")[0] + "_pcr.tmp"

    pcr = IsPCR(
        assembly_filename=query,
        primer_filename=primer_db,
        min_perfect=min_perfect,
        min_good=min_good,
        max_product_length=max_size,
        output_stream="stdout",
        tool_path=tool_path,
    )

    # Run isPcr, take output and use it as input for Blast.
    with open(pcr_amplicons, "w") as temp:
        temp.write(pcr.run_isPCR())

    return pcr_amplicons
