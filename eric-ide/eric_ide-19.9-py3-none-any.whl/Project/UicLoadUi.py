# -*- coding: utf-8 -*-

# Copyright (c) 2011 - 2019 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module to get sys.path of an external interpreter.
"""

from __future__ import print_function
try:
    bytes = unicode     # __IGNORE_EXCEPTION__
except NameError:
    pass

import sys
import json
import xml.etree.ElementTree

try:
    from PyQt5.QtCore import qVersion, QMetaMethod, QByteArray
    from PyQt5.QtWidgets import QAction, QWidget, QApplication
    from PyQt5 import uic
    
    pyqtType = 5
except ImportError:
    try:
        # try a potential PyQt4 installation
        from PyQt4.QtCore import qVersion, QMetaMethod, QByteArray
        from PyQt4.QtGui import QAction, QWidget, QApplication
        from PyQt4 import uic
        
        pyqtType = 4
    except ImportError:
        print("Neither PyQt5 nor PyQt4 found.")
        sys.exit(1)


def objectName(formFile, projectPath):
    """
    Function to get the object name of a form.
    
    @param formFile file name of the form
    @type str
    @param projectPath directory name of the project
    @type str
    """
    app = QApplication([])      # __IGNORE_WARNING__
    try:
        dlg = uic.loadUi(formFile, package=projectPath)
        print(dlg.objectName())
        sys.exit(0)
    except (AttributeError, ImportError,
            xml.etree.ElementTree.ParseError) as err:
        print(str(err))
        sys.exit(1)


def className(formFile, projectPath):
    """
    Function to get the class name of a form.
    
    @param formFile file name of the form
    @type str
    @param projectPath directory name of the project
    @type str
    """
    app = QApplication([])      # __IGNORE_WARNING__
    try:
        dlg = uic.loadUi(formFile, package=projectPath)
        print(dlg.metaObject().className())
        sys.exit(0)
    except (AttributeError, ImportError,
            xml.etree.ElementTree.ParseError) as err:
        print(str(err))
        sys.exit(1)


def __mapType(type_):
    """
    Private function to map a type as reported by Qt's meta object to the
    correct Python type.
    
    @param type_ type as reported by Qt
    @type QByteArray or bytes
    @return mapped Python type
    @rtype str
    """
    mapped = bytes(type_).decode()
    
    # I. always check for *
    mapped = mapped.replace("*", "")
    
    if pyqtType != 4:
        # 1. check for const
        mapped = mapped.replace("const ", "")
        
        # 2. replace QString and QStringList
        mapped = mapped.replace("QStringList", "list")\
                       .replace("QString", "str")
        
        # 3. replace double by float
        mapped = mapped.replace("double", "float")
    
    return mapped


def signatures(formFile, projectPath):
    """
    Function to get the signatures of form elements.
    
    @param formFile file name of the form
    @type str
    @param projectPath directory name of the project
    @type str
    """
    objectsList = []
    
    app = QApplication([])      # __IGNORE_WARNING__
    try:
        dlg = uic.loadUi(formFile, package=projectPath)
        objects = dlg.findChildren(QWidget) + dlg.findChildren(QAction)
        for obj in objects:
            name = obj.objectName()
            if not name or name.startswith("qt_"):
                # ignore un-named or internal objects
                continue
            
            metaObject = obj.metaObject()
            objectDict = {
                "name": name,
                "class_name": metaObject.className(),
                "methods": [],
            }
            
            for index in range(metaObject.methodCount()):
                metaMethod = metaObject.method(index)
                if metaMethod.methodType() == QMetaMethod.Signal:
                    signatureDict = {
                        "methods": []
                    }
                    if qVersion().startswith("5."):
                        signatureDict["signature"] = "on_{0}_{1}".format(
                            name,
                            bytes(metaMethod.methodSignature()).decode()
                        )
                    else:
                        signatureDict["signature"] = "on_{0}_{1}".format(
                            name,
                            metaMethod.signature()
                        )
                    
                    if qVersion().startswith("5."):
                        signatureDict["methods"].append("on_{0}_{1}".format(
                            name,
                            bytes(metaMethod.methodSignature())
                            .decode().split("(")[0]
                        ))
                    else:
                        signatureDict["methods"].append("on_{0}_{1}".format(
                            name,
                            metaMethod.signature().split("(")[0]
                        ))
                    signatureDict["methods"].append("{0}({1})".format(
                        signatureDict["methods"][-1],
                        ", ".join([
                            __mapType(t)
                            for t in metaMethod.parameterTypes()
                        ])
                    ))
                    
                    returnType = __mapType(
                        metaMethod.typeName().encode())
                    if returnType == 'void':
                        returnType = ""
                    signatureDict["return_type"] = returnType
                    parameterTypesList = [
                        __mapType(t)
                        for t in metaMethod.parameterTypes()
                    ]
                    signatureDict["parameter_types"] = parameterTypesList
                    pyqtSignature = ", ".join(parameterTypesList)
                    signatureDict["pyqt_signature"] = pyqtSignature
                    
                    parameterNames = metaMethod.parameterNames()
                    if parameterNames:
                        for index in range(len(parameterNames)):
                            if not parameterNames[index]:
                                parameterNames[index] = \
                                    QByteArray("p{0:d}".format(index)
                                               .encode("utf-8"))
                    parameterNamesList = [bytes(n).decode()
                                          for n in parameterNames]
                    signatureDict["parameter_names"] = parameterNamesList
                    methNamesSig = ", ".join(parameterNamesList)
                    
                    if methNamesSig:
                        if qVersion().startswith("5."):
                            pythonSignature = \
                                "on_{0}_{1}(self, {2})".format(
                                    name,
                                    bytes(metaMethod.methodSignature())
                                    .decode().split("(")[0],
                                    methNamesSig)
                        else:
                            pythonSignature = \
                                "on_{0}_{1}(self, {2})".format(
                                    name,
                                    metaMethod.signature().split("(")[0],
                                    methNamesSig)
                    else:
                        if qVersion().startswith("5."):
                            pythonSignature = "on_{0}_{1}(self)".format(
                                name,
                                bytes(metaMethod.methodSignature())
                                .decode().split("(")[0])
                        else:
                            pythonSignature = "on_{0}_{1}(self)".format(
                                name,
                                metaMethod.signature().split("(")[0])
                    signatureDict["python_signature"] = pythonSignature
                    
                    objectDict["methods"].append(signatureDict)
            
            objectsList.append(objectDict)
        
        print(json.dumps(objectsList))
        sys.exit(0)
    except (AttributeError, ImportError,
            xml.etree.ElementTree.ParseError) as err:
        print(str(err))
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Wrong number of arguments.")
        sys.exit(1)
    
    if sys.argv[1] == "object_name":
        objectName(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "class_name":
        className(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "signatures":
        signatures(sys.argv[2], sys.argv[3])
    else:
        print("Unknow operation given.")
        sys.exit(1)
    
#
# eflag: noqa = M701, M801
