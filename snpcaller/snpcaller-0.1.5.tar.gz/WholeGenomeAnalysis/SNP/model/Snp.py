import copy

class Snp:

    def __init__(self, isValid, seqName, rawReads, snpName, chrom, chromStart, chromEnd, refNCBI, refUCSC, observed, rawBases, minBaseOcurrances, minBasePercentages, minBaseQualityPercentage, sequence):
        self.isValid = isValid
        self.seqName = seqName
        self.rawReads = rawReads
        self.snpName = snpName
        self.chrom = chrom
        self.chromStart = chromStart
        self.chromEnd = chromEnd
        self.refNCBI = refNCBI
        self.refUCSC = refUCSC
        self.observed = observed
        self.rawBases = rawBases
        self.minBaseOcurrances = minBaseOcurrances
        self.minBasePercentages = minBasePercentages
        self.minBaseQualityPercentage = minBaseQualityPercentage
        self.sequence = sequence

    def reprJSON(self):
        return dict(isValid=self.isValid, seqName=self.seqName, rawReads=self.rawReads, snpName=self.snpName, chrom=self.chrom, chromStart=self.chromStart, chromEnd=self.chromEnd
                    ,refNCBI=self.refNCBI, refUCSC=self.refUCSC, observed=self.observed, rawBases=self.rawBases, minBaseOcurrances=self.minBaseOcurrances
                    , minBasePercentages=self.minBasePercentages, minBaseQualityPercentage=self.minBaseQualityPercentage, sequence=self.sequence)

def make_snp(isValid, seqName, rawReads, snpName, chrom, chromStart, chromEnd, refNCBI, refUCSC, observed, rawBases, minBaseOcurrances, minBasePercentages, minBaseQualityPercentage, sequence):
    snp = Snp(isValid, seqName, rawReads, snpName, chrom, chromStart, chromEnd, refNCBI, refUCSC, observed, rawBases, minBaseOcurrances, minBasePercentages, minBaseQualityPercentage, sequence)
    return snp
