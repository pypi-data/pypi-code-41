"""
Functions to inspect features and/or models after training
"""
import sys as __sys__ 
import os as __os__
if __os__.path.dirname(__os__.path.abspath(__file__)) not in __sys__.path:
    __sys__.path.insert(0,  __os__.path.dirname(__os__.path.abspath(__file__)))
    
import JL_ML_compare as compare
import JL_ML_plot as plot