import os
from pathlib import Path
import time
import json
import re
import pickle
import shutil
from functools import partial
import math

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA, KernelPCA
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import MissingIndicator, SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    explained_variance_score,
    f1_score,
    log_loss,
    mean_absolute_error,
    mean_squared_error,
    mean_squared_log_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    Binarizer,
    LabelEncoder,
    MinMaxScaler,
    MultiLabelBinarizer,
    Normalizer,
    OneHotEncoder,
    OrdinalEncoder,
    PolynomialFeatures,
    RobustScaler,
    StandardScaler,
)

import tensorflow as tf
from tensorflow import keras

# My imports
from dlai.colab_utils import setup_kaggle
from dlai.colab_utils import download_kaggle_data
from dlai.colab_utils import unarchive_data

from dlai.utils import check_df_image_size
from dlai.utils import plot_df_images

from dlai.tfai import deprocess_image
from dlai.tfai import visualise_one_filter
from dlai.tfai import visualise_filters