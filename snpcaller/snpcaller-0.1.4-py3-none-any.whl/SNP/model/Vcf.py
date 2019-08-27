import copy

class Vcf:

    def __init__(self, chrom, pos, id, ref, alt, qual, filter, info, format, sampleid):
        self.chrom = chrom
        self.pos = pos
        self.id = id
        self.ref = ref
        self.alt = alt
        self.qual = qual
        self.filter = filter
        self.info = info
        self.format = format
        self.sampleid = sampleid