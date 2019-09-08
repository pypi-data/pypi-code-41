# Imports from Django.
from django.urls import include, path


# Imports from other dependencies.
from rest_framework import routers


# Imports from election.
from election.viewsets import BallotAnswerViewSet
from election.viewsets import BallotMeasureViewSet
from election.viewsets import CandidateViewSet
from election.viewsets import ElectionCycleViewSet
from election.viewsets import ElectionDayViewSet
from election.viewsets import ElectionTypeViewSet
from election.viewsets import ElectionViewSet
from election.viewsets import RaceViewSet


router = routers.DefaultRouter()

router.register(r"ballot-answers", BallotAnswerViewSet)
router.register(r"ballot-measures", BallotMeasureViewSet)
router.register(r"candidates", CandidateViewSet)
router.register(r"election-cycles", ElectionCycleViewSet)
router.register(r"election-days", ElectionDayViewSet)
router.register(r"election-types", ElectionTypeViewSet)
router.register(r"elections", ElectionViewSet)
router.register(r"races", RaceViewSet)

urlpatterns = [path("api/", include(router.urls))]
