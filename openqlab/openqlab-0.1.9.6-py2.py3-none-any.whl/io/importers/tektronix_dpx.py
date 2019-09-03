from openqlab.io.importers.tektronix import Tektronix


class TektronixDPX(Tektronix):
    NAME = 'TektronixDPX'
    STARTING_LINES = [r'^DPX', r'^\[Global Parameters\]']
    HEADER_MAP = {
        'Span': (float, 'Span'),
        'Resolution Bandwidth': (float, 'RBW'),
        'Actual RBW': (float, None),
        'Frequency': (float, 'CenterFrequency'),
        'Reference Level': (float, None),
        'RBW-unit': (str, 'xUnit'),
        'Reference Level-unit': (str, 'yUnit'),
    }
    xUNIT = 's'

    def read(self):
        output = super().read()
        output.index.name = 'Time'
        return output
