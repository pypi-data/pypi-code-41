import os
import glob
import importlib
import inspect

from openqlab.io.importers import utils
from openqlab.io.base_importer import BaseImporter
from openqlab.io.importers.ascii import ASCII
from openqlab.io.importers.data_container_csv import DataContainerCSV
from openqlab.io.importers.hp4395a import HP4395A
#from openqlab.io.importers.hp4395a_gpib import HP4395A_GPIB
from openqlab.io.importers.keysight_binary import KeysightBinary
from openqlab.io.importers.keysight_csv import KeysightCSV
from openqlab.io.importers.keysight_fra import KeysightFRA
from openqlab.io.importers.rhode_schwarz import RhodeSchwarz
from openqlab.io.importers.tektronix import Tektronix
from openqlab.io.importers.tektronix_dpx import TektronixDPX
from openqlab.io.importers.tektronix_spectrogram import TektronixSpectrogram



# TODO maybe refactoring
IMPORTER_DIR = os.path.abspath(__file__)

IMPORTER_DIR = os.path.dirname(IMPORTER_DIR)

for fn in glob.glob(IMPORTER_DIR + "/*.py"):
    importer = utils.get_file_basename(fn)
    if importer in ('__init__', 'utils'):
        continue
    try:
        importer_module = importlib.import_module('openqlab.io.importers.' + importer, package='openqlab.io.importers')
        for m in inspect.getmembers(importer_module, inspect.isclass):
            name, klass = m
            if issubclass(klass, BaseImporter):
                globals()[name] = klass
    except ImportError as e:
        print(e)
        continue
