"""
Custom modules/classes/methods for various data science, computer vision, and machine learning operations in python
"""

__version__ = '2.0.0'

import sys, os

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0,  os.path.dirname(os.path.abspath(__file__)))
    
import JL_plot as plot
import summary_tables
import img
import JL_ML_models as ML_models
import JL_kaggle as kaggle

print('JLpy_utils_package mounted (repo: https://github.com/jlnerd/JLpy_utils_package.git)')