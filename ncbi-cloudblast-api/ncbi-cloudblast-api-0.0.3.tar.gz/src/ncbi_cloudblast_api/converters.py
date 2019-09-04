from ncbi.cloudblast.v1alpha import api_pb2 as cloudblast_pb2
from ncbi.cloudblast.v1alpha import blast_request_pb2

from .models import StatusReply, ResultStatus
from .result import Alignment, SearchResult, Seg
from .status import Status

from typing import List


def convert_status(reply: cloudblast_pb2.StatusReply) -> StatusReply:
    res = []
    for s in reply.status:
        res.append(ResultStatus(
            s.job_id,
            Status(s.status)
        ))
    return StatusReply(res)


def convert_resultreply(reply: cloudblast_pb2.ResultReply) -> SearchResult:
    """convert protobuf ResultReply to SearchResult"""
    if reply.HasField('failure'):
        return SearchResult(
            errors=_make_str_list(reply.failure.errors)
        )
    else:
        data = reply.results
        return SearchResult(
            alignments=_make_rows(data),
            warnings=_make_str_list(data.warnings)
        )


def _make_rows(data: cloudblast_pb2.Resultset) -> List[Alignment]:
    if not data.alignments:
        return list()

    rows = list()
    for a in data.alignments:
        r = Alignment()
        r.qseqid = data.query_seq_id
        if r.qseqid in data.seq_info:
            si = data.seq_info[r.qseqid]
            r.qaccver = si.accession
            r.qlen = si.length

        r.sseqid = a.subject_seq_id
        if r.sseqid in data.seq_info:
            si = data.seq_info[r.sseqid]
            r.saccver = si.accession
            r.stitle = si.title
            r.slen = si.length
            r.staxid = si.tax_id

            if r.staxid in data.tax_info:
                ti = data.tax_info[r.staxid]
                r.ssciname = ti.sci_name
                r. scomname = ti.common_name

        r.score = a.score
        r.evalue = a.e_value
        r.bitscore = a.bit_score
        r.nident = a.num_identical
        r.pident = a.percent_identity
        r.mismatch = a.num_mismatches
        r.gapopen = a.num_gap_opens
        r.gaps = a.num_gaps
        r.qcovs = a.percent_qry_cov_per_subject
        r.qcovhsp = a.percent_qry_cov_per_hsp
        r.length = a.alignment_length

        # query_coords and subject_coords in Alignment are
        # calculated by output translator.
        qc = a.query_coords
        r.qstart = qc.start
        r.qend = qc.stop
        r.qseq = a.aligned_query_seq

        sc = a.subject_coords
        r.sstart = sc.start
        r.send = sc.stop
        r.sseq = a.aligned_subject_seq
        r.sstrand = blast_request_pb2.NAStrand.Name(sc.strand)

        for seg in a.segments:
            r.segs.append(Seg(
                seg.length,
                seg.query_coords.start,
                seg.query_coords.stop,
                seg.subject_coords.start,
                seg.subject_coords.stop,
                blast_request_pb2.NAStrand.Name(seg.subject_coords.strand)
            ))
        rows.append(r)
    return rows


def _make_str_list(data: List[str]) -> List:
    res = []
    for s in data:
        res.append(s)
    return res
