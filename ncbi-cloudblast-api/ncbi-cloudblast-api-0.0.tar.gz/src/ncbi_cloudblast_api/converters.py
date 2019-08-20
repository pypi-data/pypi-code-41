from ncbi.cloudblast.v1alpha import api_pb2 as cloudblast_pb2
from ncbi.cloudblast.v1alpha import blast_request_pb2
from typing import Dict, List
from .models import *

# NOT USED. Keep for future reference.

# Convert protobuf objects to corresponding attr objects defined in models.py


def convert_status(reply: cloudblast_pb2.StatusReply) -> StatusReply:
    res = []
    for s in reply.status:
        res.append(ResultStatus(
            s.job_id,
            ResultStatus.Status(s.status)
        ))
    return StatusReply(res)


def convert_result(reply: cloudblast_pb2.ResultReply) -> SearchResult:
    if reply.HasField('failure'):
        return SearchResult(
            errors=_make_str_list(reply.failure.errors)
        )
    else:
        data = reply.results
        return SearchResult(
            data.query_seq_id,
            _make_alignments(data.alignments),
            _make_seq_info(data.seq_info),
            _make_tax_info(data.tax_info),
            _make_str_list(data.warnings),
            []  # errors
        )


def _make_str_list(data: List[str]) -> List:
    res = []
    for s in data:
        res.append(s)
    return res


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
            v.org,
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
