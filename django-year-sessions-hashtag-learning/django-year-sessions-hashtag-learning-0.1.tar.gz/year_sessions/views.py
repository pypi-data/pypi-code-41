from django.shortcuts import render

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from evaluations.models import Evaluation, EvaluationSession

from .forms import ChangeSessionForm


