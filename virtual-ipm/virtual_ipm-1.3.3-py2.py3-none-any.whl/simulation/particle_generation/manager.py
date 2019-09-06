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

import six

import injector

from virtual_ipm.components import Manager
import virtual_ipm.di as di
from virtual_ipm.timings import measure_cpu_time


class ParticleGenerationManager(Manager):
    """
    This component provides functionality for generating particles during the simulation.
    """

    @injector.inject(model=di.models.particle_generation)
    def __init__(self, model):
        """
        Parameters
        ----------
        model : :class:`ParticleGenerationModel`
        """
        super(ParticleGenerationManager, self).__init__()
        self._model = model

    @measure_cpu_time
    def prepare(self):
        """
        Prepare the particle generation model.
        """
        super(ParticleGenerationManager, self).prepare()
        self._model.prepare()

    @measure_cpu_time
    def generate_particles(self, progress):
        """
        Generate the particles for the given simulation progress.

        Parameters
        ----------
        progress : :class:`Progress`
        """
        self._model.generate_particles(progress)

    def __str__(self):
        return six.text_type(self._model)
