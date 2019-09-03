import attr
from typing import Dict, List, Optional
from enum import Enum

from ncbi.cloudblast.v1alpha import api_pb2 as cloudblast_pb2
from ncbi.cloudblast.v1alpha import blast_request_pb2
from .result import NAStrand

# !!! NOT USED !!! Kept for future reference.

# Python objects created via attrs for the corresponding
# protobuf objects as defined in public API spec.
from .status import Status


@attr.s(auto_attribs=True)
class DbInfo(object):
    name: str = ""
    tag: str = ""
    description: str = ""


@attr.s(auto_attribs=True)
class DbList(object):
    dbs: List[DbInfo] = attr.ib(factory=list)


@attr.s(auto_attribs=True)
class ResultStatus(object):
    job_id: str = ""
    status: Status = Status.RUNNING


@attr.s(auto_attribs=True)
class StatusReply(object):
    status: List[ResultStatus] = attr.ib(factory=list)


@attr.s(auto_attribs=True)
class SeqCoord(object):
    start: int = -1
    end: int = -1
    strand: NAStrand = NAStrand.UNKNOWN


@attr.s(auto_attribs=True)
class Seg(object):
    length: int = -1
    query_coords: Optional[SeqCoord] = None
    subject_coords: Optional[SeqCoord] = None


@attr.s(auto_attribs=True)
class Alignment(object):
    subject_seq_id: str = ""
    score: int = -1
    e_value: float = -1
    bit_score: float = -1
    num_identical: int = -1
    percent_identity: float = -1
    query_coords: Optional[SeqCoord] = None
    subject_coords: Optional[SeqCoord] = None
    alignment_length: int = -1
    num_mismatches: int = -1
    num_gap_opens: int = -1
    num_gaps: int = -1
    percent_qry_cov_per_subject: int = -1
    percent_qry_cov_per_unique_subject: int = -1
    percent_qry_cov_per_hsp: int = -1
    aligned_query_seq: str = ""
    aligned_subject_seq: str = ""
    segments: List[Seg] = attr.ib(factory=list)


@attr.s(auto_attribs=True)
class Infraspecies(object):
    class InfraspecificType(Enum):
        UNKNOWN = 0
        BREED = 1
        ISOLATE = 2
        CULTIVAR = 3
        STRAIN = 4

    type: InfraspecificType = InfraspecificType.UNKNOWN
    value: str = ""


@attr.s(auto_attribs=True)
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

    tax_id: int = -1
    sci_name: str = ""
    common_name: str = ""
    infra_species: Optional[Infraspecies] = None
    tax_group: TaxGroupType = TaxGroupType.UNKNOWN
    host: str = ""
    rank: RankType = RankType.NO_RANK
    genomic_moltype: str = ""


class SeqType(Enum):
    NUCLEOTIDE = 1
    PROTEIN = 2


@attr.s(auto_attribs=True)
class SeqInfo(object):
    seq_id: str = ""
    accession: str = ""
    title: str = ""
    tax_id: int = 0
    type: SeqType = SeqType.NUCLEOTIDE
    length: str = ""


def _make_tax_info(info: Dict[int, cloudblast_pb2.Organism]) -> Dict[int, Organism]:
    tax_info = dict()
    for k, v in info.items():
        tax_info[k] = Organism(
            v.tax_id,
            v.sci_name,
            v.common_name,
            _make_infra_species(v.infra_species),
            Organism.TaxGroupType(v.tax_group),
            v.host,
            Organism.RankType(v.rank),
            v.genomic_moltype
        )
    return tax_info


def _make_infra_species(spec: cloudblast_pb2.Organism.Infraspecies) -> Infraspecies:
    return Infraspecies(
        Infraspecies.InfraspecificType(spec.type),
        spec.value
    )


def _make_seq_info(info: Dict[str, cloudblast_pb2.SeqInfo]) -> Dict[str, SeqInfo]:
    seq_info = dict()
    for k, v in info.items():
        seq_info[k] = SeqInfo(
            v.seq_id,
            v.accession,
            v.title,
            v.tax_id,
            SeqType(v.type),
            v.length
        )
    return seq_info


def _make_alignments(alis: List[cloudblast_pb2.Alignment]) -> List[Alignment]:
    alignments = []
    for ali in alis:
        alignments.append(
            Alignment(
                ali.subject_seq_id,
                ali.score,
                ali.e_value,
                ali.bit_score,
                ali.num_identical,
                ali.percent_identity,
                ali.query_coords,
                ali.subject_coords,
                ali.alignment_length,
                ali.num_mismatches,
                ali.num_gap_opens,
                ali.num_gaps,
                ali.percent_qry_cov_per_subject,
                ali.percent_qry_cov_per_unique_subject,
                ali.percent_qry_cov_per_hsp,
                ali.aligned_query_seq,
                ali.aligned_subject_seq,
                _make_segments(ali.segments)
            )
        )
    return alignments


def _make_segments(segs: List[cloudblast_pb2.Alignment.Seg]) -> List[Seg]:
    segments = []
    for seg in segs:
        segments.append(
            Seg(
                seg.length,
                _make_seg_coords(seg.query_coords),
                _make_seg_coords(seg.subject_coords)
            )
        )
    return segments


def _make_seg_coords(coords: blast_request_pb2.SeqCoord) -> SeqCoord:
    return SeqCoord(
        coords.start,
        coords.stop,
        NAStrand(coords.strand)
    )
