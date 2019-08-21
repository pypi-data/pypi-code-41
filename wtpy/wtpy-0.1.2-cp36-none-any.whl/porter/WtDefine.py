from ctypes import c_uint, c_void_p, WINFUNCTYPE, POINTER, c_char_p, c_bool, c_ulong
from wtpy.porter.WtStructs import  WTSBarStruct, WTSTickStruct

# 回调函数定义
CB_STRATEGY_INIT = WINFUNCTYPE(c_void_p, c_ulong)
CB_STRATEGY_TICK = WINFUNCTYPE(c_void_p, c_ulong)
CB_STRATEGY_CALC = WINFUNCTYPE(c_void_p, c_ulong)
CB_STRATEGY_BAR = WINFUNCTYPE(c_void_p, c_ulong, c_char_p, c_char_p, POINTER(WTSBarStruct))
CB_STRATEGY_GET_BAR = WINFUNCTYPE(c_void_p, c_ulong, c_char_p, c_char_p, POINTER(WTSBarStruct), c_bool)
CB_STRATEGY_GET_TICK = WINFUNCTYPE(c_void_p, c_ulong, c_char_p, POINTER(WTSTickStruct), c_bool)
