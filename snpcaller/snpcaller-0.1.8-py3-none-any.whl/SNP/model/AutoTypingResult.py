import copy


class AutoTypingResult:

    def __init__(self, snpVersion, targetSnpVersion):
        self.snpVersion = snpVersion
        self.targetSnpVersion = targetSnpVersion
        self.Sample = []
        self.sample_dic = {}
        self.sample_list = []

    def get(self):
        return self.Sample

    def add(self, Sample):
        self.Sample.append(Sample)
        self.sample_dic = copy.deepcopy(self.sample_dic)
        self.sample_dic["experimentID"] = Sample.experimentID
        self.sample_dic["experimentName"] = Sample.experimentName
        self.sample_dic["plateName"] = Sample.plateName
        self.sample_dic["sampleId"] = Sample.sampleId
        self.sample_dic["amplicon"] = Sample.amplicon_list
        self.sample_list.append(self.sample_dic)

    def reprJSON(self):
        return dict(snpVersion=self.snpVersion, targetSnpVersion=self.targetSnpVersion, Sample=self.Sample)

    # def make_autoTypingResult(snpVersion, targetSnpVersion):
#     autoTypingResult = AutoTypingResult(snpVersion, targetSnpVersion)
#     return autoTypingResult
