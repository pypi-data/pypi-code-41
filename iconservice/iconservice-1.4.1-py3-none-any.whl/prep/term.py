# -*- coding: utf-8 -*-
# Copyright 2019 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import TYPE_CHECKING, List, Optional

from ..icon_constant import PREP_MAIN_PREPS, PREP_MAIN_AND_SUB_PREPS

if TYPE_CHECKING:
    from .data import PRep, PRepFlag, PRepContainer
    from ..base.address import Address
    from ..iconscore.icon_score_context import IconScoreContext


class Term(object):
    """Defines P-Rep Term information
    """
    _VERSION = 0

    def __init__(self):
        self._sequence: int = -1
        self._start_block_height: int = -1
        self._end_block_height: int = -1
        self._period: int = -1
        # Main and Sub P-Reps
        self._preps: List['PRep'] = []
        self._main_prep_count: int = PREP_MAIN_PREPS
        self._main_and_sub_prep_count: int = PREP_MAIN_AND_SUB_PREPS
        self._irep: int = -1
        self._total_supply: int = -1

    @property
    def sequence(self) -> int:
        return self._sequence

    @property
    def start_block_height(self) -> int:
        return self._start_block_height

    @property
    def end_block_height(self) -> int:
        return self._end_block_height

    @property
    def period(self) -> int:
        return self._period

    @property
    def main_preps(self) -> List['PRep']:
        return self._preps[:self._main_prep_count]

    @property
    def sub_preps(self) -> List['PRep']:
        return self._preps[self._main_prep_count:self._main_and_sub_prep_count]

    @property
    def preps(self) -> List['PRep']:
        return self._preps

    @property
    def irep(self) -> int:
        """Returns weighted average irep used during a term

        :return: weighted average irep that is calculated with ireps submitted by 22 Main P-Reps
        """
        return self._irep

    @property
    def total_supply(self) -> int:
        return self._total_supply

    def load(self, context: 'IconScoreContext', term_period: int):
        self._period = term_period
        data: Optional[list] = context.storage.prep.get_term(context)
        if data:
            version = data[0]
            assert version == self._VERSION

            self._sequence = data[1]
            self._start_block_height = data[2]
            self._end_block_height = self._start_block_height + term_period - 1
            self._preps: List['PRep'] = self._make_main_and_sub_preps(context, data[3])
            self._irep = data[4]
            self._total_supply = data[5]
        else:
            self._irep = 0
            self._total_supply = context.total_supply

        self._main_prep_count = context.main_prep_count
        self._main_and_sub_prep_count = context.main_and_sub_prep_count

    @staticmethod
    def _make_main_and_sub_preps(context: 'IconScoreContext', data: list) -> List['PRep']:
        """Returns tuple of Main P-Rep List and Sub P-Rep List

        :param context:
        :param data:
        :return:
        """
        prep_list: list = []
        frozen_preps: 'PRepContainer' = context.engine.prep.preps
        assert frozen_preps.is_frozen()

        for i in range(0, len(data), 2):
            address: 'Address' = data[i]
            delegated: int = data[i + 1]

            frozen_prep: 'PRep' = frozen_preps.get_by_address(address)
            assert frozen_prep.is_frozen()

            if delegated == frozen_prep.delegated:
                prep: 'PRep' = frozen_prep
            else:
                prep: 'PRep' = frozen_prep.copy()
                prep.delegated = delegated
                prep.freeze()

            assert prep.is_frozen()
            prep_list.append(prep)

        return prep_list

    def update( self, sequence: int, main_prep_count: int, main_and_sub_prep_count: int,
                current_block_height: int, preps: List['PRep'], total_supply: int, term_period: int, irep: int):
        """
        :param sequence:
        :param main_prep_count
        :param main_and_sub_prep_count
        :param current_block_height:
        :param preps:
        :param irep:
        :param total_supply:
        :param term_period: P-Rep term period in block
        :return:
        """
        self._sequence = sequence
        self._main_prep_count = main_prep_count
        self._main_and_sub_prep_count = main_and_sub_prep_count
        self._start_block_height = current_block_height + 1
        self._end_block_height = current_block_height + term_period
        self._period = term_period
        self._preps = preps[:self._main_and_sub_prep_count]  # shallow copy
        self._total_supply = total_supply
        self._irep = irep

    # def _calculate_weighted_average_of_irep(self) -> int:
    #     total_delegated = 0  # total delegated of top 22 preps
    #     total_weighted_irep = 0
    #
    #     for i in range(self._main_prep_count):
    #         prep: 'PRep' = self._preps[i]
    #         total_weighted_irep += prep.irep * prep.delegated
    #         total_delegated += prep.delegated
    #
    #     return total_weighted_irep // total_delegated if total_delegated > 0 else 0

    def save(self, context: 'IconScoreContext'):
        """Save term data to stateDB

        :param context:
        :return:
        """
        data: list = [
            self._VERSION,
            self._sequence,
            self._start_block_height,
            self._serialize_preps(self.preps),
            self._irep,
            self._total_supply
        ]
        context.storage.prep.put_term(context, data)

    @staticmethod
    def _serialize_preps(preps: List['PRep']) -> List:
        data: list = []
        for prep in preps:
            data.append(prep.address)
            data.append(prep.delegated)
        return data
