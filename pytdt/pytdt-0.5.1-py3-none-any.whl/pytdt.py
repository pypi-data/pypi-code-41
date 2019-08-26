import numpy as np
import os
import struct
from tabulate import tabulate
from textwrap import indent

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

        #Read notes
        self._read_tnt()

        #Look for sort IDs
        self._get_sortIDs()

        #Read block notes
        self._read_blockNotes()
        
        #Read headers
        self._read_headers()

        self._create_stream_info()

    def read_stores(self, stores=None):
        '''
        Read specified stores. If no stores are specified, all stores are read

        Parameters
        ----------
        stores : str, list
            Name or names of stores to be read. If None, all stores are read.
        '''
        
        #Extract data from .TEV file
        self._read_TEV(stores)

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
    def _read_tnt(self):
        '''
        The tnt file appears to be a note file. Skipping for now
        '''
        pass

    def _get_sortIDs(self):
        '''
        Looks like it loads sort IDs from a sort/ directory. Skipping for now
        '''
        pass

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
                print(line)
                items = line.split(';')
                fieldstr = items[0].split('=')[1]
                value = items[2].split('=')[1]

            blockNotesList[storenum][fieldstr] = value
        
        # Convert blocknots from list to dict
        self.blockNotes = {store['StoreName']:store for store in blockNotesList}
        
    def _read_headers(self):
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
        
    def _read_TEV(self, stores=None):
        
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
        if code == self._event_types['STREAM']:
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
