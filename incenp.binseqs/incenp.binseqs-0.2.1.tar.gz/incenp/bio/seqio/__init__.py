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

"""Support for binary sequence formats in Biopython

Load this module to enable support of SnapGene and Xdna
formats in Biopython's SeqIO.
"""

from Bio import SeqIO

if not 'gck' in SeqIO._FormatToIterator:

    from . import GckIO
    from . import SnapGeneIO
    from . import XdnaIO

    SeqIO._FormatToIterator['gck'] = GckIO.GckIterator
    SeqIO._BinaryFormats.append('gck')

    SeqIO._FormatToIterator['snapgene'] = SnapGeneIO.SnapGeneIterator
    SeqIO._BinaryFormats.append('snapgene')

    SeqIO._FormatToIterator['xdna'] = XdnaIO.XdnaIterator
    SeqIO._FormatToWriter['xdna'] = XdnaIO.XdnaWriter
    SeqIO._BinaryFormats.append('xdna')

else:
    import warnings
    warnings.warn("Your Biopython installation already has support for the "
                  "Gck, SnapGene, and Xdna formats. You no longer need to "
                  "load the incenp.bio.seqio module",
                  DeprecationWarning)
