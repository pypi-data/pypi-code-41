import numpy as np


class InputMatrix:
    # This class groups all of the related data pulled from the input file

    def __init__(self, data, groups, sampleHeaders, speciesHeaders):
        self.data = data
        self.groups = groups
        self.sampleHeaders = sampleHeaders
        self.speciesHeaders = speciesHeaders
        self.uniqueGroups = np.unique(groups)


class OutputMatrix:
    # This class groups all of the related data pulled generated as output

    def __init__(self, lotScores, compScores, lotPValues, compPValues,
                 uniqueGroups, sampleHeaders, speciesHeaders, outputArray):
        self.lotScores = lotScores
        self.compScores = compScores
        self.lotPValues = lotPValues
        self.compPValues = compPValues
        self.uniqueGroups = uniqueGroups
        self.sampleHeaders = sampleHeaders
        self.speciesHeaders = speciesHeaders
        self.outputArray = outputArray
