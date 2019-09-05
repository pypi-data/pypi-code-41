import numpy as np
import os
import struct
import re
from tabulate import tabulate
from textwrap import indent

'''

Block format

Files
-----
.Tbk   Block level headers and offsets to each second of data collected in the .tsq file
.Tdx   Epoch indexing information for faster access or filtering when dealing with epoch data.
.tev   Actual data
.tsq   List of event headers for the tev file
.tin
.tnt


.sev

'''

class Block(object):
    def __init__(self, path):
        '''
        Read TDT block.
        
        Parameters
        ----------
        path : str
            Path to TDT block
        
        Returns
        -------
        block : TDT_block object
            Object for interfacing with a TDT block
        '''

        self._set_globals() #Set global variables

        self.path = path
        self.stream_info = {} 
        
        #Define dictionaries
        self.headerStruct = {
            'startTime' : None,
            'stopTime' : None,
            'stores' : {},
        }

        self._data = {}

        self.epocs = {
            'name'       : [],
            'buddies'    : [],
            'timestamps' : [],
            'code'       : [],
            'type'       : [],
            'typeStr'    : [],
            'data'       : [],
            'dtype'      : [],
        }
        
        #get file objects
        fnames = os.listdir(self.path)
        basePath = os.path.join(self.path, [fname for fname in fnames if '.tsq' in fname][0][:-4])
        
        self._tsq = open(basePath+'.tsq','rb')
        self._tev = open(basePath+'.tev','rb')
        self._tnt = open(basePath+'.tnt','rt') #read text
        
        self._Tbk = open(basePath+'.Tbk','rb')
        self._Tdx = open(basePath+'.Tdx','rb')
        self._tin = open(basePath+'.tin','rb')

        # Read in SEV names and info, if present
        self._read_sev_info()
        
        #Read notes
        self._read_tnt()

        #Look for sort IDs
        self._get_sortIDs()

        #Read block notes
        self._read_blockNotes()

        #Read headers
        self._read_headers()

        self._create_stream_info()

    def read_stores(self, stores=None, reload=False):
        '''
        Read specified stores. If no stores are specified, all stores are read

        Parameters
        ----------
        stores : str, list
            Name or names of stores to be read. If None, all stores are read.
        reload : bool, optional
            If true, forces reload of stores. Else, skips stores already loaded.
        '''
        # Get a list of stores to read
        if stores is None:
            stores = list(self.headerStruct['stores'].keys())

        # Determine which stores are already read
        if not reload:
            stores = [store for store in stores if store not in self.data.keys()]
            
        # Determine which stores are from SEV
        sev_stores = []
        tev_stores = []
        for store in stores:
            if store in self._sev_store_names:
                sev_stores.append(store)
            else:
                tev_stores.append(store)

        # Extract TEV and SEV stores
        self._read_sev(sev_stores)
        self._read_tev(tev_stores)
        
    @property
    def stores(self):
        return [*self.headerStruct['stores'].keys()]

    @property
    def data(self):
        '''
        Data dictionary containing read stores, where each key is the store name

        Each store itself is a dictionary, with the following keys:

        +-------+------------------------------------+
        + Key   + Value                              +
        +=======+====================================+
        + type  + type of store (stream, epoch, etc) +
        +-------+------------------------------------+
        + data  + data for the store                 +
        +-------+------------------------------------+
        + fs    + sampling rate (stream only)        +
        +-------+------------------------------------+
        + nChan + number of channels (stream only)   +
        +-------+------------------------------------+
        '''
        return self._data
    
    # Internal methods
    #---------------------------------------
    def _read_blockNotes(self):
        '''
        Reads blocknotes from .Tbk file into a list of dictionaries
        '''
        blockNotesList = []

        strbits = np.fromfile(self._Tbk, dtype='uint8')
        string = ''.join([chr(item) for item in strbits])
        string = string.split('[USERNOTEDELIMITER]')[2]
        
        lines = string.split('\n')
        lines = lines[:-1]
        
        storenum = -1
        for line in lines:
            #check if new store
            if 'StoreName' in line:
                storenum += 1
                blockNotesList.append({})

            if ';' in line:
                items = line.split(';')
                fieldstr = items[0].split('=')[1]
                value = items[2].split('=')[1]

            blockNotesList[storenum][fieldstr] = value
        
        # Convert blocknots from list to dict
        self.blockNotes = {store['StoreName']:store for store in blockNotesList}
        
    def _read_headers(self):
        '''
        Read header information from the tsq file
        '''
        header_dtype = np.dtype([
            ('size',         np.int32),
            ('type',         np.int32),
            ('code',         'S4'),
            ('channel',      np.uint16),
            ('sort code',    np.uint16),
            ('timestamp',    np.float64),
            ('event offset', np.uint64), #also Strobe, need to be able to convert to float64
            ('dtype',        np.int32),
            ('fs',           np.float32),
        ])

        # **NOTE**
        # All header codes get read in as byte strings (b'abcd') instead of regular strings ('abcd')
        # this may cause issues later, but i keep getting errors if I try to read the data as regular strings

        #Read all headers
        self._tsq.seek(0,0)
        headers = np.fromfile(self._tsq, dtype=header_dtype)
        
        #Process start/stop time
        if headers[1]['code'] != self._event_marks['STARTBLOCK']:
            print('Block start marker not found')
        if headers[-1]['code'] != self._event_marks['STOPBLOCK']:
            print('Block end marker not found')
        self.headerStruct['startTime'] = headers[1]['timestamp']
        self.headerStruct['stopTime'] = headers[1]['timestamp']

        #Process remaining headers
        headers = headers[2:-1] #remove first 2, last 1

        #Get unique codes, and determine their store types
        unique_codes = np.unique(headers['code'])
        unique_code_indxs = [np.where(headers['code'] == code)[0][0] for code in unique_codes]
        store_types = [self._code2type(headers[indx]['type']) for indx in unique_code_indxs] 

        #Add store information to store map
        for i in range(len(unique_codes)):
            header = headers[unique_code_indxs[i]]
            code = unique_codes[i].decode('utf-8') #DECODE BYTESTRING
            sType = store_types[i]
            
            #indx = unique_code_indxs[i]
            #code = unique_codes[i]

            if sType == 'epocs':
                #Need to read channel and sort code as a single string
                #There's a good chance I did this in the wrong order, but I have no way of testing it for now
                byte_str    = header['channel'].tobytes() + header['sort code'].tobytes()
                uint8_array = np.frombuffer(byte_str,dtype = 'uint8')
                buddies     = ''.join([chr(c) for c in uint8_array])
                #This is for maching epoc channels to eachother later
                
                self.epocs['name'].append(code)
                self.epocs['buddies'].append(buddies)
                #self.epocs['code'].append() Dont need because we are reading names directly
                self.epocs['timestamps'].append([])
                self.epocs['type'].append(self._epoc2type(header['type']))
                self.epocs['typeStr'].append(sType)
                #self.epocs['typeNum'].append() Also dont care about this
                self.epocs['data'].append([])
                self.epocs['dtype'].append(header['dtype'])
            else:
                self.headerStruct['stores'][code] = {
                    'name'    : code,
                    'size'    : header['size'],
                    'type'    : header['type'],
                    'typeStr' : sType,
                    'dtype'   : header['dtype']
                    }

                if store_types[i] != 'scalars':
                    self.headerStruct['stores'][code]['fs'] = header['fs']
                    
            #Get indexes of all headers associated with this store
            store_indxs = np.where(headers['code'].astype(str) == code)
    
            #=============================================
            # COMPILE NOTES HERE. SKIPPING FOR NOW     
            #=============================================
                    
            if sType == 'epocs':
                indx = self.epocs['name'].index(code)
                self.epocs['timestamps'][indx] = headers[store_indxs]['timestamp'] - self.headerStruct['startTime']
                #Need to convert offset to double
                self.epocs['data'][indx] = np.frombuffer(headers[store_indxs]['event offset'].tobytes(),dtype='float64')
                
            else:
                self.headerStruct['stores'][code]['timestamps'] = headers[store_indxs]['timestamp']
                self.headerStruct['stores'][code]['offsets']    = headers[store_indxs]['event offset']
                self.headerStruct['stores'][code]['channel']    = headers[store_indxs]['channel']

                if self.headerStruct['stores'][code]['typeStr'] == 'snips':
                    #NOT ALLOWING FOR CUSTOM SORT, SOMEONE ELSE CAN ADD SUPPORT FOR THIS
                    self.headerStruct['stores'][code]['sortcode'] = headers[store_indxs]['channel']
                    self.headerStruct['stores'][code]['sortname'] = 'TankSort'

            
        #Put epocs into headerStruct
        for i in range(len(self.epocs['name'])): #do non-buddies first
            if self.epocs['type'][i] == 'onset':
                name = self.epocs['name'][i]
                self.headerStruct['stores'][name] = {
                    'name'    : name,
                    'onset'   : self.epocs['timestamps'][i],
                    'offset'  : self.epocs['timestamps'][i][1:],
                    'type'    : self.epocs['type'][i],
                    'typeStr' : self.epocs['typeStr'][i],
                    #'typeNum' : 2
                    'data'    : self.epocs['data'][i],
                    'dtype'   : self.epocs['dtype'][i],
                    'size'    : 10
                }

        for i in range(len(self.epocs['name'])): #buddies second
            if self.epocs['type'][i] == 'offset':
                name = self.epocs['buddies'][i]
                self.headerStruct['stores'][name]['offset'] = self.epocs['timestamps'][i]

                #Fix time ranges
                if self.headerStruct['stores'][name]['offset'][0] < self.headerStruct['stores'][name]['onset'][0]:
                    self.headerStruct['stores'][name]['onset'] = np.hstack((0,self.headerStruct['stores'][name]['onset']))
                if self.headerStruct['stores'][name]['offset'][-1] < self.headerStruct['stores'][name]['onset'][-1]:
                    self.headerStruct['stores'][name]['offset'] = np.hstack((self.headerStruct['stores'][name]['offset'],np.inf))

    def _read_tnt(self):
        '''
        The tnt file appears to be a note file. Skipping for now
        '''
        pass

    def _read_sev_info(self):
        '''
        Get list of store names that are in SEV files
        '''
        
        '''
        Internal list of thigns to rename after porting:
        event_name -> store_name
        '''
        
        # INTERNAL FUNCTIONS
        #=====================================
        def read_sev_header(f_dict):
            with open(f_dict['path'], 'rb') as sev:
                stream_header = {}

                stream_header['size_bytes']   = np.fromfile(sev, dtype=np.uint64, count=1)[0]
                stream_header['file_type']    = np.fromfile(sev, dtype=np.uint8, count=3)
                stream_header['file_type']    = ''.join([chr(item) for item in stream_header['file_type']])
                stream_header['file_version'] = np.fromfile(sev, dtype=np.uint8, count=1)[0]
                stream_header['event_name']   = f_dict['event_name']

                if stream_header['file_version'] < 4:

                    # prior to v3, OpenEx and RS4 were not setting this properly
                    # (one of them was flipping it), so only trust the event name in 
                    # header if file_version is 3 or higher
                    temp_event_name = np.fromfile(sev, dtype=np.uint8, count=4)
                    temp_event_name = ''.join([chr(item) for item in temp_event_name])
                    if stream_header['file_version'] >= 3:
                        stream_header['event_name'] = temp_event_name

                    # current channel of stream
                    stream_header['channel_num'] = np.fromfile(sev, dtype=np.uint16, count=1)[0]
                    f_dict['chan'] = stream_header['channel_num']
                    # total number of channels in the stream
                    stream_header['total_num_channels'] = np.fromfile(sev, dtype=np.uint16, count=1)[0]
                    # number of bytes per sample
                    stream_header['sample_width_bytes'] = np.fromfile(sev, dtype=np.uint16, count=1)[0]
                    reserved = np.fromfile(sev, dtype=np.uint16, count=1)[0]

                    # data format of stream in lower 3 bits
                    data_format = np.fromfile(sev, dtype=np.uint8, count=1)[0]
                    data_format &= 0b111
                    stream_header['data_format'] = self._allowed_formats[data_format]

                    # used to compute actual sampling rate
                    stream_header['decimate']   = np.fromfile(sev, dtype=np.uint8, count=1)[0]
                    stream_header['rate']       = np.fromfile(sev, dtype=np.uint16, count=1)[0]
                else:
                    raise Exception('unknown version {0}'.format(stream_header['file_version']))

                # compute sampling rate
                if stream_header['file_version'] > 0:
                    stream_header['fs'] = np.power(2.,(stream_header['rate'] - 12)) * 25000000 / stream_header['decimate']
                else:
                    # make some assumptions if we don't have a real header
                    stream_header['data_format'] = 'single'
                    stream_header['fs'] = 24414.0625
                    stream_header['channel_num'] = f_dict['chan']
                    warnings.warn('''{0} has empty header;\nassuming {1} ch {2} format {3}\nupgrade to OpenEx v2.18 or above\n'''.format(f_dict['name'],
                                                 stream_header['event_name'],
                                                 stream_header['channel_num'],
                                                 stream_header['data_format']), Warning)

                # if fs > 0:
                #     stream_header['fs'] = fs

                #varname = fix_var_name(stream_header['event_name'])
                #f_dict['varName'] = varname
                f_dict['itemsize'] = np.uint64(np.dtype(stream_header['data_format']).itemsize)
                f_dict['npts'] = int(f_dict['data_size'] // f_dict['itemsize'])
                f_dict['fs'] = stream_header['fs']
                f_dict['data_format'] = stream_header['data_format']
                f_dict['event_name'] = stream_header['event_name']

        #=====================================
                
        sev_fnames = [f for f in os.listdir(self.path) if f[-4:] == '.sev']
        
        self._sev_files = [{'fname':f,'path':os.path.join(self.path,f)} for f in sev_fnames]

        chan_search = re.compile('_[Cc]h([0-9]*)')
        hour_search = re.compile('-([0-9]*)h')

        # Compile info on each sev file
        for f_dict in self._sev_files:
            # Determine channel number
            match_result = chan_search.findall(f_dict['fname'])
            if match_result:
                f_dict['chan'] = int(match_result[-1])
            else:
                f_dict['chan'] = -1

            # Determine starting hour
            match_result = hour_search.findall(f_dict['fname'])
            if match_result:
                f_dict['hour'] = int(match_result[-1])
            else:
                f_dict['hour'] = 0

            # Determine event name of stream
            f_dict['event_name'] = f_dict['fname'].split('_')[-2]

            # Determine filesize
            f_dict['data_size'] = os.stat(f_dict['path']).st_size - 40 # not sure what the -40 is for, a header?

            # Read header info
            f_dict = read_sev_header(f_dict)

        event_names = list(set([f_dict['event_name'] for f_dict in self._sev_files]))
        self._sev_store_names = event_names
        
    def _get_sortIDs(self):
        '''
        Looks like it loads sort IDs from a sort/ directory. Skipping for now
        '''
        pass

    def _create_stream_info(self):
        '''
        Collects important information about streams
        '''
        for name, info in self.headerStruct['stores'].items():
            self.stream_info[name] = {
                'type'  : info['typeStr'],
                'fs'    : info['fs'] if 'fs' in info else None,
                'nChan' : max(info['channel']) if 'channel' in info else None,
                'dtype' : self._dtypes[info['dtype']],
            }
        
    def _read_tev(self, stores=None):
        for storeName, store in self.headerStruct['stores'].items():
            if stores is None or storeName in stores:
                size = store['size']
                storeType = store['typeStr']
                dtype = self._dtypes[store['dtype']]
                #fs = store['fs']

                if store['typeStr'] == 'streams':
                    self._data[storeName] = {
                        'type' : 'stream',
                        'fs'   : store['fs']
                    }

                    nChan = np.max(store['channel'])
                    chanOffsets = np.zeros(nChan,dtype=int)

                    nPts = int((size-10) * 4 / np.array(1,dtype=dtype).nbytes) #number of points per block
                    nStores = store['offsets'].size  
                    self._data[storeName]['data'] = np.zeros((int(nPts*nStores/nChan), nChan),dtype=dtype)

                    for i in range(len(store['offsets'])):
                        self._tev.seek(store['offsets'][i],0)
                        chan = store['channel'][i] - 1
                        x = np.fromfile(self._tev, dtype=dtype, count=nPts)

                        self._data[storeName]['data'][chanOffsets[chan]:chanOffsets[chan]+nPts, chan] = x
                        chanOffsets[chan] += nPts

                elif store['typeStr'] == 'epocs':
                    self._data[storeName] = store.copy()
  
                elif store['typeStr'] == 'scalars':
                    pass

                elif store['typeStr'] == 'snpis':
                    pass

                else:
                    pass

    def _read_sev(self, stores):
        '''
        Read sev stores
        '''        
        for store_name in stores:
            # get file list for this store
            file_list = [f for f in self._sev_files if f['event_name'] == store_name]
            
            # extract header info
            fs = file_list[0]['fs']
            store_name = file_list[0]['event_name']
            data_format = file_list[0]['data_format']

            chans = [f['chan'] for f in file_list]
            hours = [f['hour'] for f in file_list]
            max_chan = np.max(chans)
            min_chan = np.min(chans)
            max_hour = np.max(hours)
            hour_values = sorted(list(set(hours)))
            
            search_ch = min_chan # We could use this later to read only specified channel
            
            # determine number of samples across chunks
            total_samples = np.uint64(0)
            npts = [np.uint64(0) for i in hour_values]
            for hour in hour_values:
                hour_mask = np.asarray(hours) == hour
                chan_mask = np.asarray(chans) == search_ch
                temp_num = np.where(hour_mask & chan_mask)[0]
                if len(temp_num) < 1:
                    raise Exception('matching file not found for hour {0} channel {1}'.format(hour, search_ch))
                elif len(temp_num) > 1:
                    raise Exception('too many matches found for hour {0} channel {1}'.format(hour, search_ch))
                temp_num = temp_num[0]
                npts[hour] = np.uint64(file_list[temp_num]['npts'])
                total_samples += npts[hour]
                
            # Create data array
            channels = sorted(list(set(chans)))
            self._data[store_name] = {
                'type' : 'stream',
                'fs'   : file_list[0]['fs'],
                'data' : np.zeros((total_samples, len(channels)), dtype=file_list[0]['data_format'])
                }

            unique_hours = sorted(list(set(hours)))
            # Loop through channels
            for chan in channels:
                chan_index = np.uint64(0)

                chan_mask = np.asarray(chans) == chan

                # loop through chunks
                for hour in unique_hours:
                    hour_mask = np.asarray(hours) == hour
                    file_num = np.where(hour_mask & chan_mask)[0][0]

                    f_dict = file_list[file_num]
                    
                    # open file
                    with open(f_dict['path'],'rb') as f:

                        # skip first 40 bytes from header
                        f.seek(40, os.SEEK_SET)

                        MAX_UINT64 = np.iinfo(np.uint64).max #MAX_UINT64
                        # Here, we can change the first and last samples to read specific parts of the data in the future
                        firstSample = 0
                        lastSample = MAX_UINT64
                        
                        # skip ahead
                        if firstSample > 0:
                            f.seek(int(firstSample * f_dict['itemsize']), os.SEEK_CUR)
                        if lastSample == MAX_UINT64:
                            ddd = np.frombuffer(f.read(), dtype=f_dict['data_format'])
                        else:
                            ddd = np.frombuffer(f.read(int((lastSample - firstSample)*file_list[file_num]['itemsize'])), dtype=f_dict['data_format'])
                        read_size = np.uint64(len(ddd))

                        if len(channels) > 1:
                            self._data[store_name]['data'][int(chan_index):int(chan_index + read_size), chan-1] = ddd
                        else:
                            self._data[store_name]['data'][int(chan_index):int(chan_index + read_size), 0] = ddd
                        chan_index = chan_index + read_size
            
    def _get_data_info(self):
        self._data['info'] = {
            'blockpath'     : None,
            'blockname'     : None,
            'date'          : None,
            'utcStartTime'  : None,
            'utcStopTime'   : None,
            'duration'      : None,
            'streamChannel' : None,
            'snipChannel'   : None,
        }

    def _code2type(self,code):
        '''
        Given a code, returns string
        '''
        #if code == self._event_types['STREAM']:
        if code & self._event_types['MASK'] == self._event_types['STREAM']:  #Straight from TDT code. Don't know why
            code_str = 'streams'
        elif code == self._event_types['SNIP']:
            code_str = 'snips'
        elif code == self._event_types['SCALAR']:
            code_str = 'scalars'
        elif code in [self._event_types['STRON'], self._event_types['STROFF'], self._event_types['MARK']]:
            code_str = 'epocs'
        else:
            code_str = 'unknown'
        
        return code_str

    def _epoc2type(self,code):
        if code in [self._event_types['STRON'], self._event_types['MARK']]:
            code_str = 'onset'
        elif code == self._event_types['STROFF']:
            code_str = 'offset'
        else:
            code_str = 'unknown'

        return code_str
        
    def _set_globals(self):
        self._event_types = {
            'UNKNOWN'      : int('0x00000000',16),
            'STRON'        : int('0x00000101',16),
            'STROFF'       : int('0x00000102',16),
            'SCALAR'       : int('0x00000201',16),
            'STREAM'       : int('0x00008101',16),
            'SNIP'         : int('0x00008201',16),
            'MARK'         : int('0x00008801',16),
            'HASDATA'      : int('0x00008000',16),
            'UCF'          : int('0x00000010',16),
            'PHANTOM'      : int('0x00000020',16),
            'MASK'         : int('0x0000FF0F',16),
            'INVALID_MASK' : int('0xFFFF0000',16),
        }
        self._event_marks = {
            'STARTBLOCK' : b'\x01', #int('0x0001',16),
            'STOPBLOCK'  : b'\x02', #int('0x0002',16),
        }
        self._data_formats = {
            'float'      : 0,
            'long'       : 1,
            'short'      : 2,
            'byte'       : 3,
            'double'     : 4,
            'qword'      : 5,
            'type_count' : 6
        }
        self._allowed_formats = [np.float32, np.int32, np.int16, np.int8, np.float64, np.int64]


        self._dtypes = ['float32','int32','int16','int8','float64','']
        
    def __del__(self):
        pass

    def __str__(self):

        s = 'TDT block\n'\
            '  Block name : {}\n'\
            '  Store info :\n'.format(os.path.basename(self.path))
        
        stream_info_dict = {'Store' : []}

        for key, value in self.stream_info.items():
            stream_info_dict['Store'].append(key)
            for k, v in value.items():
                if k not in stream_info_dict:
                    stream_info_dict[k] = []
                stream_info_dict[k].append(v)

        s += indent(tabulate(stream_info_dict, headers='keys', tablefmt='simple'), '    ')
        
        return s
    
def is_block(path):
    '''
    Checks if the given path is a tdt block.

    Parameters
    ----------
    block : str
        Block path

    Returns
    -------
    is_block : bool
        True if `path` is a tdt block, else False
    '''
    #Check that path exists...
    if not os.path.isdir(path):
        return False
    
    fnames = os.listdir(path)
    if any('.tsq' in fname for fname in fnames):
        return True

    return False

def is_tank(path):
    '''
    Check if the given path is a tdt tank. A tank is any directory with one
    or more blocks.

    Parameters
    ----------
    block : str
        Block path

    Returns
    -------
    is_block : bool
        True if `path` is a tdt block, else False
    '''
    #Check that path exists...
    if not os.path.isdir(path):
        return False
    
    dirs = os.listdir(path)
    if any(is_block(os.path.join(path, d)) for d in dirs):
        return True

    return False
