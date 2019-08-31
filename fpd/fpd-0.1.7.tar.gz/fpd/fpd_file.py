from __future__ import print_function

'''
'''


# file module version (separate from fpd version)
__version__ = '0.1.1'
_min_version = '0.1.0'

import mmap
import h5py
import numpy as np
from collections import OrderedDict
import time
from dateutil.parser import parse
import codecs
import re
from collections import MutableMapping
import os
from functools import partial
import inspect
import matplotlib.pyplot as plt
import matplotlib as mpl
from distutils.version import LooseVersion
import logging
from pkg_resources import parse_version
import io
from tqdm import tqdm
from collections import namedtuple
from itertools import product
import sys
from scipy.interpolate import griddata
from scipy.interpolate import CloughTocher2DInterpolator


from . import __version__ as fpd_pkg_version

#from . import _p3
# python version
_p3 = False
if sys.version_info > (3, 0):
    _p3 = True


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_handler = logging.StreamHandler()
#_handler.setFormatter(logging.Formatter(fmt='%(levelname)s:%(name)s:%(message)s'))
_handler.setFormatter(logging.Formatter(fmt='%(levelname)s: %(message)s'))
_logger.addHandler(_handler)


if _p3:
    _str_type_list = [str]
    _input_fn = input
else:
    _str_type_list = [str, unicode]
    _input_fn = raw_input


_mpl_non_adjust = False
import matplotlib as mpl
_mplv = mpl.__version__
from distutils.version import LooseVersion
if LooseVersion(_mplv) >= LooseVersion('2.2.0'):
    _mpl_non_adjust = True



def _flatten(d, parent_key='', sep='_', include_empty=False):
    '''
    Flatten a dictionary or other nested structure into a dictionary.
    
    Parameters
    ----------
    d : instance of MutableMapping
        Object to be flattened.
    parent_key : string
        String to a which all keys are appended.
    sep : string
        String seperating flattened keys.
    include_empty : bool
        boolean controlling if empty keys are retained.
    
    Returns
    -------
    Dictionary of flattened structure.
    
    '''

    items = []
    for k,v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(_flatten(v, new_key, sep).items())
            if include_empty:
                items.append((new_key, v))
        else:
            items.append((new_key, v))
    return dict(items)



def _unflatten(fd, sep='_'):
    '''
    Unflatten a dictionary or other nested structure into a nested
    dictionary.
    
    Parameters
    ----------
    fd : dictionary
        Flattend dictionary.
    sep : string
        String at which keys are split. 
    
    Returns
    -------
    Nested dictionary of unflattened structure.
    
    '''

    ud = dict()
    for k, v in fd.items():
        new_ks = k.split(sep)
        d = ud
        for new_k in new_ks[:-1]:
            if new_k not in d:
                d[new_k] = dict()
            d = d[new_k]
        d[new_ks[-1]] = v
    return ud



class Merlin_hdr_file_parser:
    '''
    Converts Merlin header file into ordered key : value dictionary,
    patching the file formatting and extracting specific parameters
    along the way.
    
    The keys exclude any lists of possible values (in parentheses).
    Strings are converted to lower case and words are separated by
    underscores.
        
    Versions handled are:
        0   0.76                format differs from documentation.
        1   0.65.8 - 0.67.0.6   format matches documentation.
        
    Additional keys in 1 are:
        humidity, dac_file, gap_fill_mode
    
    Attributes
    ----------
    fn : string
        Merlin header filename.
    strict : bool
        boolean of whether strict version check control took place.
    fmt_ver : integer
        Internal version numbering of known systems.
    hs : string
        Header file contents as a string.
    hd : ordered dictionary
        Dictionary of keys and values parsed from header file.
    CM : bool
        boolean describing if colour mode is in operation.
    AC : integer
        Number of active counters.
    
    Methods
    -------
    _print_testing_notes
        
    '''
    
    def __init__(self, fn, strict=True):
        '''
        Parameters
        ----------
        fn : string
            Merlin header filename.
        strict : bool
            boolean controlling if strict version check takes place.
        
        Notes
        -----
        If `strict` is False, the most recent version will be tried.
        
        '''
        
        self._ver_str_min = "0.65.8"
        self._ver_str_max = "0.67.0.8"
        
        self.fn = fn
        self.strict = strict
                
        self._read_file_and_version()
        self._parse_header()
        self._extract_data()
        
        
    def _read_file_and_version(self):
        with codecs.open(self.fn, "r", encoding='iso 8859-15') as f:
            self.hs = f.read().strip()

        # Parse versions
        p = 'Software Version:[\s]*([\d\.]+)'
        s = re.search(p, self.hs)
        try:
            self._ver_str = s.groups()[0]
        except:
            # This should never happen in newer versions of the file.
            m = 'hdr version string not found!'
            _logger.error(m)
            raise Exception(m)

        p = 'Readout System:[\s]*([^\n\r]+)'
        s = re.search(p, self.hs)
        try:
            self._read_str = s.groups()[0]
        except:
            # This should never happen in newer versions of the file.
            m = 'hdr readout system string not found!'
            _logger.error(m)
            raise Exception(m)
        
        # Check versions. Could write as dict if many versions.
        fmt_ver1 = (parse_version(self._ver_str_min)
                    <= parse_version(self._ver_str)
                    <= parse_version(self._ver_str_max))

        fmt_ver0_string = '0.76'
        if self._ver_str==fmt_ver0_string and self._read_str=='Merlin vs 1':
            # 1st hardware / software
            _logger.info("Detected 1st version: '%s'" %(self._ver_str))
            self.fmt_ver = 0
        elif fmt_ver1 and self._read_str=='Merlin Quad':
            _logger.info("Detected 2nd version: '%s'" %(self._ver_str))
            self.fmt_ver = 1
        else:
            if self.strict:
                m = "hdr software '%s' and readout '%s' combination not \
                        understood" %(self._ver_str, self._read_str)
                _logger.error(m)
                _logger.info("Try adding 'strict=False' to input options.")
                raise Exception(m)
            else:
                self.fmt_ver = 1
                _logger.warning('Assuming latest known version, fingers crossed!')
    
    
    def _parse_header(self):
        # Convert header string into ordered key : value dictionary.
        
        # split at header delims: End is optional (it is absent in 0.76)
        p = '^HDR,(.+?)(End)?$'
        s = re.search(p, self.hs, re.S)
        hsp = s.groups()[0].strip()
        
        # patch header
        # add ':' to end of Sensor Bias line key if needed.
        # It is absent in 0.76 and 0.65.8.
        p = '(Sensor Bias \(V, .?A\))[^:][\s ]*'
        s = re.search(p, hsp)
        if s is not None:
            k = s.groups()[0]
            hsp = hsp.replace(k, k+':')

        # split into keys and values
        p1 = '[ ]*:[\s ]+'  # matches 'spaces : newlines' for v0.76
        p2 = '[\n\r]+'      # matches newlines for end of lines
        s = re.split(p1+'|'+p2, hsp)
        ks = s[0::2]
        vs = [v.strip() for v in s[1::2]]
        
        # Match and remove last parentheses with contents,
        # then strip and swap underscore for space to form keys
        ks_strip = [re.sub(r' *\([^)]*\)$', '', k.strip()).replace(' ', '_').lower() for k in ks]
        # make dictionary
        self.hd = OrderedDict(zip(ks_strip, vs))
        
        # print key vals
        for i,k in enumerate(ks):
            m = '%50s\t%25s\t%s' %(k, ks_strip[i], vs[i])
            _logger.debug(m)
    
    
    def _extract_data(self):
        # read parsed dictionary for important parameters
        
        # Colour mode activated if CM in one of (SPM, CSM, CM, CSCM)
        self.CM = 'CM' in self.hd['chip_mode']    
        
        # number of active counters (1 or 2) 
        if self.fmt_ver==0:
            AC = self.hd['active_counters'].lower().count('on')              
        elif self.fmt_ver==1:
            AC = len(re.findall('\d', self.hd['active_counters']))
        self.AC = AC
        
        
    def _print_testing_notes(self):
        m = '''
        To see what keys are different:
        m1 = Merlin_hdr_file_parser('./fpd_test_data/bin_257.hdr')
        m2 = Merlin_hdr_file_parser('./fpd_test_data/spm100ms.hdr')
        
        d1 = m1.hd
        d2 = m2.hd
        
        print( set(d1.keys()) - set(d2.keys()) )
        #[]
        print( set(d2.keys()) - set(d1.keys()) )
        #[u'humidity', u'dac_file', u'gap_fill_mode']
        
        for x,y in d1.items():
            print(x, '\t', y)
        
            chip_id                 W113_L6
            chip_type               Medipix3RX
            assembly_size           1 X 1
            chip_mode               SPM
            counter_depth           12B
            gain                    High
            active_counters         On Off
            thresholds              2.700000E+1  3.600000E+0
            dacs                    150,20,0,0,0,0,0,0,100,10,125,125,100,100,80,100,120,50,128,4,255,108,120,160,148,401,401
            bpc_file                C:\MediPix\Config\default\Mask default.bpc
            flat_field_file         Dummy (C:\Temp\Temp.ffc)
            dead_time_file          Dummy (C:\Temp\Temp.dtc)
            acquisition_type        Normal
            frames_in_acquisition   65792
            trigger_start           Rising Edge
            trigger_stop            Internal
            frames_per_trigger      1
            time_and_date_stamp     11/08/201517:55:07
            sensor_bias             90 V
            sensor_polarity         Positive
            temperature             0.000000
            medipix_clock           120MHz
            readout_system          Merlin vs 1
            software_version        0.76


        for x,y in d2.items():
            print(x, '\t', y)
            
            time_and_date_stamp     27/08/2015 17:54:11
            chip_id                 W113_L6,-,-,-
            chip_type               Medipix 3RX
            assembly_size           2x2
            chip_mode               SPM
            counter_depth           12
            gain                    SLGM
            active_counters         Counter 0
            thresholds              0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0
            dacs                    000,000,000,000,000,000,000,000,175,010,200,125,100,100,093,100,099,030,128,004,255,127,128,177,167,000,000
            bpc_file                C:\Merlin_Quad_Config\Default\Default_SPM.bpc,,,
            dac_file                c:\MERLIN_Quad_Config\default\Default_SPM.dacs,,,
            gap_fill_mode           Distribute
            flat_field_file         None
            dead_time_file          Dummy (C:\<NUL>\)
            acquisition_type        Normal
            frames_in_acquisition   1
            frames_per_trigger      1
            trigger_start           Internal
            trigger_stop            Internal
            sensor_bias             15 V
            sensor_polarity         Positive
            temperature             Board Temp 0.000000 Deg C
            humidity                Board Humidity 0.000000
            medipix_clock           120MHz
            readout_system          Merlin Quad
            software_version        0.65.8
        
        
        import fpd.fpd_file as fpdp
        v0p67p0p8 = fpdp.Merlin_hdr_file_parser('test_small_16/test_small_16.hdr', strict=False)
        for x,y in v0p67p0p8.hd.items():
            print(x, '\t', y)
        
            time_and_date_stamp      01/03/2018 15:09:59
            chip_id          W529_E5,-,-,-
            chip_type        Medipix 3RX
            assembly_size    1x1
            chip_mode        SPM
            counter_depth    24
            gain             SLGM
            active_counters  Counter 0
            thresholds       0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0
            dacs             040,511,000,000,000,000,000,000,175,010,200,125,100,100,096,100,093,030,128,004,255,054,128,104,100,511,511
            bpc_file         c:\MERLIN_Quad_Config\W529_E5\W529_E5_SPM.bpc,,,
            dac_file         c:\MERLIN_Quad_Config\W529_E5\W529_E5_SPM.dacs,,,
            gap_fill_mode    Distribute
            flat_field_file  None
            dead_time_file   Dummy (C:\<NUL>\)
            acquisition_type         Normal
            frames_in_acquisition    16
            frames_per_trigger       1
            trigger_start    Internal
            trigger_stop     Internal
            sensor_bias      110 V
            sensor_polarity          Positive
            temperature      Board Temp 0.000000 Deg C
            humidity         Board Humidity 0.000000
            medipix_clock    120MHz
            readout_system   Merlin Quad
            software_version         0.67.0.8
        '''
        print(m)



class Merlin_binary_header_parser:
    '''
    Parses a Merlin binary header to extract parameters.
    
    Attributes
    ----------
    hs : string
        Header string, trimmed of padding.
    bitdepth_data : integer
        Data bitdepth: 1, 6, 12, 24.
    bitdepth_bin : integer
        Binary bitdepth (non-raw: 8, 16 or 32, raw: 64).
    params : dict of dicts
        Parameters extracted from header.
        The key is used internally. The value is a dict used for 
        dataset creation and has keys:
        'name' : str
            Dataset name.
        'unit' : str
            Data unit.
        'data' : obj
            Object data to be stored.
        'isim' : bool
            True is stored with image tag.
    raw_mode : bool
        If True, data was recorded in raw mode.
    header_bytesize : int
        Binary header size in bytes
    
    Notes
    -----
    If `fh` is an opened file, the file position after parsing is at
    the data block, and Exception('EOF') is raised at end of file.
    
    '''


    def __init__(self, fh, fmt_ver):
        '''
        Parameters
        ----------
        fh : bytes object or file / io.BufferedReader
            Object to parse. 
        fmt_ver : integer
            Internal format version, determined from Merlin header file.
        
        '''
        
        self._fh = fh
        self._fmt_ver = fmt_ver
        
        self._read_header()
        self._parse_header()
        
        
    def _read_header(self):
        # python 2/3 compatibility
        if _p3:
            ft = io.BufferedReader
        else:
            ft = file
        
        # Read header
        if type(self._fh) in _str_type_list:
            # header is provided directly
            self.header = self._fh
        elif type(self._fh)==ft:
            # read correct number of bytes from file 
            if self._fmt_ver==0:
                self.header_bytesize = 256
            elif self._fmt_ver==1:
                # Length is variable and contained in 3rd csv in binary hdr
                nc = 0      # number of commas read
                ns = 0      # number of bytes read 
                sl = []
                while True:
                    c = self._fh.read(1)
                    if c==b'':
                        raise Exception('EOF') # eof
                    ns+=1
                    if c==b',':
                        nc+=1
                        if nc==3:
                            break
                    elif nc>1:
                        sl.append(c)
                self.header_bytesize = int(b''.join(sl))
                self._fh.seek(-ns, 1) # reset to start of header
            else:
                m = "Format '%s' versions not understood" %(self._fmt_ver)
                _logger.error(m)
                raise Exception(m) 
            
            self.header = self._fh.read(self.header_bytesize)
            if self.header==b'':
                # reached end of file
                raise Exception('EOF')
        else:
            m = "fh must be of type 'str' or 'file', got %s." %(str(type(self._fh)))
            _logger.error(m)
            raise Exception(m)
    
    
    def _parse_header(self):
        self.hs = self.header.split(b'\x00', 1)[0]
        hv = self.hs.split(b',')
        
        if self._fmt_ver==0:
            Threshold_keV = np.array(hv[5:7], dtype='f4')
            DAC_val = np.array(hv[7:], dtype='u1')
            Exposure_nS = int(float(hv[4])*1e6)
            
            t = time.mktime(parse(hv[3]).timetuple())
            Unixtime_nS = int(t//1)*1000000000 + int(hv[3].rsplit('.')[-1].ljust(9, '0'))
            
            bitdepth_data = int(hv[0][:2])
            if bitdepth_data == 12:
                bitdepth_bin = 16
            else:
                bitdepth_bin = 32
        
        elif self._fmt_ver==1:
            bitdepth_bin = int(hv[6][1:])
            
            bitdepth_data = int(hv[-2]) # 53
            Exposure_nS = int(hv[-3].lower().split(b'ns')[0])   # 52
            t = time.mktime(parse(hv[-4]).timetuple())  # 51
            # s = t//1 + float(hv[51].rsplit('.')[-1][:-1])/1e9
            Unixtime_nS = int(t//1)*1000000000 + int(hv[-4].rsplit(b'.')[-1][:-1])  # 51
            
            if bitdepth_bin==64:
                self.raw_mode = True
            else:
                self.raw_mode = False
                
                Threshold_keV = np.array(hv[14:22], dtype='f4')
                DAC_val = np.array(hv[23:50], dtype='u1')
        
        # these always exist
        self.bitdepth_data = bitdepth_data
        self.bitdepth_bin = bitdepth_bin
        
        # make dictionary of data to be added to file
        self.params = {'exposure' : {'name' : 'Exposure',
                                     'unit' : 'nS',
                                     'data' : Exposure_nS,
                                     'isim' : True},
                       'unixtime' : {'name' : 'Unixtime',
                                     'unit' : 'nS',
                                     'data' : Unixtime_nS,
                                     'isim' : True}}
        
        # add non-raw params
        if self.raw_mode == False:
            nonraw_params = {'threshold': {'name' : 'Threshold',
                                           'unit' : 'keV',
                                           'data' : Threshold_keV,
                                           'isim' : False},
                             'DAC' : {'name' : 'DAC',
                                      'unit' : 'val',
                                      'data' : DAC_val,
                                      'isim' : False}}
            self.params.update(nonraw_params)
    
    
    def _print_testing_notes(self):
        m = '''
            #--------------------------------------------------
            # VERSION 0.76 (no documentation)
            Format is 256 bytes, zero byte padded.
            20150825 - currently 34 values, eg:
            
            '12B,000001,0,2015-08-11 17:55:11.682,1.000000E+0,2.700000E+1,3.600000E+0,150,020,000,000,000,000,000,000,100,010,125,125,100,100,080,100,120,050,128,004,255,108,120,160,148,401,401'
            
                bit depth                               12B|24B
                frame number (6 wide)                   000001
                counter or colour (in CM)?              0    # TODO check value
                date and time stamp (to ms)             2015-08-11 17:55:11.682
                exposure (ms)                           1.000000E+0
                threshold0                              2.700000E+1
                threshold1                              3.600000E+0
                DAC (27 of)                             150
            
            #--------------------------------------------------
            # VERSION 0.65.8 (differs from documentation)
            Variable length csv, zero byte padded. eg:
            
            'MQ1,000001,00384,01,0128,0128,U16,   2x2,01,2015-08-27 18:10:36.025832,0.010000,0,1,0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,3RX,000,000,000,000,000,000,000,000,175,010,200,125,100,100,093,100,099,030,128,004,255,127,128,177,167,000,000,MQ1A,2015-08-27T17:10:36.025832396Z,10000000nS,12,'
            
                id                                      MQ1
                frame number                            000001
                header length                           00384
                number of chips                         01
                image size x                            0128
                image size y                            0128
                binary no. fmt                          U16
                chip layout                             2x2
                hexadecimal of active chips             01
                date and time stamp (to us)             2015-08-27 18:10:36.025832
                exposure (s w/ us resolution)           0.010000
                counter number (0,1) or colour (0-7)    0
                colour mode bool                        1
                gain mode 0=SLGM, 1=LGM, 2=HGM, 3=SHGM  0
                TH0 (keV)                               0.000000E+0
                TH1 (keV)                               0.000000E+0
                TH2 (keV)                               0.000000E+0
                TH3 (keV)                               0.000000E+0
                TH4 (keV)                               0.000000E+0
                TH5 (keV)                               0.000000E+0
                TH6 (keV)                               0.000000E+0
                TH7 (keV)                               0.000000E+0
                
                REPEATED ONCE PER CHIP
                    chip version                        3RX
                    DAC (27 of)                         000
                
                    UNDOCUMENTED
                        more detailed id?               MQ1A
                        ns timestamp                    2015-08-27T17:10:36.025832396Z
                        exposure (ns)                   10000000nS
                        bit depth?                      12
            
            #--------------------------------------------------
            # VERSION 0.67.0.6 as 0.65.8
            
            Raw mode status is not recorded in hdr file. Comparison of binary headers:
            
            
            head -c 2000 12bit_multi_file/12bit_multi_file1.mib; echo 
            MQ1,000001,00384,01,0256,0256,U16,   1x1,01,2017-11-10 15:35:28.419324,0.005000,0,0,0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,3RX,060,510,000,000,000,000,000,000,100,010,100,125,100,100,064,100,070,030,128,004,255,125,128,179,167,511,511,MQ1A,2017-11-10T15:35:28.419324545Z,5000000ns,12,
            
            
            head -c 2000 1bit_raw.mib; echo 
            MQ1,000001,00384,01,0256,0256,R64,   1x1,01,2017-11-10 15:38:15.030531,0.005000,0,0,0,,MQ1A,2017-11-10T15:38:15.030531785Z,5000000ns,1,

            head -c 2000 6bit_raw.mib; echo 
            MQ1,000001,00384,01,0256,0256,R64,   1x1,01,2017-11-10 15:39:58.616402,0.005000,0,0,0,,MQ1A,2017-11-10T15:39:58.616402345Z,5000000ns,6,

            head -c 2000 12bit_raw.mib; echo 
            MQ1,000001,00384,01,0256,0256,R64,   1x1,01,2017-11-10 15:40:37.414250,0.005000,0,0,0,,MQ1A,2017-11-10T15:40:37.414250055Z,5000000ns,12,

            head -c 2000 24bit_raw.mib; echo 
            MQ1,000001,00384,01,0512,0256,R64,   1x1,01,2017-11-10 15:41:20.880248,0.005000,0,0,0,,MQ1A,2017-11-10T15:41:20.880248165Z,5000000ns,24,
            
            
            Differences:
                raw mode documented by 7th csv as R64
                after counter, color, gain, is empty string.
                missing are thresholds, chip version and dacs
                next values are same last 4 values begining with MQ1A
                last of these seems to indicate the bit depth
            
            Examples of missing:
                0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,3RX,060,510,000,000,000,000,000,000,100,010,100,125,100,100,064,100,070,030,128,004,255,125,128,179,167,511,511,
            
            
            
            ----------------------------------------------------------------------------------------------------
            # V 0.67.0.8 appears the same as 0.67.0.6
            
            with open('test_small_16/test_small_16.mib', 'rb') as f:
                t = fpdp.Merlin_binary_header_parser(f, fmt_ver=1)
            
            t.header
            
            MQ1,000001,00384,01,0256,0256,U32,   1x1,01,2018-03-01 15:10:00.059524,0.002000,0,0,0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,0.000000E+0,3RX,040,511,000,000,000,000,000,000,175,010,200,125,100,100,096,100,093,030,128,004,255,054,128,104,100,511,511,MQ1A,2018-03-01T15:10:00.059524623Z,2000000ns,24,
            
            '''
        print(m)



def _parse_dm_file(fn):
    '''
    Parse DM file to extract axes properties, tags, image data, and
    binary.
    
    Parameters
    ----------
    fn : string
        DM file name.
        
    Returns
    -------  
    (pixX, axisX, unitsX) : tuple
        Image x-axis information where:
            pixX : int
                Number of pixels.
            axisX : ndarray
                Pixel axis.
            unitsX : string
                Axis units.
    (pixY, axisY, unitsY) : tuple
        y-axis information, as above.
    tag_dict : dictionary
        Dictionary of image tags.
    im_data : ndarray
        Image data array.
    bin_file : binary object
        Complete binary DM file.
    
    Examples
    --------
    xaxis, yaxis, tag_dict, im_data, bin_file = _parse_dm_file('1.dm3')
    pixX, axisX, unitsX = xaxis
    pixY, axisY, unitsY = yaxis
    
    '''
    from hyperspy.io import load

    with open(fn, 'rb') as f:
        dm_bin = f.read()

    im = load(fn)
    dm_im = im.data

    tagd = im.original_metadata.as_dictionary()
    unitsX = im.axes_manager[0].units
    axisX = im.axes_manager[0].axis
    if len(im.axes_manager.shape)==1:
        pixX = im.axes_manager.shape[0]
        pixY = 1
        unitsY = im.axes_manager[0].units
        axisY = 'y'
    else:
        pixX, pixY = im.axes_manager.shape
        unitsY = im.axes_manager[1].units
        axisY = im.axes_manager[1].axis

    return (pixX, axisX, unitsX), (pixY, axisY, unitsY), tagd, dm_im, dm_bin



def _create_emd(fgp, gname, im_class, dim_names, dim_axes, dim_units, 
                data_name='', data_units='', *args, **kwargs):
    '''
    Create an EMD compatible dataset, with additional attributes.
    
    Parameters
    ----------
    fgp : one of [filename, hdf5 group, h5 file]
        Object in which EMD group will be made.
    gname : string
        EMD group name. If empty (''), EMD dataset will be in `fgp`. 
    im_class : bool
        booling controlling if data is an hdf5 image class.
    dim_names : list of strings
        Dimension names.
    dim_axes : list of ndarrays
        Dimension axes.
    dim_units : list of strings
        Dimension units.    
    data_name : string 
        Attribute for data group.
    data_units : string
        Attribute for data group.
    
    Additional parameters are passed to `create_dataset`. See h5py for
    details.
    
    Returns
    -------
    ds : hd5f dataset
        The created dataset. This will be in a closed file if `fgp` is 
        a filename. 

    '''
    
    
    for x in [dim_names, dim_axes, dim_units]:
        assert( type(x)==list )
    
    # should file be closed at end?
    closef = False
    fpgn_type = type(fgp)
    
    if fpgn_type in _str_type_list:
        # fgp is filename
        h5f = h5py.File(fgp, 'w')
        closef = True
    elif fpgn_type == h5py._hl.files.File:
        h5f = fpgn
    elif fpgn_type == h5py._hl.group.Group:
        h5f = fgp
    
    if gname:
        grp = h5f.create_group(name=gname)
    else:
        grp = h5f
    
    
    # Group attributes
    grp.attrs['emd_group_type'] = 1
    
    # This makes the HyperSpy file loader identify the N-D datasets
    # as Signal2D, making it easier to navigate and use
    if len(dim_names) >= 3:
        grp.attrs['signal_type'] = 'Signal2D'    
    
    
    ds = grp.create_dataset(name='data', *args, **kwargs)
    
    if isinstance(data_name, bytes):
        data_name = data_name.decode('utf-8')
    if isinstance(data_units, bytes):
        data_units = data_units.decode('utf-8')
    
    
    ds.attrs['name'] = data_name
    ds.attrs['units'] = data_units
    if im_class == True:
        ds.attrs['CLASS'] = np.string_('IMAGE')
        ds.attrs['IMAGE_VERSION'] =  np.string_('1.2')
    
    
    # add axes
    dim_dataset_names = ['dim'+str(x+1) for x in range(len(dim_names))]
    for i, dim_dataset_name in enumerate(dim_dataset_names):
        try:
            dim_ds = grp.create_dataset(name=dim_dataset_name, 
                                        data=dim_axes[i], 
                                        compression="gzip", 
                                        compression_opts=4)
        except Exception as e:
            #print(e)
            # Scalar datasets don't support chunk/filter options
            dim_ds = grp.create_dataset(name=dim_dataset_name,
                                        data=dim_axes[i])
        
        dim_name = dim_names[i]
        dim_unit = dim_units[i]
        if isinstance(dim_name, bytes):
            dim_name = dim_name.decode('utf-8')
        if isinstance(dim_unit, bytes):
            dim_unit = dim_unit.decode('utf-8')

        dim_ds.attrs['name'] = dim_name
        dim_ds.attrs['units'] = dim_unit
        
    if closef:
        h5f.close()
    return ds



def _create_dm_grp(fgp, gname, im_class, dim_names, dim_axes, dim_units,
               dmfn, dm_tagd, dm_bin, *args, **kwargs):
    '''
    Create an DM group containing an EMD compatible dataset, a
    dictionary of tags, and the binary file.
    
    Parameters
    ----------
    fgp : one of [filename, hdf5 group, h5 file]
        Object in which EMD group will be made.
    gname : string
        DM group name. If empty (''), DM dataset will be in `fgp`. 
    im_class : bool
        boolean controlling if data is an hdf5 image class.
    dim_names : list of strings
        Dimension names.
    dim_axes : list of ndarrays
        Dimension axes.
    dim_units : list of strings
        Dimension units.
    
    dmfn : string 
        DM filename.
    dm_tagd : dictionary
        DM tag dictionary.
    dm_bin : binary
        DM file binary.
    
    Additional parameters are passed to `create_dataset` for EMD. See 
    h5py for details.
    
    Returns
    -------
    grp : hd5f group
        The created DM group. This will be in a closed file if `fgp` is 
        a filename. 

    '''
    
    
    for x in [dim_names, dim_axes, dim_units]:
        assert( type(x)==list )
    
    closef = False
    fpgn_type = type(fgp)
    
    if fpgn_type in _str_type_list:
        h5f = h5py.File(fgp, 'w')
        closef = True
    elif fpgn_type == h5py._hl.files.File:
        h5f = fpgn
    elif fpgn_type == h5py._hl.group.Group:
        h5f = fgp
    
    if gname:
        grp = h5f.create_group(name=gname)
    else:
        grp = h5f
    
    # internal group 'version'
    grp.attrs['dm_group_type'] = 1
    
    # add DN filename with extension as attribute
    dmfn_dir, dmfn_fn = os.path.split(dmfn)
    grp.attrs['dm_filename'] = dmfn_fn
    
    # add EMD as subgroup
    _create_emd(grp, '', im_class, dim_names, dim_axes, dim_units, 
                data_name='Intensity', data_units='Counts', *args, **kwargs)
    
    # add binary dm file
    DM_bin = grp.create_dataset(name='bin', data=np.void(dm_bin))

    # dm tags
    DM_tags_grp = grp.create_group(name='tags')
    # exclude empty dicts which raise error when writing to hdf5
    tagdf = _flatten(dm_tagd, sep='/', include_empty=False)
    for k, v in tagdf.items():
        try:
            DM_tags_grp.create_dataset(name=k, data=v,
                                       compression="gzip", compression_opts=4)
        except Exception as e:
            #print(e)
            # Scalar datasets don't support chunk/filter options
            DM_tags_grp.create_dataset(name=k, data=v)       
    
    if closef:
        h5f.close()
    return grp



def _sort_multiple_binary_file_input(filename_list):
    """
    Function for sorting multiple binary files written by the Merlin 
    Medipix readout system in the acquisition order.
    
    Parameters
    ----------
    filename_list : list of strings
    
    Notes
    -----
    One of the settings on the Merlin readout system saves each frame
    as a separate file. This function will work if there are other 
    numbers in the filename, but there must be a non-numeric character
    between the file counter and any other numbers.

    """

    index_list = []
    # Extract index numbers from the filenames.
    # Makes sure the last number in the filename is chosen, in case there are several
    # numbers in the filename
    for filename in filename_list:
        temp_filename = filename.split(".")[-2]
        index_list.append(int(re.search('\d+',temp_filename[::-1]).group()[::-1]))

    # Sort the filename_list using the index_list
    new_filename_list = [filename_list for (index_list,filename_list) in sorted(zip(index_list,filename_list))]
    return(new_filename_list)



def _embed_source_in_hdf5_group(fpd_expt_grp):
    # embed source
    src_path = inspect.stack()[0][1]
    with open(src_path, 'r') as f:
        src_str = f.read() 
    
    src_ds = fpd_expt_grp.create_dataset(name='src', data=src_str)
    src_ds.attrs['src_path'] = src_path



def _embed_header_in_hdf5_group(fpd_expt_grp, header):
    fpd_hdr_grp = fpd_expt_grp.create_group(name='merlin_hdr')
    fpd_hdr_grp.attrs['string'] = header.hs
    
    fhdf = _flatten(header.hd, sep='/')
    for k, v in fhdf.items():
        try:
            fpd_hdr_grp.create_dataset(name=k, data=v, 
                                       compression="gzip", 
                                       compression_opts=4)
        except:
            fpd_hdr_grp.create_dataset(name=k, data=v)



def _create_sum_im_hdf5_dataset(group, base_kwd, det_pix_max_val,
                                dim_lens, dim_names, dim_axes, dim_units):
    ''' 
    Create sum_im dataset, returning dataset object.
    Sum of all detector signals at each scan pixel.
    '''
    
    sum_im_dtype = 'u8'
    assert det_pix_max_val*np.prod(dim_lens[-2:]) < np.iinfo(sum_im_dtype).max
    
    kwd = base_kwd.copy()
    shp = tuple(dim_lens[:-2])
    kwd.update({'shape' : shp,
                'dtype' : sum_im_dtype,
                'maxshape' : shp}) 
    fpd_sum_im_dataset = _create_emd(group, 'fpd_sum_im', True, 
                                     dim_names[:-2], dim_axes[:-2], dim_units[:-2],
                                     data_name='Intensity', data_units='Counts', **kwd)
    return fpd_sum_im_dataset



def _create_sum_dif_hdf5_dataset(group, base_kwd, det_pix_max_val,
                                 dim_lens, dim_names, dim_axes, dim_units):
    ''' 
    Create sum_dif dataset, returning dataset object.
    Sum of each detector pixel across all scan pixels.
    '''
    
    sum_dif_dtype = 'u8'
    assert det_pix_max_val*np.prod(dim_lens[:2]) < np.iinfo(sum_dif_dtype).max
    
    kwd = base_kwd.copy()
    shp = tuple(dim_lens[2:])
    kwd.update({'shape' : shp,
                'dtype' : sum_dif_dtype,
                'maxshape' : shp}) 
    fpd_sum_dif_dataset = _create_emd(group, 'fpd_sum_dif', True, 
                                      dim_names[2:], dim_axes[2:], dim_units[2:],
                                      data_name='Intensity', data_units='Counts', **kwd)
    
    fpd_sum_dif_dataset[...] = np.zeros_like(fpd_sum_dif_dataset,
                                    dtype=fpd_sum_dif_dataset.dtype)
    return fpd_sum_dif_dataset


def _create_mask_hdf5_dataset(group, base_kwd,
                              dim_lens, dim_names, dim_axes, dim_units):
    ''' 
    Create mask dataset, returning dataset object.
    '''
    
    dtype = bool
    
    kwd = base_kwd.copy()
    shp = tuple(dim_lens[-2:])
    kwd.update({'shape' : shp,
                'dtype' : dtype,
                'maxshape' : shp})
    kwd.pop('fillvalue')
    
    fpd_mask_dataset = _create_emd(group, 'fpd_mask', True, 
                                   dim_names[-2:], dim_axes[-2:], dim_units[-2:],
                                   data_name='Mask', data_units='Boolean', **kwd)
    return fpd_mask_dataset



def _write_dm_files_to_hdf5(group, base_kwd, dmfns,
                            dim_lens, dim_names, dim_axes, dim_units):
    '''
    Write DM file(s)
    '''

    for i, dmfn in enumerate(dmfns):
        kwd = base_kwd.copy()
        
        # TODO move to write dm and have _create_dm_grp handle all processing? 
        # This could allow it to handle more filetypes.
        _, _, tagd, dm_im, dm_bin = _parse_dm_file(dmfns[i])
        DM_dtype = 'u%d' %(tagd['ImageList']['TagGroup0']['ImageData']['PixelDepth'])            
        kwd.update({'data' : dm_im,
                    'dtype' : DM_dtype}) 
        
        _create_dm_grp(group, 'DM%d' %(i), True, 
                       dim_names[:2], dim_axes[:2], dim_units[:2],
                       dmfn, tagd, dm_bin, **kwd)



def _create_bin_header_str_dataset(group, base_kwd,
                                   dim_lens, dim_names, dim_axes, dim_units):
    '''
    Create FPD binary header string dataset, returning dataset object. 
    '''
    
    kwd = base_kwd.copy()
    shp = tuple(dim_lens[:-2])
    kwd.update({'shape' : shp,
                'dtype' : h5py.special_dtype(vlen=bytes),
                'maxshape' : shp})
    kwd.pop('fillvalue')
    
    fpd_binary_hdr_dataset = _create_emd(group, 'binary_hdr', False, 
                                         dim_names[:-2], dim_axes[:-2], dim_units[:-2],
                                         data_name='binary_hdr', data_units='', **kwd)
    return fpd_binary_hdr_dataset



def _create_fpd_data_hdf5_dataset(group, base_kwd, det_dtype,
                                  dim_lens, dim_names, dim_axes, dim_units,
                                  chunks, compression_opts):
    '''
    Create FPD data dataset, returning dataset object. 
    '''
    
    kwd = base_kwd.copy()
    shp = tuple(dim_lens)
    kwd.update({'shape' : shp,
                'dtype' : det_dtype, 
                'chunks' : chunks,
                'compression_opts' : compression_opts,
                'maxshape' : shp}) 
    
    fpd_dataset = _create_emd(group, 'fpd_data', True, 
                              dim_names, dim_axes, dim_units, 
                              data_name='Intensity', data_units='Counts',  **kwd)
    return fpd_dataset



def _create_bin_header_param_hdf5_dataset(group, base_kwd, det_dtype,
                                          dim_lens, dim_names, dim_axes, dim_units,
                                          params):
    '''
    Create FPD binary header datasets, returning list of datasets. 
    '''
    
    bhd_dss = []
    for pk in params.keys():
        p = params[pk]
        data = p['data']
        data_dim_name_s = p['name']
        data_unit_s = p['unit']
        isim = p['isim']
        
        kwd = base_kwd.copy()
        try:
            # arrays
            data_len = len(data)
            data_dtype = data.dtype  
            shp = tuple(dim_lens[:-2])
            kwd.update({'shape' : shp + (data_len,),
                        'dtype' : data_dtype,
                        'maxshape' : shp + (data_len,)})
            bhd_ds = _create_emd(group, data_dim_name_s, isim,
                                dim_names[:-2] + [data_dim_name_s],
                                dim_axes[:-2] + [np.arange(data_len)],
                                dim_units[:-2] + [data_unit_s],
                                data_name = data_dim_name_s,
                                data_units = data_unit_s,
                                **kwd)
        except TypeError:
            # scalar
            data_len = 0
            data_dtype = type(data)
            shp = tuple(dim_lens[:-2])
            kwd.update({'shape' : shp,
                        'dtype' : data_dtype,
                        'maxshape' : shp})  
            bhd_ds = _create_emd(group, data_dim_name_s, isim,
                                dim_names[:-2],
                                dim_axes[:-2],
                                dim_units[:-2],
                                data_name = data_dim_name_s,
                                data_units = data_unit_s,
                                **kwd)
        bhd_dss.append(bhd_ds)
    return bhd_dss



def _read_header_and_data(fp, fmt_ver, im_bytesize):
    '''
    Helper function to read binary header and data.
    '''
    
    try:
        Mbhp = Merlin_binary_header_parser(fp, fmt_ver)
        bin_data = fp.read(im_bytesize)
    except Exception as e:
        if str(e)=='EOF':
            return ''
        else:
            raise
    return (Mbhp.hs, Mbhp.params, bin_data)


def _raw_merlin_to_array(data_buffer, det_dtype, bitdepth_data, bitdepth_bin, raw_mode, detY=256, detX=256):
    '''
    Convert Merlin data from string to array.
    
    Parameters
    ----------
    data_buffer : binary string to convert
        Binary string to convert.
    det_dtype : numpy dtype
        numpy dtype in which data is stored in string
    bitdepth_data : integer
        Data bitdepth: 1, 6, 12, 24.
    bitdepth_bin : integer
        Binary bitdepth (non-raw: 8, 16 or 32, raw: 64).
    raw_mode : bool
        If True, data_buffer is in raw mode form.
    detY : int
        Number of detector y pixels. See notes.
    detX : int
        Number of detector x pixels. See notes.
    
    Returns
    -------
    im_array : ndarray
        2-D array of detector data of appropriate type.
    
    Notes
    -----
    `detY` and `detX` are the modified from the real pixel count by running
    in colour mode.
    
    '''
    
    raw_1bit = raw_mode and (bitdepth_data == 1)
    
    # process bin_data
    if raw_1bit:
        # raw 1bit is really 1 bit
        # this is all really slow!
        im_array = np.frombuffer(data_buffer, dtype='>u1')
        
        im_array = np.array([np.unpackbits(byte) for byte in im_array], dtype=det_dtype)
        im_array = im_array.flatten().reshape(detY, detX)
    else:
        im_array = np.frombuffer(data_buffer, dtype=det_dtype).reshape(detY, detX)
    
    if raw_mode:
        # raw mode needs data flipped in column sections. 
        #n = 64  # 1 bit
        #n = 8   # 6 bit
        #n = 4   # 12 bit
        #n = 2   # 24 bit (untested)
        
        # overwrite bitdepth_bin which is always 64 with real bitdepth
        bitdepth_bin = int(max(1, 2**np.ceil(np.log2(bitdepth_data))//8)) * 8
        n = 64 // bitdepth_bin
        if raw_1bit:
            n = 64
        
        indices = np.arange(detX/n+1, dtype=int)*n
        im_array_temp = np.empty_like(im_array)
        for start, stop in zip(indices[:-1], indices[1:]):
            im_array_temp[:, start:stop] = im_array[:, start:stop][:,::-1]
        im_array = im_array_temp
    return im_array[::-1]


def _image_array_properties(detY, detX, Mbhp):
    '''
    Determine image array properties 
    '''
    # detector data storage bitdepth
    # min x in 2**x bytes. The max makes 1bit -> 8bit
    nbytes = int(max(1, 2 ** np.ceil(np.log2(Mbhp.bitdepth_data)) // 8))
    det_dtype = np.dtype('>u%d' %(nbytes))
    
    im_bytesize = detX*detY*nbytes
    # raw 1bit is really 1 bit
    raw_1bit = Mbhp.raw_mode and (Mbhp.bitdepth_data == 1)
    if raw_1bit:
        im_bytesize = int(detX*detY/8)
    return nbytes, det_dtype, im_bytesize



class CubicImageInterpolator:
    def __init__(self, mask):
        '''
        CloughTocher2DInterpolator for 2-D arrays at locations where mask is True.
        
        Parameters
        ----------
        mask : 2-D bool array
            Mask indicating which values are to be interpolated.
        '''
        
        self.mask = np.asarray(mask, dtype=bool)
        self.keep_inds = np.where(self.mask==False)
        self.interp_inds = np.where(self.mask==True)
        self.points = np.asarray(self.keep_inds).T
        self.xi = np.asarray(self.interp_inds).T
                
        # dummy values for initialisation
        values = np.ones(self.points.shape[0], dtype=np.float)
        self.ip = CloughTocher2DInterpolator(self.points, values, fill_value=np.nan,
                                             rescale=False)
        
    def interpolate_image(self, image, clip_min=None, clip_max=None, in_place=True):
        '''
        Iinterpolate image
        
        Parameters
        ----------
        image : 2-D array
            Image to be processed
        clip_min : None or scalar
            Minimum value to clip interpolated values to.
        clip_max : None or scalar
            Maximum value to clip interpolated values to.
        in_place : bool
            If True, the image is processed in place. Otherwise, a new image is returned.
        
        Returns
        -------
        image : 2-D array or None 
            Interpolated input array or None. See `in_place` for details.
        '''
        
        self.ip.values[:] = image[self.keep_inds].astype(self.ip.values.dtype)[:, None]
        interp_vals = self.ip(self.xi)
        if clip_min is not None or clip_max is not None:
            interp_vals = interp_vals.clip(clip_min, clip_max)
        if not in_place:
            image = image.copy()
            image[self.interp_inds] = interp_vals.astype(image.dtype)
            return image
        else:
            image.setflags(write=1) # make sure image is writable
            image[self.interp_inds] = interp_vals.astype(image.dtype)



class MerlinBinary:
    def __init__(self, binfns, hdrfn, dmfns=[], ds_start_skip=0, row_end_skip=1,
                 scanYalu=None, scanXalu=None, detYalu=None, detXalu=None, 
                 detY=256, detX=256, sort_binary_file_list=True, 
                 strict=True, *args, **kwargs):
        '''
    
        Class for reading data produced by the Merlin Medipix 3 readout system.
        The class exposes an array-like interface to allow reading directly
        from the file to memory, and can convert the detector data and metadata
        into an hdf5 file.
        
        The data order c-order: scanY, scanX, [colour,] detY, detX
        The colour axis is omitted if singular.
        
        Parameters
        ----------
        binfns : str, or list of str
            Binary FPD filenames to process.
        hdrfn : str
            FPD text header filename.
        dmfns : str, or list of str
            DM filenames to process. Use [] for no files. The scan 
            dimensions are parsed from the first file. If no files are
            supplied, scanXpau and scanYalu control scan size.
        ds_start_skip : int
            Number of scan pixels skipped at start of input file.
        row_end_skip : int
            Number of pixels to skip after end of each row.
            This can be used to omit false triggers during beam flyback.
        scanXalu : tuple or None
            Determines scan size if no `dmfns` are specified. The tuple must
            be in the form (axis, label, units). See Notes.
            scanXaxis : int or iterable
                If an integer, this is taken as the axis length and an axis is
                generated. Otherwise, scanX is converted to an axis directly.
            scanXlabel : str
                Name of x-axis.
            scanXunits : str
                Units of the x-axis.
        scanYalu : tuple or None
            As `scanXalu`, but for y-axis.
        detYalu : tuple or None
            As `scanXalu`, but for detector y-axis. The axis size should be 
            the size of the data axis. See also `detY`.
        detXalu : tuple or None
            As `scanXalu`, but for detector x-axis.
        detY : int
            The number of hardware pixels is SPM mode.
            This value will be automatically modified in colour mode.
        detX : int
            As `detY`, but for detector x-axis.
        sort_binary_file_list : bool
            If True, and if binfns is a list, the filenames will be sorted
            by frame number.
        strict : bool
            If True, file format matching is strict and only known versions 
            will be processed. If False, the most recent known version will
            be tried. 
        
        Notes
        -----        
        If 'scanXalu' or 'scanYalu' not None, these take precedence over
        scan parameters from DM files. If None, the scan parameters 
        are parsed from the first DM file. For other files, the axes information
        can be parsed with:    
        
        >>> from hyperspy.io import load
        >>> im = load('image_filename')
        >>> scanXalu, scanYalu = [(m.axis, m.name, m.units) for m in im.axes_manager.signal_axes]
        
        Non-scan data can be processed by setting the y-axis size as 1, and
        the x-axis size the same as the number of images. In this case,
        `ds_start_skip` and `row_end_skip` should be set to 0.
        
        If the scanXalu axis is None, it is automatically generated from the header
        file with axis being the index. Note that the header file contains the 
        maximum number of frames and the real number of frames could be smaller by
        design or error.
        
        If no scan information is passed, and a single binary file is provided, all
        images in the file are processed as though the shape was [nimages, 1, detY, detX].
        In this case, `row_end_skip` should be set to 0 unless there are a known
        number of unwanted images at the end of the dataset.
        
        The class exposes an array-like interface that may be sliced and indexed,
        with ndims, size, nbytes, shape, dtype etc attributes. Since the data are
        read from disc, these should not be changed after the class is initialised. 
        
        When the class is indexed, the file is parsed from the beginning, since
        the file format allows each header length to be of a different size, and
        so multiple single files may be converted.
        
        '''

        self._binfns = binfns
        self._hdrfn = hdrfn
        self._dmfns = dmfns
        self._ds_start_skip = ds_start_skip
        self._row_end_skip = row_end_skip
        self._scanYalu = scanYalu
        self._scanXalu = scanXalu
        self._detYalu = detYalu
        self._detXalu = detXalu
        self._detY = detY
        self._detX = detX
        self._sort_binary_file_list = sort_binary_file_list
        self._strict = strict
        #self._memmap = memmap
        
        self._condition_params()
        self._parse_headers()
        self._determine_axes()
        
        # data and image dimensions / size
        self._ims_shape = self._dim_lens[:-2]
        self._total_no_ims = np.prod(self._ims_shape)
        
        # set getitem attributes
        self.shape = tuple(self._dim_lens)
        self.size = np.prod(self._dim_lens)
        self.ndim = len(self._dim_lens)
        self.dtype = self._det_dtype
        self.nbytes = (self.dtype.itemsize * 8) * self.size

    
    def _condition_params(self):
        # if binfns is string, convert to list for looping  
        if type(self._binfns) in _str_type_list:
            self._binfns = [self._binfns]
        else:
            if self._sort_binary_file_list:
                m = "Sorting binfns by frame number, deactivite sorting by 'setting sort_binary_file_list=False'."
                _logger.info(m)
                self._binfns = _sort_multiple_binary_file_input(self._binfns)
        # if dmfns is string, convert to list for looping over 1 or more DM files.
        if type(self._dmfns) in _str_type_list:
            self._dmfns = [self._dmfns]    
    
    def _parse_headers(self):
        # parse header file
        self._Mhfp = Merlin_hdr_file_parser(self._hdrfn, strict=self._strict)
        # parse first binary header
        with open(self._binfns[0], "rb") as f:
            self._Mbhp = Merlin_binary_header_parser(f, self._Mhfp.fmt_ver)

        # set detector size and colour depth from hdr file
        self._colourN = 1
        if  self._Mhfp.CM:
            self._detX //= 2
            self._detY //= 2
            self._colourN *= 4*self._Mhfp.AC

        rtn = _image_array_properties(self._detY, self._detX, self._Mbhp)
        self._nbytes, self._det_dtype, self._im_bytesize = rtn
    
    
    def _determine_axes(self):
        # Determine scanX/Y and their axes and units.
        # If non None, use these over those in DM file
        if len(self._binfns) == 1 and self._scanXalu is None and self._scanYalu is None and len(self._dmfns) == 0:
            # If a single binary file is provided with no dimensional info and no DM files, determine number of frames based
            # on the bit depth and the file size. Resulting data structure will be: [nframes , 1 , detY , detX]
            if self._row_end_skip != 0:
                _logger.info("Do you really want to set 'row_end_skip' to %d?" %(self._row_end_skip))
            if self._ds_start_skip != 0:
                _logger.info("Do you really want to set 'ds_start_skip' to %d?" %(self._ds_start_skip))
            # This will fail in the unlikely case of the the header size
            # changing mid-file, but should work in most cases.
            nframes = int(os.path.getsize(self._binfns[0]) / (self._Mbhp.header_bytesize +
                                                              self._im_bytesize))
            # subtract _ds_start_skip / offset here, since nframes is total number of images in the file
            nframes = nframes - self._ds_start_skip
            self._scanXalu = (nframes, 'xaxis', 'pixels')
            self._scanYalu = (1, 'yaxis', 'pixels')
        elif self._scanYalu is None or self._scanXalu is None or (
                self._scanXalu is not None and self._scanXalu[0] is None and self._scanXalu[1] is None):
            # must use DM file
            pauX, pauY, tagd, dm_im, dm_bin = _parse_dm_file(self._dmfns[0])
        
        if self._scanYalu is not None:
            scanYaxis, scanYlabel, scanYunits = self._scanYalu
            if type(scanYaxis) is int:
                scanYaxis = list(range(scanYaxis))
            else:
                scanYaxis = np.array(scanYaxis)
            scanY = len(scanYaxis)
        else:
            scanY, scanYaxis, scanYunits = pauY
            scanYlabel = 'scanY'
        
        if self._scanXalu is not None:
            scanXaxis, scanXlabel, scanXunits = self._scanXalu
            if scanXaxis is None:
                # generate 'scan' size and an index axis from header
                scanXaxis = int(self._Mhfp.hd['frames_in_acquisition'])
            if type(scanXaxis) is int:
                scanXaxis = list(range(scanXaxis))
            else:
                scanXaxis = np.array(scanXaxis)
            if scanXlabel is None:
                scanXlabel = 'scanX'
            scanX = len(scanXaxis)
        else:
            scanX, scanXaxis, scanXunits = pauX
            scanXlabel = 'scanX'
        
        self._scanY = scanY
        self._scanX = scanX
        
        
        # detector axes
        if self._detYalu is None:
            self._detYalu = (self._detY, 'detY', 'pixels')
        detYa, detYl, detYu = self._detYalu
        if type(detYa) is int: # use as length
            detYa = list(range(detYa))
        else: # use directly
            detYa = np.array(detYa)
        if len(detYa) != self._detY:
            _logger.exception("y-axis detector (%d) and data (%d) pixels don't match" %(len(detYa), self._detY))
        
        if self._detXalu is None:
            self._detXalu = (self._detX, 'detX', 'pixels')
        detXa, detXl, detXu = self._detXalu
        if type(detXa) is int: # use as length
            detXa = list(range(detXa))
        else: # use directly
            detXa = np.array(detXa)
        if len(detXa) != self._detX:
            _logger.exception("x-axis detector (%d) and data (%d) pixels don't match" %(len(detXa), self._detX))
        
        
        # FPD dataset axes details
        # TODO specify colour and detector axes and units
        # could be custom image tag in DM.
        self._Caxis = [x+1 for x in range(self._colourN)]
        self._dim_axes = [scanYaxis, scanXaxis, self._Caxis, detYa, detXa]
        self._dim_names = [scanYlabel, scanXlabel, 'colour', detYl, detXl]
        self._dim_units = [scanYunits, scanXunits, 'colour_index', detYu, detXu]
        
        if not self._Mhfp.CM:
            # rm colour axis if singular
            _logger.info('Removing singular colour axis.')
            del self._dim_axes[2]
            del self._dim_names[2]
            del self._dim_units[2]
            pass
        self._dim_lens = [len(t) for t in self._dim_axes]
        _logger.info('FPD data shape: ' + str(self._dim_lens))
    
    
    def write_hdf5(self, h5fn=None, chunks=None, scan_chunks=(16, 16), im_chunks=(16, 16),
                   compression_opts=4, repack=True, ow=False, embed_header_file=True,
                   embed_source=False, count_extra=True, mask=None, allow_memmap=True):
        '''
        Convert the dataset into an hdf5 file composed of EMD [1] data sets.
        
        Parameters
        ----------
        h5fn : str
            hdf5 output filename. If None, the first binary filename is used
            with a '.hdf5' extension.
        chunks : tuple of length equalling dimensionality of data
            fpd dataset chunking for all axes. Note, this takes precedence
            over any values set for scan and image chunking. See Notes.
        scan_chunks : length 2 tuple
            y and x fpd data chunking for scan dimensions. See Notes.
        im_chunks : length 2 tuple
            y and x fpd data chunking for image dimensions. See Notes.
        compression_opts : int
            fpd dataset gzip compression level in interval [0,9].
        repack : bool
            If True, fpd_data will be first written to an uncompressed temporary
            file, before being copied to the final file. See notes.
        ow : bool
            If True, pre-existing hdf5 output files are overwritten without asking.
        embed_header_file : bool
            If True, the Merlin header file is embedded in the hdf5 file.
        embed_source : bool
            If True, the source code used to generate the hdf5 file is embedded.
        count_extra : bool
            If True, extra images in input data are counted and reported.
        mask : None or 2-D bool array
            If not None, the detector images where mask is True are replaced
            with cubic interpolated values. The mask and interpolation parameters
            are stored as a dataset and attribute.
        allow_memmap : bool
            If True, files will be memmory mapped to increase conversion speed.
        
        Notes
        -----
        `chunks` sets the chunking for all axes of the fpd dataset and takes 
        precedence over the scan and image chunking parameters. If `chunks`
        is None, the fpd data chunking is set by `scan_chunks` and `im_chunks`,
        with the entire colour axis (when non-singular) as one chunk.
        
        If the file can be memory mapped, this is used to access the image data
        and write it to the hdf5 file one chunk at a time. If this is not possible,
        to efficiently chunk in the scan axes repacking is used. If `repack` is True,
        the fpd data is written to a temporary file, then copied to the compressed /
        chuncked file. The copying is done by only loading one chunk at a time, so
        this is RAM efficient but disk space expensive. Increasing chuncking in this
        way can significantly reduced the final file size and improve processing
        speed.
        
        If repacking is disabled, setting the scan axis chunks to anything other
        than (1, 1) will be slow. Because the binary Merlin data format is
        sequential, for chunks greater than 1 in the scan axes, h5py would have
        to deal with many successive writes to each chunk, probably uncompressing
        and recompressing the data each time.
        
        The memory mapped interface has a y-axis flip compared to the hdf5 file. 
        
        References
        ----------
        [1] http://emdatasets.lbl.gov/spec/
        
        '''
        
        file_format_version = __version__
        fpd_version_attr_name = 'fpd_version'
    
        # default emd parameters
        emd_ds_default = {'data' : None,
                          'compression' : 'gzip',
                          'compression_opts' : 4,
                          'shuffle' : True,
                          'fillvalue' : np.nan,
                          'track_times' : True,
                          'fletcher32' : True}
        
        # set chunking
        if chunks is not None:
            # use chunks directly
            if not len(chunks) == len(self._dim_lens):
                message = "'chunks' length (%d) does not match data length (%d)." %(len(chunks), len(self._dim_lens))
                raise Exception(message)
        else:
            # check for lower precedence chunking parameters
            chunks = scan_chunks + (1,)*(len(self._dim_lens)-4) + im_chunks
        
        # coerce chunks to be <= shape
        chunks = tuple([min(chk, shp) for chk, shp in zip(chunks, self._dim_lens)])
        _logger.info('FPD data chunking: ' + str(chunks))
        
        # condition filename
        if h5fn is None:
            h5fn = os.path.splitext(self._binfns[0])[0]+'.hdf5'
        if not ow and os.path.isfile(h5fn):
            reply = _input_fn("File '%s' already exists. Overwrite? ([y]/n): " %(os.path.abspath(h5fn)) )
            if reply.strip().lower() not in ['y', 'yes', '']:
                print('Doing nothing.')
                return
        _logger.info('Output: ' + os.path.abspath(h5fn))
        
        # if memmap is possible, use it for reading chunks
        memmap_possible = allow_memmap and self._memmap_check(throw_error=False)
        if memmap_possible:
            m = "Memory mapping the file is possible, so repacking is disabled."
            _logger.info(m)
            repack = False
            mm = self.get_memmap()
            
        if repack:
            m = "This will use a lot of temporary disk space, set 'repack=False' if this is an issue."
            _logger.warning(m)
            # make temp file 
            h5fn_tmp = h5fn + '.tmp'
            h5f_tmp = h5py.File(h5fn_tmp, 'w', driver=None)
            h5f_tmp_fpd = h5f_tmp.create_dataset("fpd_data", shape=self._dim_lens, dtype=self._det_dtype)
        elif not memmap_possible:
            # warn about chunking
            non_data_chunks = np.array(chunks[:-2])
            if (non_data_chunks > 1).any():
                m = "This could be very slow. Try setting 'repack=True'."
                _logger.warning(m)    
        
        # create main hdf5
        with h5py.File(h5fn, 'w', driver=None) as h5f:
            # http://docs.h5py.org/en/latest/faq.html?highlight=core
            # http://docs.h5py.org/en/latest/high/file.html?highlight=file%20drivers
            
            # EMD file version
            h5f.attrs['version_major'] = 0
            h5f.attrs['version_minor'] = 2
            
            # file format version
            vmajor, vminor, vpatch = [int(x) for x in file_format_version.split('.')]
            h5f.attrs[fpd_version_attr_name] = file_format_version
            h5f.attrs['fpd_version_major'] = vmajor
            h5f.attrs['fpd_version_minor'] = vminor
            h5f.attrs['fpd_version_patch'] = vpatch
            
            # fpd package version
            vmajor, vminor, vpatch = [int(x) for x in fpd_pkg_version.split('.')]
            h5f.attrs['fpd_pkg_version'] = fpd_pkg_version
            h5f.attrs['fpd_pkg_version_major'] = vmajor
            h5f.attrs['fpd_pkg_version_minor'] = vminor
            h5f.attrs['fpd_pkg_version_patch'] = vpatch
            
            ### Create groups / datasets and populate all except binary FPD data. 
            # fpd experiment group (top level)
            fpd_expt_grp = h5f.create_group(name='fpd_expt')
            
            # source
            if embed_source:
                _embed_source_in_hdf5_group(fpd_expt_grp)
            
            # header file
            if embed_header_file:
                _embed_header_in_hdf5_group(fpd_expt_grp, self._Mhfp)
            
            # sum_im (sum of all detector signals at each scan pixel)
            det_pix_max_val = 2**self._Mbhp.bitdepth_data-1
            fpd_sum_im_dataset = _create_sum_im_hdf5_dataset(fpd_expt_grp,
                                                            emd_ds_default,
                                                            det_pix_max_val, 
                                                            self._dim_lens, self._dim_names, 
                                                            self._dim_axes, self._dim_units)
            
            # sum_dif (sum of each detector pixel across all scan pixels)
            fpd_sum_dif_dataset = _create_sum_dif_hdf5_dataset(fpd_expt_grp, 
                                                            emd_ds_default, 
                                                            det_pix_max_val, 
                                                            self._dim_lens, self._dim_names, 
                                                            self._dim_axes, self._dim_units)
            
            # Write DM files
            _write_dm_files_to_hdf5(fpd_expt_grp, emd_ds_default, self._dmfns,
                                    self._dim_lens, self._dim_names, self._dim_axes, self._dim_units)
            
            # FPD binary header string. 
            fpd_binary_hdr_str_dataset = _create_bin_header_str_dataset(fpd_expt_grp, 
                                                                        emd_ds_default,
                                                                        self._dim_lens, self._dim_names, 
                                                                        self._dim_axes, self._dim_units)
            # Create FPD data.
            fpd_dataset = _create_fpd_data_hdf5_dataset(fpd_expt_grp, emd_ds_default, 
                                                        self._det_dtype, self._dim_lens, self._dim_names, 
                                                        self._dim_axes, self._dim_units, chunks, 
                                                        compression_opts)
            
            # Binary header params
            bhd_dss = _create_bin_header_param_hdf5_dataset(fpd_expt_grp, emd_ds_default, 
                                                            det_pix_max_val, self._dim_lens, 
                                                            self._dim_names, self._dim_axes, 
                                                            self._dim_units, self._Mbhp.params)
            
            # mask prep
            if mask is not None:
                mask = np.asarray(mask, dtype=bool)
                mask = mask
                if mask.any() is False:
                    _logger.warning("Mask is all False, mask has been set to None")
                    mask = None
            if mask is not None:
                # create dataset
                fpd_mask_dataset = _create_mask_hdf5_dataset(fpd_expt_grp,
                                                emd_ds_default,
                                                self._dim_lens, self._dim_names, 
                                                self._dim_axes, self._dim_units)
                fpd_mask_dataset[...] = mask
                fpd_mask_dataset.parent.attrs['mask_method'] = 'scipy.interpolate.CloughTocher2DInterpolator'
                
                # set up for interpolation
                CI = CubicImageInterpolator(mask)
            
            
            # scanXbindata is dimension in bin file >= scanX due to row_end_skip
            scanXbindata = self._scanX + self._row_end_skip
            
            # (scanY, scanXbindata[, colourN])
            ims_inc_extra_shape = self._ims_shape[:]
            ims_inc_extra_shape[1] = scanXbindata
            ims_inc_extra_shape = tuple(ims_inc_extra_shape)
            total_no_ims_inc_extra = np.prod(ims_inc_extra_shape)
            
            
            ### Process binary file(s), parsing header each time
            i = 0   # index in scan, including row ends
            j = 0   # index of read data
            k = 0   # index of saved data
            stop = False
            pbar = tqdm(total=self._total_no_ims, mininterval=0, leave=True, unit='images')
            for binfn_index, binfn in enumerate(self._binfns):
                if stop == True:
                    # needed for multiple single images and breaking loop over iterator
                    break
                # loop over input files
                with open(binfn, "rb") as f:
                    fp = f        # file reference
                    
                    # create partial for looping
                    read_binary_func = partial(_read_header_and_data, fp, self._Mhfp.fmt_ver, self._im_bytesize)
                    bin_file_iter = iter(read_binary_func, '')
                    for (hdr_str, hdr_params, data_buffer) in bin_file_iter:
                        if j < self._ds_start_skip:
                            pass
                        else:
                            try:
                                sYi_sXi_opCi = np.unravel_index(i, ims_inc_extra_shape, 'C')
                                scanYind, scanXind = sYi_sXi_opCi[:2]
                                s = np.s_[sYi_sXi_opCi]
                                if self._row_end_skip and scanXind > self._scanX-1:
                                    i += 1
                                    # skip row_end_skip
                                    pass
                                else:
                                    # process bin_data
                                    im_array = _raw_merlin_to_array(data_buffer, 
                                                                    self._det_dtype, 
                                                                    self._Mbhp.bitdepth_data,
                                                                    self._Mbhp.bitdepth_bin,
                                                                    self._Mbhp.raw_mode,
                                                                    self._detY, self._detX)
                                    if mask is not None:
                                        CI.interpolate_image(image=im_array, 
                                                             clip_min=0, 
                                                             clip_max=det_pix_max_val,
                                                             in_place=True)
                                        # this is repeated if memmapping file
                                        # but it is relatively fast, so ok for now
                                    
                                    # sum_im image
                                    fpd_sum_im_dataset[s] = im_array.sum()
                                    # sum_dif image
                                    if self._Mhfp.CM:
                                        fpd_sum_dif_dataset[sYi_sXi_opCi[2:],:,:] += im_array
                                    else:
                                        fpd_sum_dif_dataset[:,:] += im_array
                                    # fpd bin_data
                                    if not memmap_possible:
                                        if repack:
                                            h5f_tmp_fpd[s + (np.s_[:],)*2] = im_array
                                        else:
                                            fpd_dataset[s + (np.s_[:],)*2] = im_array
                                    
                                    # binary header string
                                    fpd_binary_hdr_str_dataset[s] = hdr_str
                                    # bin hdr
                                    for pk in hdr_params.keys():
                                        ds = fpd_expt_grp[hdr_params[pk]['name']]['data']
                                        ds[s] = hdr_params[pk]['data']
                                    i += 1
                                    k += 1
                                    pbar.update(1)
                            except ValueError as e:
                                # detect unravel index error for more images than data
                                e1 = str(e)=='invalid entry in index array' # older numpy
                                e2 = 'is out of bounds' in str(e) # newer numpy
                                if e1 or e2:
                                    if count_extra:
                                        if len(self._binfns)==1:
                                            # single file
                                            # Remaining data after processing last row,
                                            # including row_end_skip.
                                            no_extra_images = sum(1 for _ in bin_file_iter)
                                        else:
                                            # multiple files
                                            no_extra_images = len(self._binfns) - (binfn_index+1)
                                        m = '%d images at end of file(s) not processed!' %(no_extra_images)
                                        _logger.warning(m)
                                    else:
                                        m = 'Extra images at end of file(s) not processed!'
                                        _logger.warning(m)
                                        m = "Use 'count_extra=True' to count extra images."
                                        _logger.info(m)
                                    stop = True
                                    break
                                else:
                                    raise
                        j+=1
            if k+1 < self._total_no_ims:
                m = 'Only %d of expected %d images read!' %(k+1, self._total_no_ims)
                _logger.warning(m)
            pbar.close()
            
            
            if repack:
                _logger.info('Repacking data.')
                
                data_chunks = fpd_dataset.chunks
                data_shape = h5f_tmp_fpd.shape
                
                # loop over axes           
                sinds, n = slice_indices(data_shape, data_chunks)
                
                for si in tqdm(sinds, total=n, unit='chunks'):
                    s = tuple([slice(x[0],x[1]) for x in si])
                    fpd_dataset[s] = h5f_tmp_fpd[s]
                
                # close and delete file
                h5f_tmp.close()
                os.remove(h5fn_tmp)
            
            if memmap_possible:
                _logger.info('Packing memmaped data.')
                
                data_chunks = fpd_dataset.chunks
                data_shape = mm.shape
                
                if mask is None:
                    # loop over chunks           
                    sinds, n = slice_indices(data_shape, data_chunks)
                    
                    for si in tqdm(sinds, total=n, unit='chunks'):
                        s = tuple([slice(x[0],x[1]) for x in si])
                        fpd_dataset[s] = mm[s]
                else:
                    # loop over chunks only in non-image axes
                    data_chunks = fpd_dataset.chunks[:-2]
                    sinds, n = slice_indices(data_shape, data_chunks)
                    
                    for si in tqdm(sinds, total=n, unit='non-image chunks'):
                        s = tuple([slice(x[0],x[1]) for x in si])
                        nis = np.ascontiguousarray(mm[s])     # non_image_slice
                        
                        nis_shape = nis.shape
                        nis.shape = (np.prod(nis_shape[:-2]),) + nis_shape[-2:]
                        for im_array in nis:
                            CI.interpolate_image(image=im_array, 
                                                 clip_min=0, 
                                                 clip_max=det_pix_max_val,
                                                 in_place=True)                  
                        nis.shape = nis_shape
                        
                        fpd_dataset[s] = nis
                    
                    # need to load entire image, run through filter and write as chunks
                    # loop over slices in non-image dimensions
                    #_interp_image_partial(im_array)
                    # loop over slices in image dimensions
                    # write to file
                        
                del mm
                
        return h5fn
    
    def _memmap_check(self, throw_error=True):
        try:
            if len(self._binfns) > 1:
                raise NotImplementedError('Only single multi-image binary files may be memory mapped.')
        
            if self._Mbhp.raw_mode:
                raise NotImplementedError('Raw data cannot be memory mapped.')
                # This could be done, but it would be up to the user to unravel the
                # images when in-memory.
            
            if self._Mbhp.bitdepth_data == 1:
                raise NotImplementedError('1 bit data cannot be memory mapped.')
            
            if self._Mbhp.header_bytesize % self._Mbhp.bitdepth_bin != 0:
                raise NotImplementedError('The header is not an integer multiple of the dtype')
        except NotImplementedError:
            print("INFO: The only way to access the data is to index the class's array-like")
            print("INFO: interface to read the data into memory, or convert the data to an hdf5")
            print("INFO: file with the `write_hdf5` method.")
            if throw_error:
                raise
            else:
                return False
        return True
        
        
    def get_memmap(self):
        '''
        Returns a memory mapped array for out-of-core data access. 
        Delete the memmap instance to close the file.
        
        Returns
        -------
        mm : numpy.core.memmap.memmap
            Memory mapped on-disk array. To close the file, delete the object
            with `del mm`.
        
        Examples
        --------
        >>> from fpd.fpd_file import MerlinBinary, DataBrowser  +SKIP
        >>> import numpy as np  +SKIP
        
        >>> mb = MerlinBinary(binary_filename, header_filename, dm_filename)    +SKIP
        
        >>> mm = mb.get_memmap()    +SKIP
        
        This may be plotted with a navigation image generated from the data:
        >>> nav_im = mm.sum((-2,-1))    +SKIP
        or a blank image:
        >>> nav_im = np.zeros(mm.shape[:2]) +SKIP
        >>> b = DataBrowser(mm, nav_im=nav_im)  +SKIP
        
        Notes
        -----
        Based on https://gitlab.com/fpdpy/fpd/issues/16#note_72345827
        
        '''
        
        self._memmap_check()
        
        header_pixels = self._Mbhp.header_bytesize // (self._Mbhp.bitdepth_bin // 8)
        image_pixels = self._detY * self._detX + header_pixels
        offset = self._ds_start_skip * (self._Mbhp.header_bytesize + self._im_bytesize)
        
        shape = list(self.shape)
        shape[1] = shape[1] + self._row_end_skip
        shape = shape[:-2] + [image_pixels]
        shape = tuple(shape)
        
        mm = np.memmap(self._binfns[0], dtype=self._det_dtype, mode='r',
                       offset=offset, shape=shape)
        
        end_ind = -self._row_end_skip
        if end_ind == 0:
            end_ind = None
        mm = mm[:, :end_ind, ..., header_pixels:]
        # invert so origin is at top
        mm = mm.reshape(self.shape)[..., ::-1, :]
        return mm
    
    
    def __getitem__(self, key):
        # make into list (default is int or slice object or tuples thereof)
        if type(key) is not tuple:
            key = list([key])
        else:
            key = list(key)
        
        # only ints, slices, or ellipsis
        key_types = [type(k) for k in key]
        for kt in key_types:
            if kt not in [slice, int, type(Ellipsis)]:
                # only integers, slices (`:`), ellipsis (`...`), numpy.newaxis (`None`) and integer or boolean arrays are valid indices
                raise IndexError("only integers, slices (`:`), and ellipsis (`...`) are valid indices")
        
        # at most one ellipsis
        n_ellipsis = sum([kt == type(Ellipsis) for kt in key_types])
        if n_ellipsis > 1:
            raise IndexError("an index can only have a single ellipsis ('...')")
        
        # check slice axes length
        if len(key)-n_ellipsis > self.ndim:
            raise IndexError("too many indices for array")
        
        # handle ellipsis
        if n_ellipsis:
            kti = key_types.index(type(Ellipsis))
            if len(key) == self.ndim +1:
                # remove if not needed
                del key_types[kti]
                del key[kti]
            else:
                # replace ellipsis
                del key[kti]
                new_axis = slice(None, None, None)
                naxes_to_add = self.ndim - len(key)
                for i in range(naxes_to_add):
                    key.insert(kti, new_axis)
        
        # TODO
        # negative indices
        
        # homogenise keys to be all complete slices
        for i, k in enumerate(key):
            # convert ints to slices
            if type(k) is int:
                k = slice(k, k+1, None)
                key[i] = k
            
            # replace None in slices with ints
            sss = k.start, k.stop, k.step
            start, stop, step = sss
            if start is None:
                start = 0
            if stop is None:
                stop = self.shape[i]
            if step is None:
                step = 1
            if start > stop:
                raise IndexError("start index must be greater than stop index")
            stop = min(stop, self.shape[i])
            sss = start, stop, step
            if min(sss) < 0:
                # only positive values
                raise IndexError("indices must be positive")
            k = slice(*sss)
            key[i] = k
        
        # add missing slices
        missing_ndims = self.ndim - len(key)
        if missing_ndims > 0:
            for i in range(len(key), len(key)+missing_ndims):
                key.append(slice(0, self.shape[i], 1))
        
        # determine indices and shape
        if _p3:
            index_axes = [range(k.start, k.stop, k.step) for k in key]
        else:
            index_axes = [xrange(k.start, k.stop, k.step) for k in key]
        index_shape = tuple([len(i) for i in index_axes])
        
        # determine if detector images are indexed or full
        full_detector_images = all([i1 == i2 for i1, i2 in zip(index_shape[-2:], self.shape[-2:])])
        
        # make dataset array
        fpd_dataset = np.empty(shape=index_shape, dtype=self.dtype)
        
        # generate flat on disk indices
        from itertools import product, starmap
        from functools import partial
        rmip = partial(np.ravel_multi_index, dims=self.shape[:-2])
        def rmip_args(*args):
            r, c = args[:2]
            # ignoring extra pixels
            disk_dataset_flat_index = rmip(args)
            # including extra pixels
            disk_dataset_flat_index += self._ds_start_skip + r * self._row_end_skip
            return disk_dataset_flat_index
        flat_indices_iterator = starmap(rmip_args, product(*index_axes[:-2]))
        # this should be in on disk order
        
        # reshape output data to n, detY, detX
        fpd_dataset.shape = (np.prod(index_shape[:-2]),) + index_shape[-2:]
        
        # loop over data
        ### Process binary file(s), parsing header each time
        if _p3:
            sel_ind = flat_indices_iterator.__next__()
        else:
            sel_ind = flat_indices_iterator.next()
        i = 0   # index in scan, including row ends
        k = 0   # index of saved data
        stop = False
        pbar = tqdm(total=np.prod(index_shape[:-2]), mininterval=0, leave=True, unit='images')
        if _p3:
            im_indices = np.ogrid[index_axes[-2:]]
        else:
            im_indices = np.meshgrid(*index_axes[-2:], indexing='ij')
        for binfn_index, binfn in enumerate(self._binfns):
            if stop == True:
                # needed for multiple single images and breaking loop over iterator
                break
            # loop over input files
            with open(binfn, "rb") as f:
                fp = f        # file reference
                
                # create partial for looping
                read_binary_func = partial(_read_header_and_data, fp, self._Mhfp.fmt_ver, self._im_bytesize)
                bin_file_iter = iter(read_binary_func, '')
                for (hdr_str, hdr_params, data_buffer) in bin_file_iter:
                    # process bin_data                       
                    if i == sel_ind:
                        im_array = _raw_merlin_to_array(data_buffer,
                                self._det_dtype, 
                                self._Mbhp.bitdepth_data,
                                self._Mbhp.bitdepth_bin,
                                self._Mbhp.raw_mode,
                                self._detY,
                                self._detX)
                        
                        # fill array
                        if full_detector_images:
                            fpd_dataset[k] = im_array
                        else:
                            fpd_dataset[k] = im_array[im_indices]
                        k += 1
                        pbar.update(1)
                        try:
                            if _p3:
                                sel_ind = flat_indices_iterator.__next__()
                            else:
                                sel_ind = flat_indices_iterator.next()
                        except StopIteration:
                            stop = True
                            break
                    i += 1        
        pbar.close()

        # reshape output data
        fpd_dataset.shape = index_shape
        return np.squeeze(fpd_dataset)
        
        
    def to_array(self, count_extra=True, read_max=None):
        '''
        Convert the dataset into an in-memory numpy array.
        
        Parameters
        ----------
        count_extra : bool
            If True, extra images in input data are counted and reported.
        read_max : int or None
            If not None, only `read_max` images non-skip will be read.
            If not None, `count_extra` is disabled.
        
        Returns
        -------
        fpd_dataset : ndarray
            Dataset image array.
        '''
        if read_max is not None:
            count_extra = False
        
        fpd_dataset = np.empty(self._dim_lens, dtype=self._det_dtype)
        
        # scanXbindata is dimension in bin file >= scanX due to row_end_skip
        scanXbindata = self._scanX + self._row_end_skip
        
        # (scanY, scanXbindata[, colourN])
        ims_inc_extra_shape = self._ims_shape[:]
        ims_inc_extra_shape[1] = scanXbindata
        ims_inc_extra_shape = tuple(ims_inc_extra_shape)
        total_no_ims_inc_extra = np.prod(ims_inc_extra_shape)
        
        
        ### Process binary file(s), parsing header each time
        i = 0   # index in scan, including row ends
        j = 0   # index of read data
        k = 0   # index of saved data
        stop = False
        pbar = tqdm(total=self._total_no_ims, mininterval=0, leave=True, unit='images')
        for binfn_index, binfn in enumerate(self._binfns):
            if stop == True:
                # needed for multiple single images and breaking loop over iterator
                break
            # loop over input files
            with open(binfn, "rb") as f:
                fp = f        # file reference
                
                # create partial for looping
                read_binary_func = partial(_read_header_and_data, fp, self._Mhfp.fmt_ver, self._im_bytesize)
                bin_file_iter = iter(read_binary_func, '')
                for (hdr_str, hdr_params, data_buffer) in bin_file_iter:
                    if j < self._ds_start_skip:
                        pass
                    else:
                        try:
                            sYi_sXi_opCi = np.unravel_index(i, ims_inc_extra_shape, 'C')
                            scanYind, scanXind = sYi_sXi_opCi[:2]
                            s = np.s_[sYi_sXi_opCi]
                            if self._row_end_skip and scanXind > self._scanX-1:
                                i += 1
                                # skip row_end_skip
                                pass
                            else:
                                # process bin_data
                                bitdepth_data = self._Mbhp.bitdepth_data
                                bitdepth_bin = self._Mbhp.bitdepth_bin
                                raw_mode = self._Mbhp.raw_mode
                                
                                im_array = _raw_merlin_to_array(data_buffer, self._det_dtype, 
                                                                bitdepth_data, bitdepth_bin,
                                                                raw_mode, self._detY, self._detX)
                                fpd_dataset[s + (np.s_[:],)*2] = im_array
                                i += 1
                                k += 1
                                pbar.update(1)
                                if k == read_max:
                                    m = "Read %d images. Set 'read_max=None' to read all images."  %(read_max)
                                    _logger.info(m)
                                    stop == True
                                    break
                        except ValueError as e:
                            # detect unravel index error for more images than data
                            e1 = str(e)=='invalid entry in index array' # older numpy
                            e2 = 'is out of bounds' in str(e) # newer numpy
                            if e1 or e2:
                                if count_extra:
                                    if len(self._binfns)==1:
                                        # single file
                                        # Remaining data after processing last row,
                                        # including row_end_skip.
                                        no_extra_images = sum(1 for _ in bin_file_iter)
                                    else:
                                        # multiple files
                                        no_extra_images = len(self._binfns) - (binfn_index+1)
                                    m = '%d images at end of file(s) not processed!' %(no_extra_images)
                                    _logger.warning(m)
                                else:
                                    m = 'Extra images at end of file(s) not processed!'
                                    _logger.warning(m)
                                    m = "Use 'count_extra=True' to count extra images."
                                    _logger.info(m)
                                stop = True
                                break
                            else:
                                raise
                    j+=1
        if k+1 < self._total_no_ims and read_max is None:
            m = 'Only %d of expected %d images read!' %(k+1, self._total_no_ims)
            _logger.warning(m)
        pbar.close()
        
        return fpd_dataset







def slice_indices(data_shape, data_chunks, iterator=False):
    '''
    Generates indices that may be passed to a slice to chunk an array.
    
    Parameters
    ----------
    data_shape : tuple
        Data shape.
    data_chunks : tuple
        Data chunks in each axis.
    iterator : bool
        If True, an iterator is returned. If False, a list is returned.
    
    Returns
    -------
    Tuple of sinds, n.
    sinds : iterator or list
        Start and end indices of chunks.
    n : integer
        total number of chunks.
    
    Examples
    --------
    >>> import numpy as np
    >>> from tqdm import tqdm
    
    >>> data_chunks =  (17, 32, 64)
    >>> data_shape = (128, 128, 256)
    
    >>> sinds, n = slice_indices(data_shape, data_chunks)
    
    >>> for si in tqdm(sinds, total=n, unit='chunks'):
    ...     s = tuple([slice(x[0],x[1]) for x in si])
    ...     # ndarray[s]

    
    '''

    inds = [np.arange(0, np.ceil(float(shp)/cks).astype(int)+1, dtype=int)*cks for cks, shp in zip(data_chunks, data_shape)]
    # for int x 2 (start, stop) for each axis
    sss = [np.array([x[:-1], x[1:]]).T for x in inds]
    # clip to max size
    sss = [d.clip(max=lim) for d, lim in zip(sss, data_shape)]
    # convert to list
    sss = [x.tolist() for x in sss]
    # calculate total chuncks
    n = np.product([len(i) for i in sss])
    # generate iterator
    sinds = product(*sss)
    
    if not iterator:
        # convert to list
        sinds = list(sinds)
    
    return sinds, n



def _get_hdf5_file_from_obj(fpg):
    '''
    Gets hdf5 file from any one of filename, file, group or dataset.
    
    Parameters
    ----------
    fpg : str, file, group or dataset
        Filename, or hdf5 file, group or dataset.
    
    Returns
    -------
    closef : bool
        True if file should be closed to return to original state.
    
    h5f : hdf5 file
    
    '''
    
    closef = False
    h5fnp_type = type(fpg)
    
    if h5fnp_type in _str_type_list:
        h5f = h5py.File(fpg, 'r')
        closef = True
    elif h5fnp_type == h5py._hl.files.File:
        h5f = fpg
    elif h5fnp_type == h5py._hl.group.Group:        
        h5f = fpg.file
    elif h5fnp_type == h5py._hl.dataset.Dataset:
        h5f = fpg.file
    else:
        raise Exception('Unknown type:', h5fnp_type)
    
    return closef, h5f



def _check_fpd_file(fpg, min_version=None, max_version=None):
    '''
    Check if hdf5 file is a recognised FPD format.
    
    Parameters
    ----------
    fpg : str, file, group or dataset
        Filename, or hdf5 file, group or dataset.
    min_version : str
        Minimum FPD version.
    max_version : str
        Maximum FPD version.
    
    Returns
    -------
    tuple of boolean and format version string.
    
    '''
    
    closef, h5f = _get_hdf5_file_from_obj(fpg)
    
    if min_version is None:
        min_version = _min_version
    if max_version is None:
        max_version = __version__
        
    try:
        vs = h5f.attrs['fpd_version']
        if  LooseVersion(min_version) > LooseVersion(vs) > LooseVersion(max_version):
            # version understood
            print("FPD version '%s' in file '%s' is not supported" %(vs, h5f.file.filename))
            bs = (False, vs)
        else:
            bs = (True, vs)
    except KeyError:
        print("'%s' is not a recognised FPD file." %(h5f.file.filename))
        bs = (False, '')
        
    if closef:
        h5f.close()   
    return bs



def find_hdf5_objname_by_attribute(fpg, attr_name, attr_val=None, fpd_check=True):
    '''
    Returns a list of object names in hdf5 object with specified 
    attribute name and, optionally, attribute value.
    
    Parameters
    ----------
    fpg : str, file, group or dataset
        Filename, or hdf5 file, group or dataset.
    attr_name : str
        Attribute name.
    attr_val : str or None
        Atribute value to match. If not None, returned objects have 
        attr_name with attr_val. If None, all attributes matching 
        attr_name are returned.
    fpd_check : bool
        If True, the file format version is checked.
    
    '''
    
    if fpd_check:
        b, vs = _check_fpd_file(fpg)
        if not b:
            raise Exception('Not a valid FPD file. Version:', vs)
    
    closef = False
    h5fnp_type = type(fpg)
    if h5fnp_type in _str_type_list:
        h5f = h5py.File(fpg, 'r')
        closef = True
    elif h5fnp_type == h5py._hl.files.File:
        h5f = fpg
    elif h5fnp_type == h5py._hl.group.Group:
        h5f = fpg
    elif h5fnp_type == h5py._hl.dataset.Dataset:
        h5f = fpg
    else:
        raise Exception('Unknown type:', h5fnp_type)
        
    obj_names = []
    def _append_if_attr(name):
        if attr_name in h5f[name].attrs and (not attr_val or h5f[name].attrs[attr_name]==attr_val):
            obj_names.append(name)
    h5f.visit(_append_if_attr)
    
    if closef:
        h5f.close()
    return obj_names



def hdf5_dm_tags_to_dict(fpg, fpd_check=True):
    '''
    Return hdf5 dm tag groups as list of dictionaries (one per file),
    along with lists of group paths and original dm filenames.
    
    Parameters
    ----------
    fpg : str, file, group or dataset
        Filename, or hdf5 file, group or dataset.
    fpd_check : bool
        If True, the file format version is checked.
    
    Returns
    -------
    tagds : list of dicts
        Unflattened tag dictionary.
    dm_group_paths : list of str
        Object names.
    dm_filenames : list of str
        Original filenames.
        
    '''
    
    if fpd_check:
        b, vs = _check_fpd_file(fpg)
        if not b:
            raise Exception('Not a valid FPD file. Version:', vs)
    
    closef, h5f = _get_hdf5_file_from_obj(fpg)
    
    dm_group_paths = find_hdf5_objname_by_attribute(h5f, 'dm_group_type', 1, False)
    n_dm_files = len(dm_group_paths)
    print('Found %d DM file(s).' %(n_dm_files))
    
    tagds = []
    dm_filenames = []
    for dm_grp in dm_group_paths:
        dmfn_hdf5 = h5f[dm_grp].attrs['dm_filename']
        
        tag_grp = h5f[dm_grp+'/tags']
        tag_grp_flat = _flatten(tag_grp,'','/')
        tag_grp_flat_d = dict([(k,v.value) for k,v in tag_grp_flat.items()])
        tagd = _unflatten(tag_grp_flat_d, '/')
        
        tagds.append(tagd)
        dm_filenames.append(dmfn_hdf5)

    if closef:
        h5f.close()
    return tagds, dm_group_paths, dm_filenames



def hdf5_dm_to_bin(fpg, dmfns=None, fpd_check=True, ow=False):
    '''
    Write DM binary from hdf5 file with output filename given by dmfns.
    
    Parameters
    ----------
    fpg : str, file, group or dataset
        Filename, or hdf5 file, group or dataset.
    dmfns : None, list of str and None
        DM output filename(s). If None, the original filenames at time
        of hdf5 creation are used. If a list, non-None entries will be
        used as new filenames. New filenames are parsed to ensure the 
        correct extension is used.
    fpd_check : bool
        If True, the file format version is checked.

    '''
    
    if fpd_check:
        b, vs = _check_fpd_file(fpg)
        if not b:
            raise Exception('Not a valid FPD file. Version:', vs)
    
    closef, h5f = _get_hdf5_file_from_obj(fpg)
    
    dm_group_paths = find_hdf5_objname_by_attribute(h5f, 'dm_group_type', 1, False)
    n_dm_files = len(dm_group_paths)
    print('Found %d DM file(s).' %(n_dm_files))
    
    # prepare zipped list of tuples
    if dmfns is None:
        fn_gn = zip((None,)*n_dm_files, dm_group_paths)
    else:
        #type(dmfns) in _str_type_list:
        fn_gn = zip(dmfns, dm_group_paths)
    
    for dmfn, dm_grp in fn_gn:
        dm_bin = h5f[dm_grp+'/bin'].value
        dmfn_hdf5 = h5f[dm_grp].attrs['dm_filename']
        if dmfn is None:
            dmfn = dmfn_hdf5
        else:
            # parse filename
            _, dmfn_hdf5_ext = os.path.splitext(dmfn_hdf5)
            dmfn_fn, dmfn_ext = os.path.splitext(dmfn)
            if dmfn_ext != dmfn_hdf5_ext:
                dmfn = dmfn_fn+dmfn_hdf5_ext
        
        if not ow and os.path.isfile(dmfn):
            reply = _input_fn("File '%s' already exists. Overwrite? ([y]/n): " %(os.path.abspath(dmfn)) )
            if reply.strip().lower() in ['y', 'yes', '']:
                pass
            else:
                print('Doing nothing.')
                continue
        print("Extracting DM file in '%s', called '%s', as '%s'." %(dm_grp, dmfn_hdf5, dmfn))
        with open(dmfn, 'wb') as f:
            dm_bin.tofile(f, sep="") 
    if closef:
        h5f.close()



def hdf5_fpd_to_bin(fpg, fpd_fn=None, fpd_check=True, ow=False):
    '''
    Write FPD binary from hdf5 file with output filename given by fpdfn.
    Header information is omitted.
    
    Parameters
    ----------
    fpg : str, file, group or dataset
        Filename, or hdf5 file, group or dataset.
    fpd_fn : str
        FPD output filename. If None, the input filename is used with 
        a '.bin' extension.
    fpd_check : bool
        If True, the file format version is checked.
    
    Notes
    -----
    Alternatively hdf5 tools can be used:
        h5dump -d /fpd_expt/fpd_data/data -b BE -o h5dump.bin ./fpd_test_data/bin_257.hdf5
    
    '''
    
    if fpd_check:
        b, vs = _check_fpd_file(fpg)
        if not b:
            raise Exception('Not a valid FPD file. Version:', vs)
    
    closef, h5f = _get_hdf5_file_from_obj(fpg)
   
    data = h5f['fpd_expt/fpd_data/data'].value
    
    if fpd_fn is None:
        fpd_fn = os.path.splitext(h5f.filename)[0]+'.bin'
    if not ow and os.path.isfile(fpd_fn):
        reply = _input_fn("File '%s' already exists. Overwrite? ([y]/n): " %(os.path.abspath(fpd_fn)) )
        if reply.strip().lower() in ['y', 'yes', '']:
            pass
        else:
            print('Doing nothing.')
            return
    print("Writing FPD data from '%s' to binary file '%s'." %(h5f.filename, fpd_fn))
    with open(fpd_fn, 'wb') as f:
        data.tofile(f, sep="")
    
    if closef:
        h5f.close()



def hdf5_src_to_file(fpg, src_fn=None, fpd_check=True, ow=False):
    '''
    Extract code used to generate FPD hdf5 file and write to file.
    
    Parameters
    ----------
    fpg : str, file, group or dataset
        Filename, or hdf5 file, group or dataset.
    src_fn : str or None
        Source output filename. If None, the original filename is used.
    fpd_check : bool
        If True, the file format version is checked.
    
    Notes
    -----
    Alternative:
        h5dump -a /fpd_expt/src -b LE -o out2.py ./fpd_test_data/bin_257.hdf5
    
    '''
    
    if fpd_check:
        b, vs = _check_fpd_file(fpg)
        if not b:
            raise Exception('Not a valid FPD file. Version:', vs)
    
    closef, h5f = _get_hdf5_file_from_obj(fpg)

    src = h5f['fpd_expt/src'].value  #attrs['src']
    src_path = h5f['fpd_expt/src'].attrs['src_path']
    if src_fn is None:
        src_fn = os.path.split(src_path)[-1]
    if not ow and os.path.isfile(src_fn):
        reply = _input_fn("File '%s' already exists. Overwrite? ([y]/n): " %(os.path.abspath(src_fn)) )
        if reply.strip().lower() in ['y', 'yes', '']:
            pass
        else:
            print('Doing nothing.')
            return
    print("Writing FPD source originally from '%s' to file '%s'." %(src_path, os.path.abspath(src_fn)))
    with open(src_fn, 'w') as f:
        f.write(src)
    
    if closef:
        h5f.close()



def fpd_to_hysperspy(fpg, fpd_check=True, assume_yes=False, group_names=None):
    '''
    Open an fpd dataset in hyperspy.
    
    Parameters
    ----------
    fpg : str, file, group or dataset
        Filename, or hdf5 file, group or dataset.
    assume_yes : bool
        If True, open files without asking, even if they consume large
        amounts of memory.
    group_names : None, string, or list.
        Group names to filter the return by. If None, the default set is
        returned (see notes). If not None, only groups matching group_names
        are returned.

    Returns
    -------
    A named tuple of hyperspy objects. See notes.
    
    Notes
    -----
    In hyperspy versions with lazy signal support, the returned object is a
    namedtuple of all filtered emd groups. The field_names are generated from the 
    emd group names in the fpd file. This enables tab completion. If group_names is None, all groups are returned.
    
    In non-lazy versions of hyperspy, the named tuple only includes fpd_data
    and dif and scan images by default (group_names=None).  
    
    Colours are not handled yet.
    
    Examples
    --------
    import fpd.fpd_file as fpdf
    fpd_signals = fpdf.fpd_to_hysperspy(filename)
    im = fpd_signals.fpd_data
    
    fpd_signals = fpdf.fpd_to_hysperspy(filename, 
        group_names=['fpd_data', 'fpd_sum_im', 'fpd_sum_dif'])
    
    '''
    from hyperspy import __version__ as hsv
    
    
    def _check_titles(titles, group_names, hs_non_lazy):
        # helper for parsing group_names against titles
        print('Detected emd groups:', titles)
        # select groups
        if group_names is None:
            if hs_non_lazy:
                group_names = ['fpd_data', 'fpd_sum_im', 'fpd_sum_dif']
            else:
                group_names = titles
        elif type(group_names) in _str_type_list:
            group_names = [group_names]
        non_extant_groups = [t for t in group_names if t not in titles]
        if len(non_extant_groups):
            print('The following requested groups do not exists:', non_extant_groups)
        # get indices
        indices = [titles.index(t) for t in group_names if t in titles]
        return indices
    
    
    hs_non_lazy = False
    if LooseVersion(hsv) < LooseVersion('1.0.0'):
        hs_non_lazy = True
    
    if fpd_check:
        b, vs = _check_fpd_file(fpg)
        if not b:
            raise Exception('Not a valid FPD file. Version:', vs)
    
    if hs_non_lazy:
        # older hyperspy
        from hyperspy.signals import Image
        
        if not assume_yes:
            # check user wants to read data into memory
            reply = _input_fn("This may consume a large amount of memory. Continue? ([y]/n): ")
            if reply.strip().lower() in ['y', 'yes', '']:
                pass
            else:
                print('Aborting.')
                return None
        
        closef, h5f = _get_hdf5_file_from_obj(fpg)
        fpd_group = h5f['fpd_expt']
        titles = find_hdf5_objname_by_attribute(fpd_group,
                                        attr_name='emd_group_type',
                                        attr_val=1)
        indices = _check_titles(titles, group_names, hs_non_lazy)
        titles_selection = [titles[i] for i in indices]
        
        ss = []
        for tsi in titles_selection:
            emd_dg = fpd_group[tsi]
            ds = emd_dg['data']
            data = ds.value
            s = Image(data[:])
            num_axes = len(ds.shape)
            for i in range(num_axes):
                h5_ax = emd_dg['dim%d' %(i+1)]
                # horrible hack to accommodate hyperspy's non-c ordering
                if i==0:
                    i = 1
                elif i==1:
                    i = 0
                if num_axes >= 4:
                    if i==num_axes-2:
                        i = num_axes-1
                    elif i==num_axes-1:
                        i = num_axes-2
                hs_ax = s.axes_manager[i]
                
                hs_ax.axis = h5_ax.value
                hs_ax.scale = np.diff(hs_ax.axis)[0]
                hs_ax.name = h5_ax.attrs['name']
                hs_ax.units = h5_ax.attrs['units']
            ss.append(s)
        fpd_signals = namedtuple('fpd_signals', titles_selection)
        s = fpd_signals(*ss)
        
        if closef:
            h5f.close()
        return s
    else:
        # lazy loading in newer hyperspy
        closef, h5f = _get_hdf5_file_from_obj(fpg)
        h5f_fn = h5f.filename
        if closef:
            h5f.close()

        from hyperspy.io_plugins import emd
        from hyperspy.io import dict2signal

        ds = emd.file_reader(h5f_fn, lazy=True)
        titles = [d['original_metadata']['General']['title'].split('/')[-1] for d in ds]      
        indices = _check_titles(titles, group_names, hs_non_lazy)
        titles_selection = [titles[i] for i in indices]
        ds_selecion = [ds[i] for i in indices]
        
        ss = []
        for d_select in ds_selecion:
            d_select['attributes']['_lazy'] = True
            t = [axis for axis in d_select['axes'] if 'scan' in axis['name']]
            for axis in t:
                axis['navigate'] = True
            s = dict2signal(d_select)
            ss.append(s)
        fpd_signals = namedtuple('fpd_signals', titles_selection)
        s = fpd_signals(*ss)
        return s



class DataBrowser:
    def __init__(self, fpgn, nav_im=None, cmap=None, colour_index=None,
                 nav_im_dict=None, fpd_check=True):
        '''
        Navigate fpd data set.
        
        Parameters
        ----------
        fpgn : hdf5 str, file, group, dataset, ndarray, or dask array.
             hdf5 filename, file, group or dataset, or numpy array, 
             `MerlinBinary` object, or dask array.
        nav_im : 2-D array or None
            Navigation image. If None, this is taken as the sum image.
            For numpy arrays, it is calculated directly.
        cmap : str or None
            Matplotlib colourmap name used for diffraction image.
            If None, `viridis` is used if available, else `gray`.
        colour_index : int or None
            Colour index used for plotting. If None, the first index is
            used.
        nav_im_dict : None or dictionary
            Keyword arguments passed to the navigation imshow call.
        fpd_check : bool
            If True, the file format version is checked.

        TODO
        ----
        log / linear norms
        nav_im list input and switch between images?
        display with axis units rather than pixels?
            
        '''
        
        import fpd
        numpy_array = isinstance(fpgn, np.ndarray) or isinstance(fpgn, fpd.fpd_file.MerlinBinary)
        dask_array = "dask.array.core.Array" in str(type(fpgn))
        if not numpy_array and not dask_array:
            if fpd_check:
                b, vs = _check_fpd_file(fpgn)
                if not b:
                    raise Exception('Not a valid FPD file. Version:', vs)

            try:
                # try to use FPD hdf5 format
                self.closef, self.h5f = _get_hdf5_file_from_obj(fpgn)
                self.h5f_ds = self.h5f['fpd_expt/fpd_data/data']
            except:
                self.closef = False
                self.h5f_ds = fpgn
        elif numpy_array:
            # numpy array
            self.closef = False
            self.h5f_ds = fpgn
        elif dask_array:
            self.closef = False
            self.h5f_ds = fpgn
        
        self.nav_im_dict = nav_im_dict
        
        # get data shape info
        self.scanY, self.scanX = self.h5f_ds.shape[:2]
        self.detY,self.detX = self.h5f_ds.shape[-2:]
            
        # determine colour info
        ds_shape_len = len(self.h5f_ds.shape)
        if ds_shape_len == 4:
            # no colour data
            self.ncolours = 0
        elif ds_shape_len == 5:
            self.ncolours = self.h5f_ds.shape[2]
        
        self.colour_index = None
        if colour_index is None and self.ncolours:
            self.colour_index = 0
        
        # navigation image
        if nav_im is None and not numpy_array:
            if self.colour_index is not None:
                self.nav_im = self.h5f['fpd_expt/fpd_sum_im/data'].value[..., self.colour_index]
            else:
                self.nav_im = self.h5f['fpd_expt/fpd_sum_im/data'].value[...]
        else:
            self.nav_im = nav_im
        if self.nav_im is None:
            # numpy array
            if self.ncolours == 0:
                self.nav_im = self.h5f_ds.sum((-2, -1))
            else:
                self.nav_im = self.h5f_ds[:, :, self.colour_index].sum((-2, -1))
        
        self.scanYind = 0
        self.scanXind = 0
        self.scanYind_old = self.scanYind
        self.scanXind_old = self.scanXind
        if self.colour_index is not None:
            self.plot_data = self.h5f_ds[self.scanYind, self.scanXind, self.colour_index, :, :]
        else:
            self.plot_data = self.h5f_ds[self.scanYind, self.scanXind, :, :]
        self.plot_data = np.ascontiguousarray(self.plot_data)
        
        self.rwh = max(self.scanY, self.scanX)//64
        if self.rwh == 0:
            self.rwh = 2
        self.rect = None
        self.press = None
        self.background = None
        self.plot_nav_im()
        
        # cmap
        if cmap is None:
            try:
                self.cmap = mpl.cm.get_cmap('viridis')
            except ValueError:
                self.cmap = mpl.cm.get_cmap('gray')
        else:
            self.cmap = mpl.cm.get_cmap(cmap)
        self.cmap.set_bad(self.cmap(0))
        
        self.plot_dif()
        self.connect()
        
    def plot_nav_im(self):
        kwd = dict(adjustable='box-forced', aspect='equal')
        if _mpl_non_adjust:
            _ = kwd.pop('adjustable')
        
        self.f_nav, ax = plt.subplots(subplot_kw=kwd)
        self.f_nav.canvas.set_window_title('nav')
        
        d = {'cmap':'gray'}
        if self.nav_im_dict is not None:
            d.update(self.nav_im_dict)
        im = ax.imshow(self.nav_im, interpolation='nearest', **d)
        if self.nav_im.ndim != 3:
            plt.colorbar(mappable=im)
        
        rect_c = 'r'
        if self.nav_im.ndim==3 or (self.nav_im.ndim == 2 and im.cmap.name != 'gray'):
            # rgb
            rect_c = 'w'    #'k'
        self.rect = mpl.patches.Rectangle((self.scanYind-self.rwh/2, 
                                           self.scanXind-self.rwh/2), 
                                           self.rwh, self.rwh, ec=rect_c,
                                           fc='none', lw=2, picker=4)
        ax.add_patch(self.rect)        
        plt.tight_layout()
        plt.draw()
        
    def plot_dif(self):
        kwd = dict(adjustable='box-forced', aspect='equal')
        if _mpl_non_adjust:
            _ = kwd.pop('adjustable')
        
        self.f_dif, ax = plt.subplots(subplot_kw=kwd)
        self.f_dif.canvas.set_window_title('dif')
        
        if self.plot_data.max()<1:
            norm = None
        else:
            norm = mpl.colors.LogNorm()
        self.im = ax.matshow(self.plot_data, 
                             interpolation='nearest',
                             cmap=self.cmap,
                             norm=norm )
        plt.sca(ax)
        self.cbar = plt.colorbar(self.im)
        ax.format_coord = self.format_coord
        self.update_dif_plot()
      
        plt.tight_layout()
        plt.draw()

    def connect(self):
        'connect to all the events we need'
        self.cidpress = self.rect.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.rect.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.rect.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        
        self.cid_f_nav = self.f_nav.canvas.mpl_connect('close_event', self.handle_close)
        self.cid_f_dif = self.f_dif.canvas.mpl_connect('close_event', self.handle_close)

    def handle_close(self, e):
        if self.closef==True:
            self.h5f.file.close()
        self.disconnect()
        # close other fig
        if e.canvas.get_window_title()=='nav':
            plt.close(self.f_dif)
        else:
            plt.close(self.f_nav)
            
    def on_press(self, event):
        if event.inaxes != self.rect.axes: return

        contains, attrd = self.rect.contains(event)
        if contains:
            #print('event contains', self.rect.xy)
            x0, y0 = self.rect.xy   # xy is lower left
            
            # draw everything but the selected rectangle and store the pixel buffer
            canvas = self.rect.figure.canvas
            axes = self.rect.axes
            self.rect.set_animated(True)
            canvas.draw()
            self.background = canvas.copy_from_bbox(self.rect.axes.bbox)

            axes.draw_artist(self.rect)     # now redraw just the rectangle
            canvas.blit(axes.bbox)          # and blit just the redrawn area
        else:
            # in axis but not rectangle
            #print event.xdata, event.ydata
            x0, y0 = (None,)*2
            
        self.press = x0, y0, event.xdata, event.ydata
        self.yind_temp = self.scanYind
        self.xind_temp = self.scanXind

    def on_motion(self, event):
        if self.press is None: return
        if event.inaxes != self.rect.axes: return
        if self.background is None: return
        
        x0, y0, xpress, ypress = self.press
        dx = int(event.xdata - xpress)
        dy = int(event.ydata - ypress)
        if abs(dy)>0 or abs(dx)>0:
            #print('x0=%f, xpress=%f, event.xdata=%f, dx=%f, x0+dx=%f'%(x0, xpress, event.xdata, dx, x0+dx))
            self.rect.set_x(x0+dx)
            self.rect.set_y(y0+dy)
            self.scanYind = self.yind_temp+dy
            self.scanXind = self.xind_temp+dx
            #print(dy, dx)
            
            canvas = self.rect.figure.canvas
            axes = self.rect.axes
            canvas.restore_region(self.background)  # restore the background region
            axes.draw_artist(self.rect)             # redraw just the current rectangle
            canvas.blit(axes.bbox)                  # blit just the redrawn area
        
            #self.rect.figure.canvas.draw()
            self.update_dif_plot()                  
    
    def on_release(self, event):
        if event.inaxes != self.rect.axes: return
        
        x, y = self.press[2:]
        if np.round(event.xdata-x)==0 and np.round(event.ydata-y)==0:
            # mouse didn't move
            x, y = np.round(x), np.round(y)
            self.rect.set_x(x-self.rwh/2)
            self.rect.set_y(y-self.rwh/2)
            self.scanYind = int(y)
            self.scanXind = int(x)
                    
            #self.rect.figure.canvas.draw()
            self.update_dif_plot()
        elif self.background is not None:
            canvas = self.rect.figure.canvas
            axes = self.rect.axes
            canvas.restore_region(self.background)  # restore the background region
            axes.draw_artist(self.rect)             # redraw just the current rectangle
            canvas.blit(axes.bbox)                  # blit just the redrawn area
            
        'on release we reset the press data'
        self.press = None
        self.yind_temp = None
        self.yind_temp = None
        
        # turn off the rect animation property and reset the background
        self.rect.set_animated(False)
        self.background = None

        # redraw the full figure
        self.rect.figure.canvas.draw()
        
    def format_coord(self, x, y):
        col = np.ceil(x-0.5).astype(int)
        row = np.ceil(y-0.5).astype(int)
        if col>=0 and col<self.detX and row>=0 and row<self.detY:
            z = self.plot_data[row, col]
            return 'x=%d, y=%d, z=%d'%(x, y, z)
        else:
            return 'x=%d, y=%d'%(x, y)
    
    def update_dif_plot(self):
        if self.colour_index is not None:
            self.plot_data = self.h5f_ds[self.scanYind, self.scanXind, self.colour_index, :, :]
        else:
            self.plot_data = self.h5f_ds[self.scanYind, self.scanXind, :, :]
        self.plot_data = np.ascontiguousarray(self.plot_data)
        self.im.set_data(self.plot_data)
        self.im.autoscale()
        self.im.changed()
        self.im.axes.set_xlabel('scanX %s'%self.scanXind)
        self.im.axes.set_ylabel('scanY %s'%self.scanYind)
        self.im.axes.figure.canvas.draw()

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.rect.figure.canvas.mpl_disconnect(self.cidpress)
        self.rect.figure.canvas.mpl_disconnect(self.cidrelease)
        self.rect.figure.canvas.mpl_disconnect(self.cidmotion)
        
        self.f_nav.canvas.mpl_disconnect(self.cid_f_nav)
        self.f_dif.canvas.mpl_disconnect(self.cid_f_dif)


