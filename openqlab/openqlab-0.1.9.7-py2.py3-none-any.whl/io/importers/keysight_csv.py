import pandas as pd
from openqlab.io.importers import utils
from openqlab.io.base_importer import StreamImporter
from openqlab.io.data_container import DataContainer


class KeysightCSV(StreamImporter):
    NAME = 'KeysightCSV'
    AUTOIMPORTER = True
    STARTING_LINES = ['^x-axis', '^second']

    def read(self):
        data = self._read_data()
        output = DataContainer(data, type='osci')
        output.header['xUnit'] = 's'
        output.header['yUnit'] = 'V'
        return output

    def _read_data(self):
        xlabel = 'Time'
        ylabel = utils.get_file_basename(self._stream.name)
        output = pd.read_csv(self._stream, sep=',', index_col=0, prefix=ylabel + '_', header=None)
        output.index.name = xlabel

        return output
