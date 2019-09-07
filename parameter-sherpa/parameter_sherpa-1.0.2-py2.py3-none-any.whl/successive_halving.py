"""
SHERPA is a Python library for hyperparameter tuning of machine learning models.
Copyright (C) 2018  Lars Hertel, Peter Sadowski, and Julian Collado.

This file is part of SHERPA.

SHERPA is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

SHERPA is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with SHERPA.  If not, see <http://www.gnu.org/licenses/>.
"""
from .algorithms import Algorithm

class SuccessiveHalving(Algorithm):
    def __init__(self, min_iterations, max_iterations, eta):
        pass

    def get_suggestion(self, parameters, results, lower_is_better):
        for bracket in hyperband:
            for trial in bracket:
                return trial

            while not bracket.done:
                return self._get_promotable_trial(bracket)
        # return random seed

        # if no random seeds for this bracket left, get first trial to be promoted

        # if no trial is waiting to be promoted, start seed trial from next bracket

        # if there are no more brackets, return None


        for trial in bracket:
            return trial

    def _get_promotable_trial(self, results, R, eta, bracket, rung):
        """
        From knowing R and eta we know how many brackets there are

        From knowing the bracket we can get the range of Trial-IDs, but better to filter by bracket

        Helpful to add a 'rung' field to the results, maybe even a 'bracket' field

        Return None if there is no trial that can be promoted: either there are
        not enough trials yet i.e. if we have < n_{i-1} - n_i
        """


    def _get_seed_trial(self):
        """
        Return random seed trial with correct bracket notation and ``save_to``
        field. If no random seed left return None
        """