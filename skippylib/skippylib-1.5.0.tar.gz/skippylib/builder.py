# -*- coding: utf-8 -*-
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

from .abstracts import AbstractSkippyObj
from .attributes import SkippyReadAttribute, SkippyReadWriteAttribute
from copy import copy
import functools
import PyTango
import traceback

__author__ = "Sergi Blanch-Torné"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2017, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"


def AttrExc(function):
    '''Decorates commands so that the exception is logged and also raised.
    '''
    # TODO: who has self._trace?
    def nestedMethod(self, attr, *args, **kwargs):
        inst = self  # < for pychecker
        try:
            return function(inst, attr, *args, **kwargs)
        except Exception as exc:
            traceback.print_exc(exc)
            # self._trace = traceback.format_exc(exc)
            raise
    functools.update_wrapper(nestedMethod, function)
    return nestedMethod


def latin1(x):
    return x.decode('utf-8').replace(u'\u2070', u'\u00b0').\
        replace(u'\u03bc', u'\u00b5').encode('latin1')


class Builder(AbstractSkippyObj):

    __device = None

    def __init__(self, *args, **kwargs):
        super(Builder, self).__init__(*args, **kwargs)
        if hasattr(self._parent, '_parent'):  # TODO: and it is a tango device
            self.__device = self._parent._parent
        self._attributeList = list()
        self._attributeIds = {}
        self.locals_ = {}

        self.globals_ = globals()
        self.globals_.update({
            'Attribute': self.add_Attribute
        })

    def parseFile(self, fName):
        # self.__device.debug_stream('%30s\t%10s\t%5s\t%6s\t%6s'
        #                            % ("attrName", "Type", 'RO/RW', "read",
        #                               "write"))
        self.info_stream("Start parsing the attribute file: %s" % (fName))
        try:
            execfile(str(fName), self.globals_, self.locals_)
        except Exception as e:
            self.error_stream("Builder.parseFile(%s) failed" % (fName))
            self.debug_stream("Exception: %s\n%s"
                              % (e, traceback.format_exc()))
        self.debug_stream('Parse of the attribute file done.')

    def parse(self, text):
        exec(text, self.globals_, self.locals_)

    def add_Attribute(self, attributeName, attributeDefinition):
        '''Method to dynamically add an attribute
           The parameter is a the name of the attribute, followed by a
           dictionary with mandatory keys:
           - type: tango data type of the attribute
           - dim:  dimensions of the attribute.
                   it can be: 0 for scalars
                             [1,X] for spectrums and its length
                             [2,X,Y] for images and its dimensions
           - readCmd: method to be called to have the scpi read command
           There are also optional keys:
           - writeCmd:  method to be called to have the scpi write command
           - delayAfterWrite: to specify that this single command needs an
                              extra time until next communication with the
                              instrument
           - channels:  boolean to indicate if this must be replicated
                        per all the channels
           - functions: boolean to indicate if this must be replicated
                        per all the functions
           - format:    format to display information
           - label:     human string about the attribute
           - description: longer text for humans
           - unit:      extra attribute information
           - min/max:   ranges
           - memorized: to be stored the writes in a database
           TODO: attribute input validation
           TODO: dependencies between attributes (state-like, mode,...)
           TODO: expert attributes flag
           TODO: formulas to transform input before send and write after
                 receive.
            - readFormula: evaluable string to be applied to the answer from
                           the instrument to modify it to become the device
                           answer to the attribute.
            TODO writeFormula: evaluable string to be applied to the value set
                            to an attribute before format the string to be
                            send to the instrument.
        '''
        # preconditions
        if not type(attributeDefinition) == dict:
            raise AttributeError("Invalid definition of the attribute %s"
                                 % (attributeName))
        for k in ['type', 'dim', 'readCmd']:
            if k not in attributeDefinition:
                msg = "In %s Invalid definition, key %s is mandatory"\
                    % (attributeName, k)
                self.error_stream(msg)
                raise KeyError(msg)

        # If the attribute definition includes channels and functions,
        # do it in loop
        if 'channels' in attributeDefinition or \
                'functions' in attributeDefinition or \
                'multiple' in attributeDefinition:
            self.__prepareChannelLikeGroup(attributeName, attributeDefinition)
        # when is a single attribute, no loop required
        else:
            try:
                self.__getAttrObj(attributeName, attributeDefinition)
                self.__setup_switch_attr(attributeName, attributeDefinition)
                self.__setup_data_format_attr(
                    attributeName, attributeDefinition)
                self.__setup_data_origin_attr(
                    attributeName, attributeDefinition)
                self.__setup_data_increment_attr(
                    attributeName, attributeDefinition)
                self.debug_stream("Added attribute: %s" % (attributeName))
            except Exception as e:
                self.error_stream("NOT added normal attribute: "
                                  "{a!r} due to exception: {e}"
                                  "".format(a=attributeName, e=e))
                traceback.print_exc()

    def __prepareChannelLikeGroup(self, attributeName, attributeDefinition):
        if 'channels' in attributeDefinition and \
                attributeDefinition['channels']:
            if self._parent.nChannels < 0:
                raise ValueError("Could not prepare channels for %s because "
                                 "not well defined the device property about "
                                 "how many have to be created (%d)"
                                 % (attributeName, self._parent.nChannels))
            elif self._parent.nChannels == 0:
                pass  # self.debug_stream("No channels to define")
            else:
                self.__buildGroup(attributeName, attributeDefinition,
                                  self._parent.nChannels, "Ch")
        if 'functions' in attributeDefinition and \
                attributeDefinition['functions']:
            if self._parent.nFunctions < 0:
                raise ValueError("Could not prepare functions for %s because "
                                 "not well defined the device property about "
                                 "how many have to be created (%d)"
                                 % (attributeName, self._parent.nFunctions))
            elif self._parent.nFunctions == 0:
                pass  # self.debug_stream("No function to define")
            else:
                self.__buildGroup(attributeName, attributeDefinition,
                                  self._parent.nFunctions, "Fn")
        if 'multiple' in attributeDefinition and \
                attributeDefinition['multiple']:
            try:
                attrSuffix = attributeDefinition['multiple']['attrSuffix']
                first, last = self.__checkNumberOfMultiple(
                    attributeName, attributeDefinition['multiple'])

                self.__buildGroup(attributeName, attributeDefinition, last,
                                  attrSuffix, first)
            except Exception as e:
                self.error_stream("NOT added multiple attribute: "
                                  "{a!r} due to exception: {e}"
                                  "".format(a=attributeName, e=e))
                traceback.print_exc()

    def __checkNumberOfMultiple(self, attributeName, multipleDefinition):
        if 'startAt' in multipleDefinition:
            first = multipleDefinition['startAt']
        else:
            first = 1
        scpiPrefix = multipleDefinition['scpiPrefix'].lower()
        number = None
        e = "Could not prepare 'Multiple' attributes for %s " % (attributeName)
        if len(self._parent.nMultiple) > 0:
            for element in self._parent.nMultiple:
                element = element.lower()
                if element.startswith("%s:" % scpiPrefix):
                    try:
                        _, number = element.split('%s:' % (scpiPrefix))
                        number = int(number)
                        break
                    except:
                        number = -1
                        break
            if number == -1:
                e += "because element %r of NumMultiple property "\
                    "couldn't be interpreted correctly." % (element)
            elif number is None:
                e += "because no description in NumMultiple property "\
                    "has %s." % (scpiPrefix)
            else:
                last = number+first-1
                return first, last
        else:
            e += "because not well defined the device property about "\
                "how many have to be created."
        raise ValueError(e)

    def __buildGroup(self, name, definition, number, attrSuffix, startAt=1):
        attrName = "%s%s" % (name, attrSuffix)
        self.debug_stream(
            "preparing to build {a} as a group of {n} (starting at {s})"
            "".format(a=attrName, n=number, s=startAt))
        for i in range(startAt, number+1):
            defcopy = copy(definition)
            if attrSuffix in ['Ch', 'Fn']:
                if attrSuffix == 'Ch':
                    ch, fn, multiple = i, None, None
                if attrSuffix == 'Fn':
                    ch, fn, multiple = None, i, None
            else:
                ch, fn, multiple = None, None, i
            try:
                self.__getAttrObj("%s%d" % (attrName, i),
                                  defcopy, channel=ch, function=fn,
                                  multiple=multiple)
                self.__setup_switch_attr(name, definition, attrSuffix, i)
                self.__setup_data_format_attr(name, definition)
                self.__setup_data_origin_attr(name, definition)
                self.__setup_data_increment_attr(name, definition)
                self.debug_stream("Added attribute: "
                                  "{name}{seq:d}".format(name=attrName, seq=i))
            except Exception as e:
                self.error_stream("NOT added attribute: %s%d due to "
                                  "exception: %s" % (attrName, i, e))
                traceback.print_exc()

    def _generateAttrId(self, attrName):
        id = 0
        idLst = self._attributeIds.keys()
        while id in idLst:
            id += 1
        self._attributeIds[id] = attrName
        return id

    def _getAttrNameById(self, id):
        if id in self._attributeIds:
            return self._attributeIds[id]
        if self.__device is not None:
            multiattr = self.__device.get_device_attr()
            attrObj = multiattr.get_attr_by_ind(id)
            attrName = attrName = attrObj.get_name()
            if id not in self._attributeIds:
                self._attributeIds[id] = attrName
            return attrName
        raise KeyError("id %d not found in %s"
                       % (id, self._attributeIds.keys()))

    def __getAttrObj(self, attrName, definition, channel=None, function=None,
                     multiple=None):
        # TODO: image dimensions
        if self.__device is not None:
            if definition['dim'] == [0]:
                if 'writeCmd' in definition:
                    attr = PyTango.Attr(attrName, definition['type'],
                                        PyTango.READ_WRITE)
                    readmethod = AttrExc(getattr(self.__device, 'read_attr'))
                    writemethod = AttrExc(getattr(self.__device, 'write_attr'))
                else:
                    attr = PyTango.Attr(attrName, definition['type'],
                                        PyTango.READ)
                    readmethod = AttrExc(getattr(self.__device, 'read_attr'))
                    writemethod = None
            elif definition['dim'][0] == 1:
                if 'writeCmd' in definition:
                    attr = PyTango.SpectrumAttr(attrName, definition['type'],
                                                PyTango.READ_WRITE,
                                                definition['dim'][1])
                    readmethod = AttrExc(getattr(self.__device, 'read_attr'))
                    writemethod = AttrExc(getattr(self.__device, 'write_attr'))
                else:
                    attr = PyTango.SpectrumAttr(attrName, definition['type'],
                                                PyTango.READ,
                                                definition['dim'][1])
                    readmethod = AttrExc(getattr(self.__device, 'read_attr'))
                    writemethod = None
            else:
                raise AttributeError("Not supported multiple dimensions")
            # attribute properties
            aprop = PyTango.UserDefaultAttrProp()
            if 'unit' in definition:
                aprop.set_unit(latin1(definition['unit']))
            if 'min' in definition:
                aprop.set_min_value(str(definition['min']))
            if 'max' in definition:
                aprop.set_max_value(str(definition['max']))
            if 'format' in definition:
                format = latin1(definition['format'])
                if format.count("%") == 2:
                    format = format.replace('%', '', 1)
                aprop.set_format(format)
            if 'description' in definition:
                aprop.set_description(latin1(definition['description']))
            if 'label' in definition:
                aprop.set_label(latin1(definition['label']))
            if 'memorized' in definition:
                attr.set_memorized()
                attr.set_memorized_init(True)
            attr.set_default_properties(aprop)
            self.__device.add_attribute(attr, r_meth=readmethod,
                                        w_meth=writemethod)
            multiattr = self.__device.get_device_attr()
            attrId = multiattr.get_attr_ind_by_name(attrName)
            self._attributeIds[attrId] = attrName
        else:
            attrId = self._generateAttrId(attrName)
            attr = None
            aprop = None
        # self.debug_stream("Attribute %s has the id %s" % (attrName, attrId))
        self._attributeList.append(attrName)
        # prepare internal structure ---
        if channel is not None or function is not None or multiple is not None:
            if channel is not None:
                like = "channel"
                number = channel
            elif function is not None:
                like = "function"
                number = function
            elif multiple is not None and \
                    'scpiPrefix' in definition['multiple'] and\
                    'attrSuffix' in definition['multiple']:
                like = definition['multiple']['scpiPrefix']
                number = multiple
            else:
                raise AttributeError("Wrong definition of multiple attribute")
            self.__prepareChannelLikeAttr(like, number, definition, attrName)
        else:
            readCmd = definition['readCmd']
            if 'writeCmd' not in definition:
                # writeCmd = definition['writeCmd']
                definition['writeCmd'] = None
        if 'readFormula' not in definition:
            # readFormula = definition['readFormula']
            definition['readFormula'] = None
        # if 'writeFormula' not in definition:
        #     # writeFormula = definition['writeFormula']
        #     writeFormula = None
        # build internal structure ---
        if 'rampeable' in definition and definition['rampeable'] is True:
            self.__buildRWObj(attrName, attrId, definition, readmethod,
                              writemethod)
        if 'delayAfterWrite' not in definition:
            definition['delayAfterWrite'] = 0.0
        if definition['writeCmd'] is None:
            self.__buildROObj(attrName, attrId, definition)
        else:
            self.__buildRWObj(attrName, attrId, definition)
            if 'writeValues' in definition:
                self.__prepareWriteValues(attrName, definition, aprop, attr)
        return attr

    def __setup_switch_attr(self, attrName, definition,
                            attrSuffix=None, number=None):
        if 'switch' in definition:
            switchName = definition['switch']
            if attrSuffix:
                switchName = "{0}{1}{2}".format(switchName, attrSuffix, number)
            self.debug_stream(
                "{0} has {1} as switch attribute".format(attrName, switchName))
            if attrSuffix:
                attrObj = self._parent.attributes[
                    "{0}{1}{2}".format(attrName, attrSuffix, number)]
            else:
                attrObj = self._parent.attributes[attrName]
            attrObj.setSwitchAttrName(switchName)

    def __setup_data_format_attr(self, attrName, definition):
        if 'dataFormat' in definition:
            self.__prepareDataInterpreterFields(
                attrName, 'dataFormat', definition)

    def __setup_data_origin_attr(self, attrName, definition):
        if 'dataOrigin' in definition:
            self.__prepareDataInterpreterFields(
                attrName, 'dataOrigin', definition)

    def __setup_data_increment_attr(self, attrName, definition):
        if 'dataIncrement' in definition:
            self.__prepareDataInterpreterFields(
                attrName, 'dataIncrement', definition)

    def __prepareDataInterpreterFields(self, attrName, fieldName, definition):
        attrObj = self._parent.attributes[attrName]
        if not attrObj.hasArrayInterpreter():
            self.error_stream(
                "{0} cannot setup {1} definition without array interpreter"
                "".format(attrName, fieldName))
        else:
            fieldAttrName = definition[fieldName]
            self.debug_stream("{0} has {1} in {2} field"
                              "".format(attrName, fieldAttrName, fieldName))
            featureObj = self._parent.attributes[attrName].arrayInterpreter
            {'dataFormat': featureObj.dataFormatAttr,
             'dataOrigin': featureObj.originAttr,
             'dataIncrement': featureObj.incrementAttr
            }[fieldName] = fieldAttrName

    def __prepareChannelLikeAttr(self, like, number, definition, attrName):
        if like == 'channel':
            scpiPrefix = "CHAN"
            attrSuffix = "Ch"
        elif like == 'function':
            scpiPrefix = "FUNC"
            attrSuffix = "Fn"
        else:
            scpiPrefix = definition['multiple']['scpiPrefix']
            attrSuffix = definition['multiple']['attrSuffix']
        definition['readCmd'] = definition['readCmd'](scpiPrefix, number)
        if 'writeCmd' not in definition:
            definition['writeCmd'] = None
        else:
            definition['writeCmd'] = definition['writeCmd'](scpiPrefix, number)
        if 'manager' in definition and definition['manager'] is True:
            self._parent.attributesFlags["%s%d"
                                         % (attrSuffix, number)] = attrName

    def __buildROObj(self, attrName, attrId, definition):
        self._parent.attributes[attrName] =\
            SkippyReadAttribute(
                name=attrName, id=attrId, type=definition['type'],
                dim=definition['dim'][0], readCmd=definition['readCmd'],
                readFormula=definition['readFormula'], parent=self._parent)

    def __buildRWObj(self, attrName, attrId, definition, readmethod=None,
                     writemethod=None):
        _type = definition['type']
        _dim = definition['dim'][0]
        _rcmd = definition['readCmd']
        _wcmd = definition['writeCmd']
        _rformula = definition['readFormula']
        if 'writeFormula' in definition:
            _wformula = definition['writeFormula']
        else:
            _wformula = None
        if 'delayAfterWrite' in definition:
            _delayAfterWrite = definition['delayAfterWrite']
        else:
            _delayAfterWrite = None
        if 'rampeable' in definition:
            self._parent.attributes[attrName] =\
                SkippyReadWriteAttribute(
                    name=attrName, id=attrId, type=_type,
                    dim=_dim, readCmd=_rcmd, writeCmd=_wcmd,
                    readFormula=_rformula,  # writeFormula=_wformula,
                    rampeable=True, delayAfterWrite=_delayAfterWrite,
                    parent=self._parent)
            if readmethod is not None and writemethod is not None:
                self.__configureRamping(attrName, definition,
                                        readmethod, writemethod)
        else:
            self._parent.attributes[attrName] =\
                SkippyReadWriteAttribute(
                    name=attrName, id=attrId, type=_type,
                    dim=_dim, readCmd=_rcmd, writeCmd=_wcmd,
                    readFormula=_rformula,  # writeFormula=_wformula,
                    delayAfterWrite=_delayAfterWrite, parent=self._parent)

    def __prepareWriteValues(self, attrName, definition, aprop, attr):
        self._parent.attributes[attrName].\
            setWriteValues(definition['writeValues'])
        # this is a very important information to have
        # in the attr descrition
        if 'description' in definition:
            prefix = definition['description']+". "
        else:
            prefix = ""
        descr = "%sAllowed values: %s"\
                % (prefix, repr(definition['writeValues']))
        if aprop is not None:
            aprop.set_description(descr)
            attr.set_default_properties(aprop)

    def __configureRamping(self, attrName, definition, readmethod,
                           writemethod):
        if self.__device is not None:
            db = PyTango.Database()
            step = PyTango.Attr(attrName+"Step", definition['type'],
                                PyTango.READ_WRITE)
            step.set_memorized()
            step.set_memorized_init(True)
            self.__device.add_attribute(step, r_meth=readmethod,
                                        w_meth=writemethod)
            try:
                devName = self.__device.get_name()
                stepAttrName = attrName+"Step"
                attrProp = db.get_device_attribute_property(devName,
                                                            stepAttrName)
                propertyValueStr = attrProp[stepAttrName]['__value'][0]
                value = float(propertyValueStr)
                rampObj = self._parent.attributes[attrName].getRampObj()
                rampObj.rampStep = value
            except:
                rampObj = self._parent.attributes[attrName].getRampObj()
                rampObj.rampStep = None
            stepspeed = PyTango.Attr(attrName+"StepSpeed",
                                     PyTango.CmdArgType.DevDouble,
                                     PyTango.READ_WRITE)
            stepspeed.set_memorized()
            stepspeed.set_memorized_init(True)
            self.__device.add_attribute(stepspeed, r_meth=readmethod,
                                        w_meth=writemethod)
            try:
                devName = self.__device.get_name()
                stepSpeedAttrName = attrName+"StepSpeed"
                attrProp = db.get_device_attribute_property(devName,
                                                            stepSpeedAttrName)
                propertyValueStr = attrProp[attrName+"StepSpeed"]['__value'][0]
                value = float(propertyValueStr)
                rampObj = self._parent.attributes[attrName].getRampObj()
                rampObj.rampStepSpeed = value
            except:
                rampObj = self._parent.attributes[attrName].getRampObj()
                rampObj.rampStepSpeed = None
        self._attributeList.append(attrName+"Step")
        self._attributeList.append(attrName+"StepSpeed")

    # remove dynamic attributes
    def remove_attribute(self, attrName):
        if self.__device is not None:
            if attrName in self._attributeList:
                try:
                    self.__device.remove_attribute(attrName)
                except Exception as e:
                    self.error_stream("In remove_attribute(%s) Exception: %s"
                                      % (attrName, e.desc))
                else:
                    attrIdx = self._attributeList.index(attrName)
                    self._attributeList.pop(attrIdx)
            else:
                self.warn_stream("In remove_attribute(%s): it wasn't in the "
                                 "list" % (attrName))

    def remove_alldynAttrs(self):
        while len(self._attributeList) > 0:
            self.remove_attribute(self._attributeList[0])
    #      remember to clean the self.__device.attributes
    #      and the self._attributeList
