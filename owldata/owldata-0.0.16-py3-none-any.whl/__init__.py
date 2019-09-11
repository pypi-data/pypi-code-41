#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# =====================================================================
# Copyright (C) 2018-2019 by Owl Data
# author: Danny, Destiny

# =====================================================================

from .api import OwlData
from .__version__ import __version__

__docformat__ = 'restructuredtext'
__doc__ = '''
OwlData 數據貓頭鷹 API
==============================

## 數據貓頭鷹官方網站: https://owl.cmoney.com.tw/Owl/

**owldata** 提供一個穩定且快速的介面獲取數據貓頭鷹任何資料

Quick Start
-----------

import owldata

# 輸入數據貓頭鷹會員 AppID & 應用程式密鑰
appid = '請輸入 AppID'
appsecret = '請輸入 應用程式密鑰'

# 引用函數取得資料
owlapp = owldata.OwlData(appid, appsecret)

# 擷取台積電股價 from 2019/08/12 to 2019/08/13
stock_price = owlapp.ssp("2330", "20190812", "20190813")
stock_price.head()


'''
