import os
import imp
import jpype

if jpype.isJVMStarted() != True:
    jars = []
    for top, dirs, files in os.walk(imp.find_module('pdfextract')[1]+'/data'):
        for nm in files:
            if nm[-4:] == ".jar":
                jars.append(os.path.join(top, nm))
    jpype.addClassPath(os.pathsep.join(jars))
    jpype.startJVM(jpype.getDefaultJVMPath(),convertStrings=False)
