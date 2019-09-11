#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# =====================================================================
# Copyright (C) 2018-2019 by Owl Data
# author: Danny, Destiny

# =====================================================================

import datetime
import pandas as pd
from ._owlerror import OwlError

# --------------------
# BLOCK 商品資訊與時間表
# --------------------
# 取得函數與商品對應表
class _DataID():
    def __init__(self):
        # 商品表
        #self._fp = ''
        
        # 商品時間對照表
        self._table_code = {
            'd':'PYCtrl-14806a/',
            'm':'PYCtrl-14809a/',
            'q':'PYCtrl-14810a/',
            'y':'PYCtrl-14811a/'
            }
        self._table_code_test ={
            'd':'PYCtrl-14892a/',
            'm':'PYCtrl-14891a/',
            'q':'PYCtrl-14890a/',
            'y':'PYCtrl-14889b/'            
            }
        
        # 商品時間表
        self._table = {}
        
        self._pdid_map

    # 取得函數與商品對應表
    def _pdid_map(self):
        '''
        擷取商品函數與商品ID表
        Returns
        ----------
        :DataFrame:
            FuncID          pdid
            ssp 	PYPRI-14776a
            msp 	PYPRI-14777b
            sby		PYBAL-14782a
            sbq		PYBAL-14780a
        
        [Notes]
        ----------
        FuncID: ssp-個股股價, msp-多股股價, sby-年度資產負債表(個股), sbq-季度資產負債表(個股)
        pdid: 商品對應的ID
        '''
        get_data_url = self._token['data_url'] + self._token['pythonmap']
        try:
            self._fp = self._data_from_owl(get_data_url).set_index("FuncID")
        except:
            get_data_url = self._token['data_url'] + self._token['testmap']
            self._fp = self._data_from_owl(get_data_url).set_index("FuncID")
        return self._fp
    # 取得函數對應商品
    def _get_pdid(self, funcname:str):
        return self._fp.loc[funcname][0]
    
    # 商品時間
    def _date_table(self, freq:str):
        get_data_url = self._token['data_url'] + self._table_code[freq.lower()]
        data = self._data_from_owl(get_data_url)
        if type(data) == str:
            get_data_url = self._token['data_url'] + self._table_code_test[freq.lower()]
        if freq.lower() == 'd':
            get_data_url = get_data_url + '/TWA00/9999'
        return self._data_from_owl(get_data_url)
    # 商品時間頻率對照表
    def _date_freq(self, start:str, end:str, freq = 'd'):
        season = ['0' + str(x) for x in range(5,13)]

        if freq.lower() not in self._table.keys():
            self._table[freq.lower()] = self._date_table(freq.lower())
        
        if freq.lower() == 'y':
            if len(start) != 4 or len(end) != 4:
                print('YearError:',OwlError._dicts['YearError'])
                return 'error'
            try:
                dt = pd.to_datetime(start, format = '%Y')
                dt = pd.to_datetime(end, format = '%Y')

            except ValueError:
                print('ValueError:', OwlError._dicts["ValueError"])
                return 'error'

        elif freq.lower() == 'm':
            if len(start) != 6 or len(end) != 6:
                print('MonthError:',OwlError._dicts['MonthError'])
                return 'error'
            try:
                dt = pd.to_datetime(start, format = '%Y%m')
                dt = pd.to_datetime(end, format = '%Y%m')
                         
            except ValueError:
                print('ValueError:', OwlError._dicts["ValueError"])
                return 'error'

        elif freq.lower() == 'q':
            if len(start) != 6 or len(end) != 6:
                print('SeasonError:',OwlError._dicts['SeasonError'])
                return 'error'

            if start[4:6] in season or end[4:6] in season:
                print('SeasonError2:',OwlError._dicts['SeasonError2'])
                return 'error'

        elif freq.lower() == 'd':
            if len(start) != 8 or len(end) != 8:
                print('DayError:',OwlError._dicts['DayError'])
                return 'error'
            
            try:
                dt = pd.to_datetime(start)
                dt = pd.to_datetime(end)
                
            except ValueError:
                print('ValueError:', OwlError._dicts["ValueError"])
                return 'error'

        if int(start) > int(end):
            print('DateError:',OwlError._dicts['DateError'])
            return 'error'
        
        temp = self._table[freq.lower()].copy()
        temp = temp[temp[temp.columns[0]].between(start, end)]
        if len(temp) == 0:
            print('CannotFind:', OwlError._dicts["CannotFind"])
            return 'error'
        return str(len(temp))
