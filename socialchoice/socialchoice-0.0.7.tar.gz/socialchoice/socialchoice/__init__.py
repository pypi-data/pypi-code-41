"""
This file holds the complete interface for this package, as everything in here can be imported as
socialchoice.{whatever} instead of socialchoice.{filename}.{whatever}

This allows us to factor out the package into multiple files while keeping a consistent user-facing API.
"""

import socialchoice.induction as pairwise_collapse
from socialchoice.ballot import (
    PairwiseBallotBox,
    RankedChoiceBallotBox,
    VoterTrackingPairwiseBallotBox,
    InvalidElectionDataException,
    InvalidBallotDataException,
)
from socialchoice.election import *
from socialchoice.induction.resolving_incompleteness import IncompletenessResolverFactory
from socialchoice.induction.resolving_intransitivity import IntransitivityResolverFactory
