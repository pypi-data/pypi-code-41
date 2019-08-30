import copy

class Output:

    def __init__(self, isValid, seqName, snpName, chrom, chromStart, chromEnd, refNCBI, refUCSC, observed, rawBases1 , rawBases2, rawReads1, rawReads2, minBaseOcurrances, minBasePercentages, minBaseQualityPercentage, sequence):
        self.isValid = isValid
        self.seqName = seqName
        self.rawReads1 = rawReads1
        self.rawReads2 = rawReads2
        self.snpName = snpName
        self.chrom = chrom
        self.chromStart = chromStart
        self.chromEnd = chromEnd
        self.refNCBI = refNCBI
        self.refUCSC = refUCSC
        self.observed = observed
        self.rawBases1 = rawBases1
        self.rawBases2 = rawBases2
        self.minBaseOcurrances = minBaseOcurrances
        self.minBasePercentages = minBasePercentages
        self.minBaseQualityPercentage = minBaseQualityPercentage
        self.sequence = sequence
def make_Output(isValid, seqName, snpName, chrom, chromStart, chromEnd, refNCBI, refUCSC, observed, rawBases1, rawBases2,rawReads1, rawReads2, minBaseOcurrances, minBasePercentages, minBaseQualityPercentage, sequence):
    Output = Output(isValid, seqName, rawReads, snpName, chrom, chromStart, chromEnd, refNCBI, refUCSC, observed, rawBases, minBaseOcurrances, minBasePercentages, minBaseQualityPercentage, sequence)
    return snp
