import attr
from typing import Dict, List
from enum import Enum

# NOT USED. Keep for future reference.

# Python objects created via attrs for the corresponding
# protobuf objects as defined in public API spec.


@attr.s
class DbInfo(object):
    name: str = attr.ib(default="")
    tag: str = attr.ib(default="")
    description: str = attr.ib(default="")


@attr.s
class DbList(object):
    dbs: List[DbInfo] = attr.ib(factory=list)


@attr.s
class ResultStatus(object):

    class Status(Enum):
        UNKNOWN = 0
        PENDING = 1
        RUNNING = 2
        SUCCESS = 3
        FAILURE = 4
        UNRECOGNIZED_RID = 5

    job_id: str = attr.ib(default="")
    status: Status = attr.ib(default=Status.UNKNOWN)


@attr.s
class StatusReply(object):
    status: List[ResultStatus] = attr.ib(factory=list)


class NAStrand(Enum):
    UNKNOWN = 0
    PLUS = 1
    MINUS = 2


@attr.s
class SeqCoord(object):
    start: int = attr.ib(default=0)
    end: int = attr.ib(default=0)
    strand: NAStrand = attr.ib(NAStrand.UNKNOWN)


@attr.s
class Seg(object):
    length: int = attr.ib(default=0)
    query_coords: SeqCoord = attr.ib(default=None)
    subject_coords: SeqCoord = attr.ib(default=None)


@attr.s
class Alignment(object):
    subject_seq_id: str = attr.ib(default="")
    score: int = attr.ib(default=0)
    e_value: float = attr.ib(default=0)
    bit_score: float = attr.ib(default=0)
    num_identical: int = attr.ib(default=0)
    percent_identity: float = attr.ib(default=0)
    query_coords: SeqCoord = attr.ib(default=None)
    subject_coords: SeqCoord = attr.ib(default=None)
    alignment_length: int = attr.ib(default=0)
    num_mismatches: int = attr.ib(default=0)
    num_gap_opens: int = attr.ib(default=0)
    num_gaps: int = attr.ib(default=0)
    percent_qry_cov_per_subject: int = attr.ib(default=0)
    percent_qry_cov_per_unique_subject: int = attr.ib(default=0)
    percent_qry_cov_per_hsp: int = attr.ib(default=0)
    aligned_query_seq: str = attr.ib(default="")
    aligned_subject_seq: str = attr.ib(default="")
    segments: List[Seg] = attr.ib(factory=list)


@attr.s
class Infraspecies(object):
    class InfraspecificType(Enum):
        UNKNOWN = 0
        BREED = 1
        ISOLATE = 2
        CULTIVAR = 3
        STRAIN = 4

    type: InfraspecificType = attr.ib(default=InfraspecificType.UNKNOWN)
    value: str = attr.ib("")


@attr.s
class Organism(object):
    class TaxGroupType(Enum):
        UNKNOWN = 0
        BACTERIA = 1
        VIRUS = 2
        VIROID = 3
        EUK = 4
        ARCHAEA = 5

    class RankType(Enum):
        NO_RANK = 0
        SUPERKINGDOM = 1
        KINGDOM = 2
        SUBKINGDOM = 3
        SUPERPHYLUM = 4
        SUBPHYLUM = 5
        PHYLUM = 6
        SUPERCLASS = 7
        CLASS = 8
        SUBCLASS = 9
        INFRACLASS = 10
        SUPERORDER = 11
        ORDER = 12
        SUBORDER = 13
        INFRAORDER = 14
        PARVORDER = 15
        SUPERFAMILY = 16
        FAMILY = 17
        SUBFAMILY = 18
        GENUS = 19
        SUBGENUS = 20
        SPECIES_GROUP = 21
        SPECIES_SUBGROUP = 22
        SPECIES = 23
        SUBSPECIES = 24
        TRIBE = 25
        SUBTRIBE = 26
        FORMA = 27
        VARIETAS = 28
        COHORT = 29
        SUBCOHORT = 30

    tax_id: int = attr.ib(default=0)
    sci_name: str = attr.ib(default="")
    common_name: str = attr.ib(default="")
    infra_species: Infraspecies = attr.ib(default=None)
    tax_group: TaxGroupType = attr.ib(default=TaxGroupType.UNKNOWN)
    host: str = attr.ib(default="")
    rank: RankType = attr.ib(default=RankType.NO_RANK)
    genomic_moltype: str = attr.ib(default="")


class SeqType(Enum):
    NUCLEOTIDE = 1
    PROTEIN = 2


@attr.s
class SeqInfo(object):
    seq_id: str = attr.ib(default="")
    accession: str = attr.ib(default="")
    title: str = attr.ib(default="")
    org: Organism = attr.ib(default=None)
    type: SeqType = attr.ib(default=SeqType.NUCLEOTIDE)
    length: str = attr.ib(default="")


@attr.s
class SearchResult(object):
    query_seq_id: str = attr.ib(default="")
    alignments: List[Alignment] = attr.ib(factory=list)

    seq_info: Dict[str, SeqInfo] = attr.ib(factory=dict)
    tax_info: Dict[int, Organism] = attr.ib(factory=dict)

    warnings: List[str] = attr.ib(factory=list)
    errors: List[str] = attr.ib(factory=list)
