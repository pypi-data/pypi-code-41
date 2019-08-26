import copy

class PacBioObject:

    def __init__(self, jobName, experimentName, sampleID, barcodeID, experimentID):
        self.jobName = jobName
        self.experimentName = experimentName
        self.sampleID = sampleID
        self.barcodeID = barcodeID
        self.experimentID = experimentID


    def reprJSON(self):
        return dict(jobName=self.jobName, experimentName=self.experimentName, sampleID=self.sampleID, barcodeID=self.barcodeID, experimentID=self.experimentID)

def make_PacBioObject(jobName, experimentName, sampleID, barcodeID,experimentID):
    pacBioObject = PacBioObject(jobName, experimentName, sampleID, barcodeID,experimentID)
    return pacBioObject
