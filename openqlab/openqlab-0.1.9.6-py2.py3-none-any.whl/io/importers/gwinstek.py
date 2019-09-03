import numpy as np
import pandas as pd
from openqlab.io.base_importer import StreamImporter
from openqlab.io.data_container import DataContainer
from typing import Callable, cast
from openqlab.io.importers import utils
from pathlib import Path


class Gwinstek(StreamImporter):
    NAME = 'Gwinstek'
    AUTOIMPORTER = True
    STARTING_LINES = [r'^Format,1.0B,$']
    SAVEMODES = ('Detail', 'Fast')
    HEADER_SPLIT = ','
    HEADER_MAP = {
        'Memory Length': (int, 'NumPoints'),
        'Source': (str, None),
        'Vertical Units': (str, 'yUnit'),
        'Vertical Units Div': (float, None),
        'Vertical Units Extend Div': (float, None),
        'Label': (str, None),
        'Probe Type': (float, None),
        'Probe Ratio': (float, None),
        'Vertical Scale': (float, 'yScale'),
        'Vertical Position': (float, 'yOffset'),
        'Horizontal Units': (str.lower, 'xUnit'),
        'Horizontal Scale': (float, 'xScale'),
        'Horizontal Position': (float, 'xOffset'),
        'SincET Mode': (str, None),
        'Sampling Period': (float, None),
        'Horizontal Old Scale': (float, None),
        'Horizontal Old Position': (float, None),
        'Firmware': (str, None),
        'Mode': (str, None),
    }

    def read(self):
        self._read_header()
        data = self._read_data()
        output = DataContainer(data, type='osci')

        return output

    def _read_line(self, line: str):
        split = line.strip().split(self.HEADER_SPLIT)
        keyword, *values = split

        if keyword not in self.HEADER_MAP:
            return

        type_ = cast(Callable, self.HEADER_MAP[keyword][0])
        keyword = self._get_key(keyword)

        values = values[0::2]
        self._header[keyword] = [type_(value) for value in values]

    def _read_header(self):
        line = True
        while line:
            line = self._stream.readline()
            if line.startswith('Waveform Data'):
                break
            self._read_line(line)
        self.num_traces = len(self._header['NumPoints'])

    def _read_trace(self, ii):
        xlabel = 'Time'

        header = {key: value[ii] for key, value in self._header.items()}
        mode = header.get('Mode')

        if mode not in self.SAVEMODES:
            raise utils.ImportFailed(
                f"'{self.NAME}' importer: Could not determine savemode in file '{self._stream.name}'")

        if mode == 'Detail':
            index, data = self._data.iloc[:, 2 * ii:2 * ii + 2].values.T
            print(data)

        if mode == 'Fast':
            x_offset = header['xOffset']
            start = - header['xScale'] * 10 / 2 + x_offset
            stop = header['xScale'] * 10 / 2 + x_offset
            num_points = header['NumPoints']

            index = np.linspace(start, stop, endpoint=False, num=num_points)
            data = self._data.iloc[:, 2 * ii].values
            data = data * header['yScale'] / 25

        output = DataContainer(data=data, index=index, header=header,
                               columns=[f'{Path(self._stream.name).stem}_{ii+1}'])
        output.index.name = xlabel

        return output

    def _read_data(self):

        self._data = pd.read_csv(self._stream, sep=self.HEADER_SPLIT, header=None)

        traces = [self._read_trace(n) for n in range(self.num_traces)]
        return DataContainer.concat(traces, axis=1)

        # xlabel = 'Time'
        # try:
        #     mode = self._header['Mode']
        #     num_traces = self._header['NumTraces']
        #     num_points = self._header['NumPoints']
        #     x_offset = self._header['xOffset']
        #     start = - self._header['xScale'] * 10 / 2 + x_offset
        #     stop = self._header['xScale'] * 10 / 2 + x_offset
        #     if self._header['xUnit'] == 'S':
        #         self._header['xUnit'] = 's'
        # except KeyError:
        #     raise utils.ImportFailed(
        #         f"'{self.NAME}' importer: could not gather necessary information in file '{self._stream.name}'")
        #
        # ylabel = utils.get_file_basename(self._stream.name)
        # ylabels = [f'{ylabel}_{trace_num}' for trace_num in range(1, num_traces + 1)]
        # if mode == 'Detail':
        #     names = [xlabel] + ylabels
        #     usecols = [0, 1] + list(range(3, 2 * num_traces + 1, 2))
        #     output = pd.read_csv(self._stream, sep=',', index_col=0, usecols=usecols, prefix=ylabel + '_', header=None)
        #     output.index.name = xlabel
        #     output.columns = ylabels
        # elif mode == 'Fast':
        #     names = ylabels
        #     usecols = list(range(0, 2 * num_traces - 1, 2))
        #     x = np.linspace(start, stop, endpoint=False, num=num_points)
        #     output = pd.read_csv(self._stream, sep=',', usecols=usecols,
        #                          names=names, header=None, skipinitialspace=True)
        #     output = output * (self._header['yScale']) / 25
        #     if output.empty:
        #         raise EmptyDataError(
        #             f"'{self.NAME}' importer: Did not find any valid data in file '{self._stream.name}'")
        #     output.index = x
        #     output.index.name = xlabel
        # else:
        #     raise utils.ImportFailed(
        #         f"'{self.NAME}' importer: expected save modes {self.SAVEMODES} not found in file '{self._stream.name}'")
        # return output
