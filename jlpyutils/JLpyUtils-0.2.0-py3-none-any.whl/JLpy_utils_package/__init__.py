"""
Custom modules/classes/methods for various data science, computer vision, and machine learning operations in python
"""

__version__ = '2.0.5'
__repo__ = "https://github.com/jlnerd/JLpy_utils_package.git",

import sys as __sys__ 
import os as __os__
if __os__.path.dirname(__os__.path.abspath(__file__)) not in __sys__.path:
    __sys__.path.insert(0,  __os__.path.dirname(__os__.path.abspath(__file__)))
    
import JL_plot as plot
import JL_summary_tables as summary_tables
import JL_img as img
import JL_video as video
import JL_ML_models as ML_models
import JL_kaggle as kaggle
import JL_file_utils as file_utils