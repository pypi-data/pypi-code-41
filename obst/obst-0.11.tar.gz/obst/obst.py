import fs
import json
import pandas as pd
import os
import uuid
import datetime

def dictadr(dict, keys):
    if len(keys) == 1:
        return dict[keys[0]]
    return dictadr(dict[keys[0]], keys[1:])

def indict(dict, keys):
    for key in keys:
        subkeys = str(key).split('.')
        if len(subkeys) == 1:
            if not key in dict:
                return False
        else:
            if not indict(dict[subkeys[0]], subkeys[1:]):
                return False
    return True

def singlem(list):
    if len(list) == 0:
        return None
    if len(list) == 1:
        return list[0]

    return list


def genopenobj(o, d):
    def open():
        return object.open(o, d)
    return open

def genidx(table, args):
    ret = []
    for name, group in table.groupby(args[0]):
        if len(args) != 1:
            values = genidx(group, args[1:])
        else:
            values = []
            for o, d in zip(group['_obst'].values, group['_datafile'].values):
                value = genopenobj(o, d)
                values.append(value)

        ret.append([name, values])
        #One could remove name, since it can be fetch by looking into the meta data of obj,
        #but prob. this is a needed info such it is faster to add it here instead
        #of opening the meta file for it.

    return ret

SUFFIX = "_metadata.meda"

class metafiles:
    '''
    The metafiles object saves the data and the meta data to two seperated files, 
    connected by the filename.

    Parameters
    ----------
    filesystem : fs
        object of fs (filesystem2) is the filesystem in which the files are created

    Attributes
    ----------
    fs : fs
        This is where we store fs
    '''
    def __init__(self, filesystem):
        self.fs = filesystem

    def write(self, name, data, meta):
        '''Creates two files and write the data and the metadata to it

        Parameters
        ----------
        name : str
            name of the data file
        data : bytes
            data will be written to file
        data : dict
            Needs to be json serializable

        '''


        self.fs.writebytes(name, data)
        meta['_datafile'] = name
        dt = datetime.datetime.now()
        meta['_time'] = str(dt)
        #meta['_timezone'] = str(dt.tzinfo)
        name, ending = os.path.splitext(name)
        self.fs.writetext(name + SUFFIX, json.dumps(meta))

    # def write_meta(self, name, meta, suffix = SUFFIX):
    #     dt = datetime.datetime.now()
    #     meta['_time'] = str(dt)
    #     #meta['_timezone'] = str(dt.tzinfo)
    #     self.fs.writetext(name + suffix, json.dumps(meta))

    def read(self, name):
        data = self.read_obj(name)
        meta = self.read_meta(name)
        return data, meta

    def read_obj(self, name):
        data = self.fs.readbytes(name)
        return data

    def read_meta(self, name, add_suffix = True):
        if add_suffix:
            name = name + SUFFIX
        raw_text = self.fs.readtext(name)
        meta = json.loads(raw_text)
        return meta

    def remove(self, name):
        self.fs.glob(name).remove()
        name, ending = os.path.splitext(name)
        self.fs.glob(name + SUFFIX).remove()

class index:
    def __init__(self, metalist):
        self.metalist = metalist
        self.table = pd.DataFrame.from_dict(self.metalist)

    def order(self, *args):
        self.table = self.table.sort_values(list(args))
        it = genidx(self.table, list(args))
        return it

    def search(self, query):
        '''Searches obst for query

        Parameters
        ----------
        query : str
            see pandas documentation
        '''
        result = self.table.query(query)
        values = []
        for o, d in zip(result['_obst'].values, result['_datafile'].values):
            value = genopenobj(o, d)
            values.append(value)
        
        return values


    def save(self, obst, name):
        #just pickle index would be the easy solution, but not nice since
        #in table there are obst_obstject saved. Would be nicer to replace this
        #with pathnames

        #also were to save? Options:
        # 1) just as file and metafile in obst, with special entries in meta
        # 2) same as 1) but in a _indicies subfolder which could be spared out when
        #      iterating

        
        pass



            
class object:
    def __init__(self, name = "", ending = '.obj', unique_id = False, data = None, meta= {}):
        self.unique_id = unique_id
        self.name = name
        self.ending = ending
        self.obst = None #parent obst if exist, otherwise None
        self._data = data
        self._meta = meta

        self._meta_loaded = False
        self._data_loaded = False

    def filename(self):
        name = self.name 
        if self.unique_id:
            name += "_" + self.uuid()
        name += self.ending

        return name

    @property
    def meta(self):
        if not self._meta_loaded and self.obst is not None:
            self._meta = self.obst.metafiles.read_meta(self.name)
            self._meta_loaded = True
        return self._meta

    @meta.setter 
    def meta(self, value): 
        self._meta = value

    @property
    def data(self): 
        if not self._data_loaded and self.obst is not None:
            self._data = self.obst.metafiles.read_obj(self.name + self.ending)
            self._data_loaded = True
        return self._data

    @data.setter 
    def data(self, value): 
        self._data = value

    def uuid(self):
        random_uuid = uuid.uuid4()
        return str(random_uuid)

    @staticmethod
    def open(obst_obj, name):
        name, ending = os.path.splitext(name)
        obj = object(name = name, ending = ending)
        obj.obst = obst_obj
        return obj

    def remove(self):
        assert self.obst is not None, "To remove object its needs to have an assinged obst obj."
        self.obst.metafiles.remove(self.filename())



class obst:
    def __init__(self, root_fs):
        self.fs = root_fs
        self.metafiles = metafiles(self.fs)

    def sub(self, name):
        root_fs = self.fs.makedirs(name, recreate=True)
        return obst(root_fs)


    def index(self, attributes, filter=None):
        f = [filter]
        ret = self.indices([attributes], f)
        return ret[0]

    def indices(self, idx_attributes, idx_filter=[]):

        if idx_filter:
            assert len(idx_filter) == len(idx_attributes), "Filter needs an element for each attribute or None"
        else:
            idx_filter = [None for attr in idx_attributes]

        #This inititlisation is needed to make sure every index has an entry otherwise the different indicies get mixed up later, would be more elegant to fix it later instead to make this init.
        imetalist = {}
        for idx in range(len(idx_attributes)):
            imetalist[idx] = []

        for path in self.fs.walk.files(filter=['*.meda'], filter_dirs=['.']):
            meta = self.metafiles.read_meta(path, add_suffix=False)

            for idx, (attributes, filter) in enumerate(zip(idx_attributes, idx_filter)):

                if filter is not None:
                    if not filter(meta):
                        continue

                if indict(meta, attributes):
                    mrow = {
                        "_datafile" : meta["_datafile"],
                        "_obst" : self}
                    for attr in attributes:
                        subkeys = attr.split('.')
                        mrow[attr] = dictadr(meta, subkeys)
                    data = imetalist.get(idx, [])
                    data.append(mrow)
                    imetalist[idx] = data

        submetalists = []
        for dir_path in self.fs.walk.dirs():
            sub_obst = obst(self.fs.opendir(dir_path))
            submetalists.append(sub_obst.indices(idx_attributes, idx_filter=idx_filter))

        for ml in submetalists:
            for idx, il in enumerate(ml):
                data = imetalist.get(idx, [])
                data.extend(il.metalist)
                imetalist[idx] = data

        return [index(imetalist[key]) for key in imetalist]

    def insert(self, obj):
        self.metafiles.write(obj.filename(), obj.data, obj.meta)

    def write(self, name, data, meta, unique_id=False):
        obj = obst.object(name=name, unique_id = unique_id)
        obj.meta = meta
        obj.data = data
        self.insert(obj)
        
def open_obst(directory):

    import os
    if not os.path.isdir(directory):
        os.mkdir(directory)
    root_fs = fs.open_fs(directory)
    return obst(root_fs)




