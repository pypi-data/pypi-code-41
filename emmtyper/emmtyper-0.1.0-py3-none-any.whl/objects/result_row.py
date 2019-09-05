'''
Define the ResultRow class to store resultss
'''
import numpy as np

# define some known emm-like genes
PHE_emmLike = [
    "EMM51",
    "EMM134",
    "EMM138",
    "EMM149",
    "EMM156",
    "EMM159",
    "EMM164",
    "EMM167",
    "EMM170",
    "EMM174",
    "EMM202",
    "EMM205",
    "EMM236",
    "EMM240",
]

Suspects = []  # "EMM134", "EMM167",
# "EMM137", "EMM141", "EMM166", "EMM203"]

EmmImposters = PHE_emmLike + Suspects


class WrongLengthException(Exception):
    '''
    Exception to handle wrong length matches
    '''
    pass


class ResultRow:
    '''
    Store and print Blast results
    '''
    variableList = [
        "Query",
        "BlastHit",
        "Identity",
        "AlignmentLength",
        "Mismatch",
        "GapOpen",
        "QueryStart",
        "QueryEnd",
        "HitStart",
        "HitEnd",
        "E-Value",
        "BitScore",
        "SubjectLength",
    ]

    flagDict = {
        (False, True): "~",
        (True, False): "*",
        (True, True): "",
        (False, False): "~*",
    }

    def __init__(self, string):
        self.fullRow = string

        rowSplit = string.split("\t")

        if len(self.variableList) != len(rowSplit):
            raise WrongLengthException("Wrong row length!")

        rowSplit[3:10] = map(int, rowSplit[3:10])
        rowSplit[12:14] = map(int, rowSplit[12:14])

        (
            query,
            blastHit,
            identity,
            alignmentLength,
            mismatch,
            gapOpen,
            queryStart,
            queryEnd,
            hitStart,
            hitEnd,
            eValue,
            bitScore,
            subjectLength,
        ) = rowSplit

        self.query = query

        self.blastHit = blastHit
        self.type = blastHit.split(".")[0]
        self.subtype = blastHit.split(".")[1]

        self.identity = float(identity)
        self.alignmentLength = alignmentLength
        self.mismatch = mismatch
        self.gapOpen = gapOpen
        self.queryStart = queryStart
        self.queryEnd = queryEnd
        self.hitStart = hitStart
        self.hitEnd = hitEnd
        self.eValue = eValue
        self.bitScore = bitScore
        self.subjectLength = subjectLength

        # Score is percent identity, penalized by gap opening and difference in alignment length and actual subject length
        self.positions = np.array([self.query, self.queryStart, self.queryEnd])
        self.score = self.identity - (
            self.gapOpen + abs(self.alignmentLength - self.subjectLength)
        )

    def __repr__(self):
        return self.fullRow

    def __str__(self):
        if self.blastHit == "EMM0.0":
            return "-"
        else:
            return "{}{}".format(
                self.blastHit,
                ResultRow.flagDict[(self.score == 100, self.type not in EmmImposters)],
            )

    @staticmethod
    def build_header():
        header = "\t".join([variable for variable in ResultRow.variableList])

        return header + "\n"

    def filter(self, mismatch, align_diff, gap):
        return (
            self.mismatch_k(mismatch)
            and self.alignment_to_subject_length_k(align_diff)
            and self.gap_k(gap)
        )

    ### Filter functions.

    def alignment_to_subject_length_k(self, k=0):
        # Check whether alignment length is within minimum k threshold to subject length.

        return abs(self.subjectLength - self.alignmentLength) <= k

    def mismatch_k(self, k=0):
        # Accounts possibility of k mismatch(es) as okay for classification.

        return self.mismatch <= k

    def gap_k(self, k=0):
        # Check whether there are k (or less) gaps in Row instance.

        return self.gapOpen <= k

    ### Prototype filter functions. Currently not used.

    def hit_start_end_k(self, k=0):
        # Reduces need for alignment length to be same as subject length by k value.
        # Requires other functions to work well, such as mismatch functions.

        start = 1 + k
        end = self.subjectLength - k

        start_bool = self.hitStart <= start or self.hitStart >= end
        end_bool = self.hitEnd <= start or self.hitEnd >= end

        return start_bool and end_bool

    def bit_score_346(self, bit=346):
        # Check whether bit score is full.

        return self.bitScore == bit
