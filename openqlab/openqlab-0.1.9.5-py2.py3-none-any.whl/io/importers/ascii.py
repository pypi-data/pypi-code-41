from typing import List
import pandas as pd
from openqlab.io.importers import utils
from openqlab.io.base_importer import StreamImporter
from openqlab.io.data_container import DataContainer


class ASCII(StreamImporter):
    NAME = 'ASCII'
    AUTOIMPORTER = True
    STARTING_LINES: List[str] = []

    def _check_header(self):
        for _ in range(11):
            try:
                line = self._stream.readline()
            except UnicodeDecodeError:
                raise utils.UnknownFileType(
                    f"'{self.NAME}' importer: cannot decode binary file")

            col = line.split()
            for item in col:
                try:
                    float(item)
                except ValueError:
                    raise utils.UnknownFileType(
                        f"'{self.NAME}' importer: expected plain numeric ASCII")

    def read(self):
        data = self._read_data()
        output = DataContainer(data)
        if output.empty:
            raise utils.ImportFailed(
                f"'{self.NAME}' importer: \
                    Did not find any valid data \
                    in file '{self._stream.name}'")
        return output

    def _read_data(self):
        xlabel = 'x'
        ylabel = utils.get_file_basename(self._stream.name)
        data = pd.read_csv(self._stream, sep=None, index_col=0, usecols=[0, 1],
                           names=[xlabel, ylabel], header=None, engine='python')
        return data


