'''ir_bench.py
'''

import os
import sys

from .ir_searcher import IRSearcher
from .ir_evaluator import IREvaluator


class IRBench(object):
    def __init__(self, config):
        
        # default config:
        self.config = dict()
        self.config['search_method'] = 'brute-force'
        
        assert type(config) == dict
        for k, v in config:
            self.set_config(k, v)

    def set_config(self, key, value):
        assert key in self.config
        self.config[key] = value

    
    # Feed Functions.    
    def feed_for_search(self, data, mode):
        '''
        feed from file path: [a/a.npy, b/b.npy. c/c.npy ...]
        feed from np array: [np.ndarray1, np.ndarray2, np.ndarray3, ...]
        '''
        pass;
    
    def feed_for_eval(self, data, mode):
        assert mode in { 'gt', 'rank' }, 'Invalid argument mode: {}'.format(mode)

    # Search Functions.
    def search(self, top_k, scoring, l2_norm=False, query_feat = None)
        '''
        if query_feat is None:
            search with all feeded query features.
        else:
            search with provided single query feautre.
        '''

    # Eval Fucntions.
    def evaluate(self):
        pass;

    # Load Functions.

    # Utils Functions.
    def sample(self):
        pass;
        
    def idx2id(self):
        pass;

    def id2idx(self):
        pass;
        
    def get_data_length(self, target=None):
        pass;



if __name__ == "__main__":
    irbench = IRBench('g')

