import copy


class Sample:

    def __init__(self, experimentID, experimentName, plateName, sampleId):
        self.experimentID = experimentID
        self.experimentName = experimentName
        self.plateName = plateName
        self.sampleId = sampleId
        self.Amplicon = []
        self.amplicon_dic = {}
        self.amplicon_list = []

    def get(self):
        return self.Amplicon

    def add(self, Amplicon):
        self.Amplicon.append(Amplicon)
        self.amplicon_dic = copy.deepcopy(self.amplicon_dic)
        self.amplicon_dic["ampliconName"] = Amplicon.ampliconName
        self.amplicon_dic["snp"] = Amplicon.snp_list
        self.amplicon_list.append(self.amplicon_dic)

    def reprJSON(self):
        return dict(experimentID=self.experimentID, experimentName=self.experimentName, plateName=self.plateName, sampleId=self.sampleId, Amplicon=self.Amplicon)

    # def make_sample(experimentID, experimentName, plateName, sampleId):
#     sample = Sample(experimentID, experimentName, plateName, sampleId)
#     return sample
