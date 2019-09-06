# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 08:27:35 2019

@author: 10167232
"""
path = 'data_pickle'
type_list = ['str','function','pandas.core.frame.DataFrame',
             'pandas.core.series.Series','numpy.ndarray','int',
             'float','bool','complex','list','dict','set','tuple']
drop_list = ['In','Out','var_dic_list','get_ipython','']


class Config:
    def __init__(self):
        self.type_level = [['pandas.core.frame.DataFrame','pandas.core.series.Series','numpy.ndarray'],
                           ['str','function','pandas.core.frame.DataFrame','pandas.core.series.Series','float','bool','complex'],
                           ['str','function','pandas.core.frame.DataFrame','pandas.core.series.Series','numpy.ndarray','int','float','bool','complex','list','dict','set','tuple']]
        self.drop_list = ['In','Out','var_dic_list','get_ipython','']
        self.path = 'data_pickle'
     