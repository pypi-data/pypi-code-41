import copy


class Amplicon:

    def __init__(self, ampliconName):
        self.ampliconName = ampliconName
        self.Snp = []
        self.snp_dic = {}
        self.snp_list = []

    def get(self):
        return self.Snp

    def add(self, Snp):
        self.Snp.append(Snp)
        self.snp_dic = copy.deepcopy(self.snp_dic)
        self.snp_dic["isValid"] = Snp.isValid
        self.snp_dic["seqName"] = Snp.seqName
        self.snp_dic["rawReads"] = Snp.rawReads
        self.snp_dic["snpName"] = Snp.snpName
        self.snp_dic["chrom"] = Snp.chrom
        self.snp_dic["chromStart"] = Snp.chromStart
        self.snp_dic["chromEnd"] = Snp.chromEnd
        self.snp_dic["refNCBI"] = Snp.refNCBI
        self.snp_dic["refUCSC"] = Snp.refUCSC
        self.snp_dic["observed"] = Snp.observed
        self.snp_dic["rawBases"] = Snp.rawBases
        self.snp_dic["minBaseOcurrances"] = Snp.minBaseOcurrances
        self.snp_dic["minBasePercentages"] = Snp.minBasePercentages
        self.snp_dic["minBaseQualityPercentage"] = Snp.minBaseQualityPercentage
        self.snp_dic["sequence"] = Snp.sequence
        self.snp_list.append(self.snp_dic)

    def reprJSON(self):
        return dict(ampliconName=self.ampliconName, Snp=self.Snp)

    # def make_amplicon(ampliconName):#rname
#     amplicon = Amplicon(ampliconName)#rname
#     return amplicon
