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

from __future__ import absolute_import, print_function, unicode_literals

import inspect
import os
import pprint
import six

from anna import JSONAdaptor, XMLAdaptor
from anna.exceptions import InvalidPathError
from anna.frontends.qt.views import ParametrizedComponentView

import virtual_ipm.simulation.beams.bunches.electric_field_models as bunch_fields_models
import virtual_ipm.simulation.beams.bunches.shapes as bunch_shapes
import virtual_ipm.simulation.devices.models as devices
import virtual_ipm.simulation.output as output_recorder
import virtual_ipm.simulation.particle_generation.models as particle_factories
import virtual_ipm.simulation.particle_tracking.em_fields.guiding_fields.models as \
    guiding_fields_models
import virtual_ipm.simulation.particle_tracking.models as particle_tracking_models
import virtual_ipm.simulation.setup as simulation
from virtual_ipm.simulation.beams.factory import Beam
import virtual_ipm.simulation.beams.factory as beam_factory
import virtual_ipm.simulation.beams.bunch_trains as bunch_trains
from virtual_ipm.utils import with_logger

from . import pyqt45

QtCore = pyqt45.QtCore
QtGui = pyqt45.QtGui
Widgets = pyqt45.Widgets


@with_logger(__name__)
@six.python_2_unicode_compatible
class InterfaceView(Widgets.QWidget):
    interface_name = ''

    # noinspection PyArgumentList,PyShadowingBuiltins
    def __init__(self, interface, module, parent=None):
        super(InterfaceView, self).__init__(parent=parent, flags=QtCore.Qt.Widget)

        self._interface = interface
        self.logger.debug('Using interface %s', self._interface)

        model_classes = filter(
            lambda cls: (
                issubclass(cls, self._interface)
                and cls is not self._interface
                and not inspect.isabstract(cls)
            ),
            filter(
                lambda obj: isinstance(obj, type),
                map(
                    lambda obj_str: getattr(module, obj_str),
                    dir(module)
                )
            )
        )
        self.logger.debug('Loaded the following classes: %s', pprint.pformat(model_classes))

        layout = Widgets.QVBoxLayout()
        layout.addWidget(Widgets.QLabel('Select the %s:' % self._interface.__name__))

        self._model_view = Widgets.QStackedWidget()
        self._model_dropdown = Widgets.QComboBox()
        for model in model_classes:
            self._model_dropdown.addItem(model.__name__, model)
            self._model_view.addWidget(ParametrizedComponentView(model))

        h_layout = Widgets.QHBoxLayout()
        h_layout.addWidget(self._model_dropdown)
        h_layout.addStretch(1)

        layout.addLayout(h_layout)
        layout.addWidget(self._model_view)

        self.setLayout(layout)

        # noinspection PyUnresolvedReferences
        self._model_dropdown.currentIndexChanged.connect(self._model_view.setCurrentIndex)

    def __str__(self):
        return six.text_type(self._model_dropdown.currentText())

    def dump_as_xml(self):
        return self.dump_as('xml')

    def dump_as_json(self):
        return self.dump_as('json')

    def dump_as(self, format_):
        config = self._model_view.currentWidget().dump_as(format_)
        current_model = pyqt45.currentDataAsObject(self._model_dropdown)
        self.logger.debug(
            'Saving model %s @ %s',
            current_model.__name__, self._interface.CONFIG_PATH_TO_IMPLEMENTATION
        )
        config.insert_element(
            self._interface.CONFIG_PATH_TO_IMPLEMENTATION,
            six.text_type(current_model.__name__),
            replace=True
        )
        return config

    def load_from_source(self, configuration):
        model_name = configuration.get_text(self._interface.CONFIG_PATH_TO_IMPLEMENTATION)
        self.logger.debug('Load model %s' % model_name)
        index_and_model = filter(
            lambda t: t[1] == model_name,
            map(
                lambda i: (i, self._model_dropdown.itemText(i)),
                range(self._model_dropdown.count())
            )
        )
        try:
            index = list(index_and_model)[0][0]
        except IndexError:
            raise ValueError('Unknown %s model: %s' % (self._interface.__name__, model_name))
        self._model_dropdown.setCurrentIndex(index)
        self._model_view.currentWidget().load_from_source(configuration)


# noinspection PyOldStyleClasses
@with_logger(__name__)
class InterfaceViewByModule(InterfaceView):
    MODULE = None

    def __init__(self, parent=None):
        if self.MODULE is None:
            raise TypeError(
                '%s must define attribute `MODULE`'
                % self.__class__.__name__
            )
        super(InterfaceViewByModule, self).__init__(
            getattr(self.MODULE, str('Interface')),
            self.MODULE,
            parent=parent
        )

    def set_focus_on_input(self, origin):
        self.setFocus()
        origin.setFocus()


# noinspection PyOldStyleClasses
@with_logger(__name__)
class Device(InterfaceViewByModule):
    MODULE = devices

    def __init__(self, parent=None):
        super(Device, self).__init__(parent=parent)


# noinspection PyOldStyleClasses
@with_logger(__name__)
class ElectricGuidingField(InterfaceViewByModule):
    MODULE = guiding_fields_models.electric

    def __init__(self, parent=None):
        super(ElectricGuidingField, self).__init__(parent=parent)


# noinspection PyOldStyleClasses
@with_logger(__name__)
class MagneticGuidingField(InterfaceViewByModule):
    MODULE = guiding_fields_models.magnetic

    def __init__(self, parent=None):
        super(MagneticGuidingField, self).__init__(parent=parent)


# noinspection PyOldStyleClasses
@with_logger(__name__)
class ParticleGeneration(InterfaceViewByModule):
    MODULE = particle_factories

    def __init__(self, parent=None):
        super(ParticleGeneration, self).__init__(parent=parent)


# noinspection PyOldStyleClasses
@with_logger(__name__)
class ParticleTracking(InterfaceViewByModule):
    MODULE = particle_tracking_models

    def __init__(self, parent=None):
        super(ParticleTracking, self).__init__(parent=parent)


# noinspection PyOldStyleClasses
@with_logger(__name__)
class Simulation(ParametrizedComponentView):
    def __init__(self, parent=None):
        super(Simulation, self).__init__(simulation.Setup, parent=parent)

    def set_focus_on_input(self, origin):
        self.setFocus()
        origin.setFocus()


# noinspection PyOldStyleClasses
@with_logger(__name__)
class Output(InterfaceViewByModule):
    MODULE = output_recorder

    def __init__(self, parent=None):
        super(Output, self).__init__(parent=parent)


# noinspection PyOldStyleClasses
class BunchShape(InterfaceViewByModule):
    MODULE = bunch_shapes

    def __init__(self, parent=None):
        super(BunchShape, self).__init__(parent=parent)


# noinspection PyOldStyleClasses
class BunchElectricFieldModel(InterfaceViewByModule):
    MODULE = bunch_fields_models

    def __init__(self, parent=None):
        super(BunchElectricFieldModel, self).__init__(parent=parent)


@six.python_2_unicode_compatible
class BunchWithFields(Widgets.QWidget):
    # noinspection PyArgumentList
    def __init__(self, parent=None):
        super(BunchWithFields, self).__init__(parent=parent)

        self.bunch = BunchShape()
        self.bunch_fields = BunchElectricFieldModel()

        layout = Widgets.QVBoxLayout()
        layout.addWidget(self.bunch)

        line = Widgets.QFrame(flags=QtCore.Qt.Widget)
        line.setFrameShape(Widgets.QFrame.HLine)
        line.setFrameShadow(Widgets.QFrame.Sunken)
        layout.addWidget(line)

        layout.addWidget(self.bunch_fields)
        self.setLayout(layout)

    def __str__(self):
        return '%s\n%s' % (six.text_type(self.bunch), six.text_type(self.bunch_fields))

    def dump_as_json(self):
        return self.dump_as('json')

    def dump_as_xml(self):
        return self.dump_as('xml')

    def dump_as(self, format_):
        if format_ == 'xml':
            config = XMLAdaptor()
        elif format_ == 'json':
            config = JSONAdaptor()
        else:
            raise ValueError(
                'format_ must be either "xml" or "json" (got "%s" instead)'
                % format_
            )
        config.insert_config('', self.bunch.dump_as(format_))
        config.insert_config('', self.bunch_fields.dump_as(format_))
        return config

    def load_from_source(self, config):
        self.bunch.load_from_source(config)
        self.bunch_fields.load_from_source(config)


class BunchTrain(Widgets.QWidget):
    TAG = 'BunchTrain'

    # noinspection PyArgumentList
    def __init__(self, parent=None):
        super(BunchTrain, self).__init__(parent=parent, flags=QtCore.Qt.Widget)

        self._view = InterfaceView(bunch_trains.BunchTrain, bunch_trains)
        layout = Widgets.QVBoxLayout()
        layout.addWidget(self._view)
        self.setLayout(layout)

    def dump_as(self, format_):
        return self._view.dump_as(format_)

    def load_from_source(self, config):
        self._view.load_from_source(config)


# noinspection PyOldStyleClasses
@with_logger(__name__)
class BeamParameters(ParametrizedComponentView):
    def __init__(self, parent=None):
        super(BeamParameters, self).__init__(Beam, parent=parent)


@six.python_2_unicode_compatible
class NewBeamDialog(Widgets.QDialog):
    # noinspection PyArgumentList
    def __init__(self, parent=None):
        super(NewBeamDialog, self).__init__(parent=parent, flags=QtCore.Qt.Dialog)

        self.setWindowTitle('New Beam')

        v_layout = Widgets.QVBoxLayout()

        self._tab_widget = tab_widget = Widgets.QTabWidget()

        self.beam_parameters = BeamParameters()
        tab_widget.addTab(self.beam_parameters, 'Beam')

        self.bunch_with_fields = BunchWithFields()
        tab_widget.addTab(self.bunch_with_fields, 'Bunch')

        self.beam_layout = BunchTrain()
        tab_widget.addTab(self.beam_layout, 'Bunch Train')

        v_layout.addWidget(tab_widget)

        line = Widgets.QFrame()
        line.setFrameShape(Widgets.QFrame.HLine)
        line.setFrameShadow(Widgets.QFrame.Sunken)
        v_layout.addWidget(line)

        ok_button = Widgets.QPushButton('Ok')
        # noinspection PyUnresolvedReferences
        ok_button.clicked.connect(self.accept)

        cancel_button = Widgets.QPushButton('Cancel')
        # noinspection PyUnresolvedReferences
        cancel_button.clicked.connect(self.reject)

        button_layout = Widgets.QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        v_layout.addLayout(button_layout)

        container_widget = Widgets.QWidget()
        container_widget.setLayout(v_layout)

        scroll_area = Widgets.QScrollArea()
        scroll_area.setWidget(container_widget)
        scroll_area.setWidgetResizable(True)

        v_layout = Widgets.QVBoxLayout()
        v_layout.addWidget(scroll_area)
        self.setLayout(v_layout)

    def __str__(self):
        return six.text_type(self.bunch_with_fields)

    def dump_as_json(self):
        return self.dump_as('json')

    def dump_as_xml(self):
        return self.dump_as('xml')

    def dump_as(self, format_):
        if format_ == 'xml':
            config = XMLAdaptor()
        elif format_ == 'json':
            config = JSONAdaptor()
        else:
            raise ValueError(
                'format_ must be either "xml" or "json" (got "%s" instead)'
                % format_
            )
        config.insert_config('', self.beam_parameters.dump_as(format_))
        config.insert_config('', self.bunch_with_fields.dump_as(format_))
        config.insert_config('', self.beam_layout.dump_as(format_))
        return config

    def load_from_source(self, config):
        self.beam_parameters.load_from_source(config)
        self.bunch_with_fields.load_from_source(config)
        self.beam_layout.load_from_source(config)

    def set_focus_on_input(self, origin):
        parent_chain = []

        def add_parent(widget):
            if widget.parent() is not None:
                parent_chain.append(widget.parent())
                add_parent(widget.parent())

        add_parent(origin)

        if self.beam_parameters in parent_chain:
            self._tab_widget.setCurrentWidget(self.beam_parameters)
        elif self.bunch_with_fields in parent_chain:
            self._tab_widget.setCurrentWidget(self.bunch_with_fields)
        elif self.beam_layout in parent_chain:
            self._tab_widget.setCurrentWidget(self.beam_layout)
        origin.setFocus()


class Beams(Widgets.QWidget):
    # noinspection PyArgumentList
    def __init__(self, parent=None):
        super(Beams, self).__init__(parent=parent, flags=QtCore.Qt.Widget)

        self.beams = []

        v_layout = Widgets.QVBoxLayout()
        v_layout.addWidget(Widgets.QLabel('<b>%s</b>' % self.__class__.__name__))
        v_layout.addWidget(Widgets.QLabel('Configure beams:'))

        new_beam_button = Widgets.QPushButton(
            QtGui.QIcon(os.path.join(
                os.path.split(__file__)[0],
                'icons/add_plus.png'
            )),
            'New beam'
        )
        new_beam_button_layout = Widgets.QHBoxLayout()
        new_beam_button_layout.addStretch(1)
        new_beam_button_layout.addWidget(new_beam_button)
        new_beam_button_layout.addStretch(1)
        v_layout.addLayout(new_beam_button_layout)
        # noinspection PyUnresolvedReferences
        new_beam_button.clicked.connect(self._append_beam)

        v_layout.addStretch(1)
        self.setLayout(v_layout)

    def _append_beam(self):
        dialog = NewBeamDialog(self)
        dialog.setSizePolicy(Widgets.QSizePolicy.Expanding, Widgets.QSizePolicy.Expanding)
        dialog.resize(self.parent().size())
        if dialog.exec_():
            self._append_beam_from_dialog(dialog)

    def _append_beam_from_dialog(self, dialog):
        self.beams.append(dialog)

        def show_beam_dialog():
            dialog.show()

        beam_dialog_button = Widgets.QPushButton()
        # noinspection PyUnresolvedReferences
        beam_dialog_button.clicked.connect(show_beam_dialog)

        def adjust_title():
            beam_dialog_button.setText(
                '{0}\n(id: {1})'.format(
                    six.text_type(dialog),
                    self.beams.index(dialog)
                )
            )

        adjust_title()
        dialog.accepted.connect(adjust_title)

        self.layout().insertWidget(self.layout().count() - 2, beam_dialog_button)

    def dump_as_json(self):
        return self.dump_as('json')

    def dump_as_xml(self):
        return self.dump_as('xml')

    def dump_as(self, format_):
        if format_ == 'xml':
            config = XMLAdaptor()
        elif format_ == 'json':
            config = JSONAdaptor()
        else:
            raise ValueError(
                'format_ must be either "xml" or "json" (got "%s" instead)'
                % format_
            )
        for index, beam in enumerate(self.beams):
            config.insert_config('Beams/Beam[{0}]'.format(index), beam.dump_as(format_))
        return config

    def load_from_source(self, configuration):
        try:
            beam_configs = configuration.get_sub_configurations(six.text_type(Beams.__name__))
        except InvalidPathError:
            pass
        else:
            for beam_config in beam_configs:
                dialog = NewBeamDialog(self)
                dialog.load_from_source(beam_config)
                self._append_beam_from_dialog(dialog)

    def set_focus_on_input(self, origin):
        parent_chain = []

        def add_parent(widget):
            if widget.parent() is not None:
                parent_chain.append(widget.parent())
                add_parent(widget.parent())

        add_parent(origin)

        relevant_beam = list(filter(
            lambda beam: beam in parent_chain,
            self.beams
        ))

        if relevant_beam:
            relevant_beam[0].show()
            relevant_beam[0].set_focus_on_input(origin)
