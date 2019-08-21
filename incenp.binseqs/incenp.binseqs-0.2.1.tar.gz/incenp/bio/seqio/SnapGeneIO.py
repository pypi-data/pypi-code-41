# -*- coding: utf-8 -*-
# Copyright © 2017,2018 Damien Goutte-Gattat
#
# Redistribution and use of this script, with or without modifications,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of this script must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""SnapGene format support for Biopython

Provide read support for the binary format used by SnapGene.
"""

from datetime import datetime
from re import sub
from struct import unpack
from xml.dom.minidom import parseString

from Bio import Alphabet
from Bio.Seq import Seq
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio.SeqRecord import SeqRecord


class _SegmentIterator:

    def __init__(self, handle):
        self.handle = handle

    def __iter__(self):
        return self

    # Read a single segment from a SnapGene file.
    # A SnapGene segment is a TLV-like structure comprising of:
    # - 1 single byte indicating the segment's type;
    # - 1 big-endian long integer (4bytes) indicating the length
    #   of the segment's data;
    # - the segment's data.
    def __next__(self):
        type = self.handle.read(1)
        if len(type) < 1:   # No more segment
            raise StopIteration
        type = unpack('>B', type)[0]

        length = self.handle.read(4)
        if len(length) < 4:
            raise ValueError("Unexpected end of segment")
        length = unpack('>I', length)[0]

        data = self.handle.read(length)
        if len(data) < length:
            raise ValueError("Unexpected end of segment")

        return (type, length, data)

    # Python2 compatibility
    def next(self):
        return self.__next__()


def _parse_dna_segment(length, data, record):
    if record.seq:
        raise ValueError("The file contains more than one DNA Segment")

    flags, sequence = unpack(">B%ds" % (length - 1), data)
    record.seq = Seq(sequence.decode('ASCII'), alphabet=Alphabet.generic_dna)
    if flags & 0x01:
        record.annotations['topology'] = 'circular'
    else:
        record.annotations['topology'] = 'linear'


_months = [
    'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
    'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'
    ]


def _parse_notes_segment(length, data, record):
    xml = parseString(data.decode('ASCII'))
    type = _get_child_value(xml, 'Type')
    if type == 'Synthetic':
        record.annotations['data_file_division'] = 'SYN'
    else:
        record.annotations['data_file_division'] = 'UNC'

    date = _get_child_value(xml, 'LastModified')
    if date:
        d = datetime.strptime(date, '%Y.%m.%d')
        record.annotations['date'] = "%02d-%s-%4d" % (d.day, _months[d.month - 1], d.year)

    acc = _get_child_value(xml, 'AccessionNumber')
    if acc:
        record.id = acc

    comment = _get_child_value(xml, 'Comments')
    if comment:
        record.name = comment.split(' ', 1)[0]
        record.description = comment
        if not acc:
            record.id = record.name


def _parse_file_description_segment(length, data, record):
    cookie, seq_type, exp_version, imp_version = unpack('>8sHHH', data)
    if cookie.decode('ASCII') != 'SnapGene':
        raise ValueError("The file is not a valid SnapGene file")


def _parse_features_segment(length, data, record):
    xml = parseString(data.decode('ASCII'))
    for feature in xml.getElementsByTagName('Feature'):
        quals = {}

        type = _get_attribute_value(feature, 'type', default='misc_feature')
        label = _get_attribute_value(feature, 'name')
        if label:
            quals['label'] = [label]

        strand = +1
        directionality = int(_get_attribute_value(feature, 'directionality', default="1"))
        if directionality == 2:
            strand = -1

        location = None
        for segment in feature.getElementsByTagName('Segment'):
            rng = _get_attribute_value(segment, 'range')
            start, end = [int(x) for x in rng.split('-')]
            # Account for SnapGene's 1-based coordinates
            start = start - 1
            if not location:
                location = FeatureLocation(start, end, strand=strand)
            else:
                location = location + FeatureLocation(start, end, strand=strand)
        if not location:
            raise ValueError("Missing feature location")

        for qualifier in feature.getElementsByTagName('Q'):
            qname = _get_attribute_value(qualifier, 'name',
                    error="Missing qualifier name")
            qvalues = []
            for value in qualifier.getElementsByTagName('V'):
                if value.hasAttribute('text'):
                    qvalues.append(_decode(value.attributes['text'].value))
                elif value.hasAttribute('predef'):
                    qvalues.append(_decode(value.attributes['predef'].value))
                elif value.hasAttribute('int'):
                    qvalues.append(int(value.attributes['int'].value))
            quals[qname] = qvalues

        feature = SeqFeature(location, type=type, qualifiers=quals)
        record.features.append(feature)


def _parse_primers_segment(length, data, record):
    xml = parseString(data.decode('ASCII'))
    for primer in xml.getElementsByTagName('primer'):
        quals = {}

        name = _get_attribute_value(primer, 'name')
        if name:
            quals['label'] = [name]

        for site in primer.getElementsByTagName('BindingSite'):
            rng = _get_attribute_value(site, 'location', error="Missing binding ite location")
            start, end = [int(x) for x in rng.split('-')]

            strand = int(_get_attribute_value(site, 'boundStrand', default="0"))
            if strand == 1:
                strand = -1
            else:
                strand = +1

            feature = SeqFeature(FeatureLocation(start, end, strand=strand), type='primer_bind', qualifiers=quals)
            record.features.append(feature)


_segment_handlers = {
    0x00: _parse_dna_segment,
    0x05: _parse_primers_segment,
    0x06: _parse_notes_segment,
    0x09: _parse_file_description_segment,
    0x0A: _parse_features_segment
    }


# Helper functions to process the XML data in
# some of the segments

def _decode(text):
    return sub('<[^>]+>', '', text)


def _get_attribute_value(node, name, default=None, error=None):
    if node.hasAttribute(name):
        return _decode(node.attributes[name].value)
    elif error:
        raise ValueError(error)
    else:
        return default


def _get_child_value(node, name, default=None, error=None):
    children = node.getElementsByTagName(name)
    if children and children[0].childNodes and children[0].firstChild.nodeType == node.TEXT_NODE:
        return _decode(children[0].firstChild.data)
    elif error:
        raise ValueError(error)
    else:
        return default


def SnapGeneIterator(handle):

    record = SeqRecord(None)
    n = 0

    for type, length, data in _SegmentIterator(handle):
        if n == 0 and type != 0x09:
            raise ValueError("The file does not start with a File Description Segment")

        if type in _segment_handlers:
            _segment_handlers[type](length, data, record)

        n = n + 1

    if not record.seq:
        raise ValueError("No DNA Segment in file")

    yield record
