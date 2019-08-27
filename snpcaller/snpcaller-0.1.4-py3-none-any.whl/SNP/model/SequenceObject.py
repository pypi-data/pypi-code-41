class SequenceObject:
    def __init__(self, start,end,cigar,seq,chr):
        self.start = start
        self.end = end
        self.cigar = cigar
        self.seq = seq
        self.chr = chr

    def get(self):
        return self.start,self.end,self.cigar,self.seq,self.chr
