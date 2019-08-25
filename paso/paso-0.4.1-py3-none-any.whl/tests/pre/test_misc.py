import pandas as pd
import warnings

warnings.filterwarnings("ignore")
from pandas.core.dtypes.generic import ABCDataFrame, ABCIndexClass, ABCSeries
import numpy as np
import pytest
from tqdm import tqdm

# paso imports
from paso.base import pasoFunction,pasoError,_Check_No_NA_Values,get_paso_log,toDataFrame,is_DataFrame
from paso.pre.misc import TfIdfVectorizer,TruncatedSVD,FillNan
#
__author__ = "Bruce_H_Cottman"
__license__ = "MIT License"