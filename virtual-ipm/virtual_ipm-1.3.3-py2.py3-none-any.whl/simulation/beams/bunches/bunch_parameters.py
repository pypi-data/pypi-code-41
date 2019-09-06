# -*- coding: utf-8 -*-

#    Virtual-IPM is a software for simulating IPMs and other related devices.
#    Copyright (C) 2017  The IPMSim collaboration <http://ipmsim.gitlab.io/IPMSim>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals

from anna import Action, Group, Integer, Number, PhysicalQuantity
from anna.parameters import AwareParameter

from virtual_ipm.data.particle_types import ParticleType


energy = PhysicalQuantity(
    'Energy',
    unit='eV',
    info="Together with the particle type's rest energy this determines the relativistic gamma "
         "factor. Depending on the rest energy, the energy can be specified either as total "
         "energy or energy per nucleon."
)
bunch_population = Number('BunchPopulation')
# noinspection PyTypeChecker
particle_type = Action(
    Group(
        'ParticleType',
        Integer('ChargeNumber'),
        PhysicalQuantity('RestEnergy', unit='eV',
                         info='Together with the beam energy this determines the relativistic '
                              'gamma factor.')
    ),
    lambda x: ParticleType(x['ChargeNumber'], x['RestEnergy'])
)

CONFIG_PATH = 'Parameters'

aware_energy = AwareParameter(energy, CONFIG_PATH)
aware_bunch_population = AwareParameter(bunch_population, CONFIG_PATH)
aware_particle_type = AwareParameter(particle_type, CONFIG_PATH)
