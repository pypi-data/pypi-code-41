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

from anna import PhysicalQuantity, Triplet, parametrize
from anna.utils import use_docs_from
import injector
import numpy

import virtual_ipm.di as di

from .mixin import GuidingFieldModel, CSVAdaptor2D, CSVAdaptor3D, UniformGuidingField


# noinspection PyAbstractClass,PyOldStyleClasses
class ElectricGuidingFieldModel(GuidingFieldModel):
    """
    (Abstract) Base class for electric guiding field models.
    """

    CONFIG_PATH_TO_IMPLEMENTATION = 'GuidingFields/Electric/Model'
    CONFIG_PATH = 'GuidingFields/Electric/Parameters'

    def __init__(self, configuration=None):
        super(ElectricGuidingFieldModel, self).__init__(configuration)

Interface = ElectricGuidingFieldModel


# noinspection PyOldStyleClasses
@parametrize(
    _field_vector=Triplet[PhysicalQuantity](
        'ElectricField', 'V/m'
    ).use_container(numpy.array)
)
class UniformElectricField(UniformGuidingField, ElectricGuidingFieldModel):
    """
    Constant, uniform electric field.
    """

    CONFIG_PATH = ElectricGuidingFieldModel.CONFIG_PATH

    @injector.inject(
        configuration=di.components.configuration
    )
    def __init__(self, configuration):
        super(UniformElectricField, self).__init__(configuration)


class NoElectricField(UniformElectricField):
    """
    Use this model if no electric field is present (zero electric field).
    """
    _field_vector = numpy.zeros(3, dtype=float)

    @injector.inject(
        configuration=di.components.configuration
    )
    def __init__(self, configuration=None):
        super(NoElectricField, self).__init__(configuration=configuration)


# noinspection PyOldStyleClasses
class ElectricCSVAdaptor2D(CSVAdaptor2D, ElectricGuidingFieldModel):
    """
    Electric field in two dimensions whose values are read from a CST file.
    """

    CONFIG_PATH = ElectricGuidingFieldModel.CONFIG_PATH

    @injector.inject(
        configuration=di.components.configuration
    )
    def __init__(self, configuration):
        super(ElectricCSVAdaptor2D, self).__init__(configuration)

    @use_docs_from(ElectricGuidingFieldModel)
    def eval(self, position_four_vector, progress):
        return super(ElectricCSVAdaptor2D, self).eval(position_four_vector, progress)


# noinspection PyOldStyleClasses
class ElectricCSVAdaptor3D(CSVAdaptor3D, ElectricGuidingFieldModel):
    """
    Electric field in three dimensions whose values are read from a CST file.
    """

    CONFIG_PATH = ElectricGuidingFieldModel.CONFIG_PATH

    @injector.inject(
        configuration=di.components.configuration
    )
    def __init__(self, configuration):
        super(ElectricCSVAdaptor3D, self).__init__(configuration)

    @use_docs_from(ElectricGuidingFieldModel)
    def eval(self, position_four_vector, progress):
        return super(ElectricCSVAdaptor3D, self).eval(position_four_vector, progress)
