from openqlab.io.base_importer import StreamImporter
from openqlab.io.data_container import DataContainer
from openqlab.io.importers import utils


class DataContainerCSV(StreamImporter):
    NAME = 'DataContainerCSV'
    AUTOIMPORTER = True
    STARTING_LINES = [DataContainer.json_prefix]

    def read(self):
        self._stream.seek(0)
        output = DataContainer.from_csv(self._stream, parse_dates=True)
        if output.empty:
            raise utils.ImportFailed(
                    f"'{self.NAME}' importer: Did not find any valid data\
                            in file '{self._stream.name}'")
        return output

