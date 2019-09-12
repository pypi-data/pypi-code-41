""""
First, install USBTMC driver which only requires VISA installed on the computer.
Second, Use pyvisa shell to get usb visa resource name,
python -m visa shell
list
"""
from qcodes import VisaInstrument, validators as vals
from qcodes.instrument.channel import InstrumentChannel, ChannelList


class Bk4065Channel(InstrumentChannel):
    def __init__(self, parent, name, ch_num):
        super().__init__(parent, name)

        def val_parser(input_string):
            """
            Parses return values from instrument. e.g. 'C1: BSWV WVTP,SINE,FRQ,1000,AMP,3,OFST,3,PHSE,0'
            Args:
                input_string: The raw return value
            """

            payload_list = input_string.strip('C1:').strip(' ').strip('BSWV').strip(' ').split(',')
            payload_dict = dict([(k, v) for k, v in zip(payload_list[::2], payload_list[1::2])])
            return payload_dict

        self.add_parameter('basic_wave',
                           label=f'Channel {ch_num} basic wave setting',
                           get_cmd=f'C{ch_num}:BSWV?',
                           get_parser=val_parser)

        self.add_parameter('basic_wave_type',
                           label=f'Channel {ch_num} basic wave type',
                           set_cmd=f'C{ch_num}:BSWV WVTP,{{}}',
                           vals=vals.Enum('SINE', 'SQUARE', 'RAMP', 'PULSE', 'NOISE', 'ARB', 'DC')
                           )

        self.add_parameter('basic_wave_frequency',
                           label=f'Channel {ch_num} basic wave frequency',
                           set_cmd=f'C{ch_num}:BSWV FRQ,{{}}HZ',
                           vals=vals.Numbers(0, 300)
                           )

        self.add_parameter('basic_wave_amplitude',
                           label=f'Channel {ch_num} basic wave amplitude',
                           set_cmd=f'C{ch_num}:BSWV AMP,{{}}V',
                           vals=vals.Numbers(0, 5)
                           )

        self.add_parameter('basic_wave_width',
                           label=f'Channel {ch_num} basic wave pulse width',
                           set_cmd=f'C{ch_num}:BSWV WIDTH,{{}}S',
                           vals=vals.Numbers(0, 5e-6)
                           )

        self.add_parameter('basic_wave_offset',
                           label=f'Channel {ch_num} basic wave offset',
                           set_cmd=f'C{ch_num}:BSWV OFST,{{}}V',
                           vals=vals.Numbers(0, 2.5)
                           )

        self.add_parameter('basic_wave_delay',
                           label=f'Channel {ch_num} basic wave pulse delay',
                           set_cmd=f'C{ch_num}:BSWV DLY,{{}}S',
                           vals=vals.Numbers(0, 5)
                           )

        self.add_parameter('output_enable',
                           label=f'Enable or disable the output channel {ch_num}',
                           set_cmd=f'C{ch_num}:OUTP {{}}',
                           vals=vals.Enum('ON', 'OFF')
                           )

        self.add_parameter('output_load',
                           label=f'Set output load to 50Ohm or Hi-impedance to channel {ch_num}',
                           set_cmd=f'C{ch_num}:OUTP LOAD,{{}}',
                           vals=vals.Enum('50', 'HZ')
                           )


class Bk4065(VisaInstrument):
    """
    This is the QCoDeS driver for the BK PRECISION 4065 signal generator.
    """

    def __init__(self, address, timeout=20, **kwargs):
        """
        Initialises the BK4065.
        Args:
            name (str): Name of the instrument used by QCoDeS
        address (string): Instrument address as used by VISA
            timeout (float): visa timeout, in secs. long default (180)
              to accommodate large waveforms
        """

        # Init VisaInstrument. device_clear MUST NOT be issued, otherwise communications hangs
        # due a bug in firmware
        super().__init__('BK4065', address, device_clear=False, timeout=timeout, **kwargs)
        self.connect_message()

        for channel_number in range(1, 3):
            channel = Bk4065Channel(self, f'ch{channel_number}', channel_number)
            self.add_submodule(f'ch{channel_number}', channel)


if __name__ == '__main__':
    sig_inst2 = Bk4065('USB0::0xF4ED::0xEE3A::448H17107::INSTR',  terminator='\n')
    sig_inst2.ch1.basic_wave_type('PULSE')
    sig_inst2.ch1.basic_wave_frequency(25)  # 25Hz
    sig_inst2.ch1.basic_wave_amplitude(5)  # 5V
    sig_inst2.ch1.basic_wave_offset(2.5)
    sig_inst2.ch1.basic_wave_width(5e-6)  #5uS
    sig_inst2.ch1.output_load('HZ')
    sig_inst2.ch1.output_enable('ON')

    sig_inst2.ch2.basic_wave_type('PULSE')
    sig_inst2.ch2.basic_wave_frequency(25)  # 25Hz
    sig_inst2.ch2.basic_wave_amplitude(5)  # 5V
    sig_inst2.ch2.basic_wave_offset(2.5)
    sig_inst2.ch2.basic_wave_width(5e-6)  #5uS
    sig_inst2.ch2.basic_wave_delay(2e-6)
    sig_inst2.ch2.output_load('HZ')
    sig_inst2.ch2.output_enable('ON')

