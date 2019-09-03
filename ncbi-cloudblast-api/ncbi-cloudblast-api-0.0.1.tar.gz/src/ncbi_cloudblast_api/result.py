import attr
from typing import Any, List, Tuple
from enum import Enum

"""
Definition of BLAST output column header
https://www.ncbi.nlm.nih.gov/books/NBK279684/
"""

COL_DEF = {
    "qseqid": "Query Seq-id",
    "qacc": "Query accesion",
    "sseqid": "Subject Seq-id",
    "sacc": "Subject accession",
    "qstart": "Start of alignment in query",
    "qend": "End of alignment in query",
    "sstart": "Start of alignment in subject",
    "send": "End of alignment in subject",
    "qseq": "Aligned part of query sequence",
    "sseq": "Aligned part of subject sequence",
    "evalue": "Expect value",
    "bitscore": "Bit score",
    "score": "Raw score",
    "length": "Alignment length",
    "pident": "Percentage of identical matches",
    "nident": "Number of identical matches",
    "mismatch": "Number of mismatches",
    "positive": "Number of positive-scoring matches",
    "gapopen": "Number of gap openings",
    "gaps": "Total number of gap",
    "staxid": "Subject Taxonomy ID",
    "ssciname": "Subject Scientific Name",
    "scomname": "Subject Common Name",
    "sblastname": "Subject Blast Name",
    "stitle": "Subject Title",
    "sstrand": "Subject Strand",
    "qcovs": "Query Coverage Per Subject (for all HSPs)",
    "qcovhsp": "Query Coverage Per HSP"
}

"""
Default output columns are:
    qseqid sseqid pident length mismatch gapopen qstart \
    qend sstart send evalue bitscore'
"""


class NAStrand(Enum):
    UNKNOWN = 0
    PLUS = 1
    MINUS = 2


@attr.s(auto_attribs=True)
class Seg(object):
    """ A segment of the alignment """
    seglength: int = -1

    qsegstart: int = -1
    qseqstop: int = -1

    ssegstart: int = -1
    ssegstop: int = -1
    ssegstrand: str = 'UNKNOWN'


@attr.s(auto_attribs=True)
class Alignment(object):
    """ One alignment from result set """
    qseqid: str = ""
    qaccver: str = ""
    qlen: int = -1
    sseqid: str = ""
    saccver: str = ""
    stitle: str = ""
    slen: int = -1
    staxid: int = -1
    ssciname: str = ""
    scomname: str = ""
    score: int = -1
    evalue: float = -1
    bitscore: float = -1
    nident: int = -1
    pident: int = -1
    mismatch: int = -1
    gapopen: int = -1
    gaps: int = -1
    qcovs: int = -1
    qcovhsp: int = -1
    length: int = -1
    qstart: int = -1
    qend: int = -1
    qseq: str = ""
    sstart: int = -1
    send: int = -1
    sseq: str = ""
    sstrand: str = 'UNKNOWN'

    # Do not use [] or list() as the default value! If you do,
    # segs of all objects created from this class will have the same
    # default address!!
    segs: List[Seg] = attr.ib(factory=list)

    def as_tuple(self) -> Tuple[str, ...]:
        """
        Return a single tuple representing the alignment.
        Does not include segments.
        """

        return attr.astuple(self)[0:-1]

    def as_tuples(self) -> List[Tuple[str, ...]]:
        """
        Returns a list of tuples. Each tuple contains a segment
        in addition to the alignment data.
        """
        align_data = self.as_tuple()
        res = []
        for seg in self.segs:
            res.append(align_data + attr.astuple(seg))

        return res


@attr.s(auto_attribs=True)
class SearchResult(object):
    alignments: List[Alignment] = attr.ib(factory=list)

    warnings: List[str] = attr.ib(factory=list)
    errors: List[str] = attr.ib(factory=list)

    align_column_header: Tuple[str, ...] = (
        "qseqid",
        "qaccver",
        "qlen",
        "sseqid",
        "saccver",
        "stitle",
        "slen",
        "staxid",
        "ssciname",
        "scomname",
        "score",
        "evalue",
        "bitscore",
        "nident",
        "pident",
        "positive",
        "mismatch",
        "gapopen",
        "gaps",
        "qcovs",
        "qcovhsp",
        "length",
        "qstart",
        "qend"
        "qseq",
        "sstart",
        "send",
        "sseq",
        "sstrand"
    )

    seg_column_header: Tuple[str, ...] = (
        "seglength",
        "qsegstart",
        "qsegstop",
        "ssegstart",
        "ssegstop",
        "ssegstrand"
    )

    def tuple_header(self, detailed: bool = False) -> Tuple[str, ...]:
        """ Return tuple/column headers.
            Including headers for segments if detailed is True; otherwise
            return headers without those for segments. Default is False.
        """
        return self.align_column_header + self.seg_column_header \
            if detailed else self.align_column_header

    def as_tuples(self, detailed: bool = False) -> List[Tuple[str, ...]]:
        """ Return search result as tuples.
            If detailed is False, one tuple for each alignment (no segment);
            Otherwise, also include segments, so that each segment from an
            alignmet gets its own tuple plus the same alignment data.
        """
        res = []
        for r in self.alignments:
            if detailed:
                res.extend(r.as_tuples())
            else:
                res.append(r.as_tuple())
        return res

    def as_dataframe(self, detailed: bool = False) -> Any:  # DataFrame
        """ Return search as a panads.DataFrame.
            If detailed is False, result will be one row per alignment (no segment).
            Otherwise, result will be one segment per row (plus the same alignment
            data).
        """
        try:
            from pandas import DataFrame
            return DataFrame(
                self.as_tuples(detailed),
                columns=self.tuple_header(detailed)
            )
        except ImportError:
            raise ImportError("This method requires the pandas package to be installed")
