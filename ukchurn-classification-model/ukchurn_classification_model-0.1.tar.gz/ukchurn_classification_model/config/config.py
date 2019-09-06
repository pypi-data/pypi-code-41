# libs
import os
import pathlib

# packages
import ukchurn_classification_model

# main root directories
PACKAGE_ROOT = pathlib.Path(ukchurn_classification_model.__file__).resolve().parent
TRAINED_MODEL_DIR = PACKAGE_ROOT / 'trained_model'
DATASET_DIR = PACKAGE_ROOT / 'datasets'


# data directories
GLOBAL_DATA_FILE = DATASET_DIR / 'Churn_complete_dataset_270819.csv'
TRAINING_DATA_FILE = DATASET_DIR / 'ukchurn_train.csv'
TESTING_DATA_FILE = DATASET_DIR / 'ukchurn_test.csv'

# variables
TARGET = 'Churn'

FEATURES = ['PercentageCompletedSurveys1Months', 'SocialGrade', 'DemographicsCompleted', 'LevelWeeks',
            'WorkingSituation', 'DistinctDailySubmissions2Week', 'CurrentPointsBalance', 'IsUserDisabled',
            'DistinctDailySubmissions3Month', 'DaysBetweenReceipts3Month',
            'TotalReceipts2Week', 'DaysBetweenReceipts2Week', 'ManagerOrDirector', 'AppUserAge','AppNotificationOn',
            'AverageAge', 'HouseHoldSumGenders1', 'NumberIndividualsInHousehold', 'Income', 'HouseHoldSumGenders2',
            'AppUserGender']


# numerical variables with NA in train set
NUMERICAL_VARS_WITH_NA = ['AverageAge', 'AppUserAge', 'AppUserGender', 'HouseHoldSumGenders1',
                          'HouseHoldSumGenders2']

# numerical variables with NA in train set that need to be replaced by 0
NUMERICAL_VARS_WITH_NA_ZERO = ['PercentageCompletedSurveys1Months']

# categorical variables with NA in train set
CATEGORICAL_VARS_WITH_NA = ['SocialGrade', 'Income', 'WorkingSituation']

# categorical variables to encode
CATEGORICAL_VARS = ['SocialGrade', 'WorkingSituation', 'Income']

# variables where numerical imputation are not allowed since they were not seen during training
NUMERICAL_NA_NOT_ALLOWED = [
    feature for feature in FEATURES
    if feature not in CATEGORICAL_VARS + NUMERICAL_VARS_WITH_NA + NUMERICAL_VARS_WITH_NA_ZERO
]

# variables where categorical imputation are not allowed since they were not seen during training
CATEGORICAL_NA_NOT_ALLOWED = [
    feature for feature in CATEGORICAL_VARS
    if feature not in CATEGORICAL_VARS_WITH_NA
]

PIPELINE_NAME = 'uk_churn_model.pkl'


