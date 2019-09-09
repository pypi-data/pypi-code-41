# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 22:12:43 2019

@author: Reuben
"""

import os
import pandas as pd

from . import persist

root = os.path.dirname(os.path.abspath(__file__))

def set_root(new):
    global root
    root = new
    

class Automator():
    def __init__(self, container, fname):
        self.container = container
        self.sets = persist.automation_load(fname)
        
    def run(self, set_name, obj):
        data = self.sets[set_name]
        s = Sequencer(data['sequences'], data['aliases'], data['vectors'])
        obj.prepare()
        for seq_name, seq_dct in s.all_sequences().items():
            self.execute_sequence(seq_name, seq_dct, obj)
        obj.finish()

    def execute_sequence(self, seq_name, seq_dct, obj):
        obj.prepare_sequence(seq_name)
        for method_name, dct in seq_dct.items():
            self.execute_method(method_name, seq_name,
                                dct['val_list'],
                                dct['label_lst'],
                                obj)
        obj.finish_sequence(seq_name)

    def execute_method(self, method_name, seq_name, val_list, label_lst, obj):
        container = self.container
        obj.prepare_method(method_name)
        method = getattr(obj, method_name)
        with container.context(val_list[0]):
            for val_dct, label_dct in zip(val_list, label_lst):
                container.dset(val_dct)
                method(seq_name, val_dct, label_dct)
        obj.finish_method(method_name)
        
    
class Aliases(dict):
       
    def translate(self, dct):
        out = {}
        for k, v in dct.items():
            if k in self:
                out[self[k]] = v
            else:
                out[k] = v
        return out
    
    
class Vector():
    ''' Subclass for different entry formats '''
    def __init__(self, name):
        self.name =  name
        self.i = 0
        self.child = None
        
    def initialise(self, data):
        self.labels, self.data = self.setup(data)
        self.n = len(self.labels)
    
    def setup(self, data):
        raise NotImplementedError
        
    def set_child(self, vector):
        self.child = vector
        
    def get_lst(self, lst=None, d=None):
        lst = [] if lst is None else lst
        d = {} if d is None else d
        for dct in self.data:
            d.update(dct)
            if self.child is not None:
                self.child.get_lst(lst, d)
            else:
                lst.append(d.copy())
        return lst
    
    def get_label_lst(self, lst=None, d=None):
        lst = [] if lst is None else lst
        d = {} if d is None else d
        for label in self.labels:
            d[self.name] = label
            if self.child is not None:
                self.child.get_label_lst(lst, d)
            else:
                lst.append(d.copy())
        return lst

class List_Vector(Vector):
    def transpose_dict(self, dct):
        n = len(list(dct.values())[0])
        out = [{} for i in range(n)]
        for i in range(n):
            for k, v in dct.items():
                out[i][k] = v[i]
        return out
    
    def setup(self, data):
        def default_labels(d):
            for v in dct.values():
                n = len(v)
                return [i for i in range(n)]
        dct = data.copy()
        labels = dct.pop('labels', default_labels(dct))
        return labels, self.transpose_dict(dct)    

class Dict_List_Vector(Vector):
    def setup(self, data):
        labels = []
        d = []
        for k, dct in data.items():
            labels.append(k)
            d.append(dct)
        return labels, d

class Csv_File(Vector):
    def setup(self, data):
        d = []
        full_filename = os.path.join(root, data['filename'])
        df = pd.read_csv(full_filename, index_col=0)
        labels = list(df.index)
        for index, row in df.iterrows():
            d.append(row.to_dict())
        return labels, d

    
class Vector_Factory():
    @classmethod
    def new(cls, data, name):
        if 'style' not in data:
            v = List_Vector(name)
            v.initialise(data)
            return v
        elif data['style'] == 'value_dictionaries':
            v = Dict_List_Vector(name)
        elif data['style'] == 'csv':
            v = Csv_File(name)
        d = data.copy()
        d.pop('style')
        v.initialise(d)
        return v
            
    
class Vectors():
    def __init__(self, data):
        self.data = data
    
    def loop(self, v_names):
        root = None
        vectors = {k: Vector_Factory.new(v, k) for k, v in self.data.items()}
        for v_name in v_names:
            if root is None:
                root = vectors[v_name]
                current = vectors[v_name]
            else:
                current.set_child(vectors[v_name])
                current = vectors[v_name]
        return root.get_lst(), root.get_label_lst()
        
        
class Sequencer():
    def __init__(self, sequences, aliases, vectors):
        self.sequences = sequences
        self.aliases = Aliases(aliases)
        self.vectors = Vectors(vectors)
        
    def sequence(self, name):
        seq_dct = {}
        s = self.sequences[name]
        for method_name, v_names in s.items():
            val_list, label_lst = self.vectors.loop(v_names)
            val_list = [self.aliases.translate(d) for d in val_list]
            seq_dct[method_name] = {'val_list': val_list,
                                    'label_lst': label_lst}
        return seq_dct
    
    @property
    def sequence_names(self):
        return list(self.sequences.keys())
        
    def all_sequences(self):
        out = {}
        for seq_name in self.sequence_names:
            seq_dct = self.sequence(seq_name)
            out[seq_name] = seq_dct
        return out
        

