from . import general_info
from . import total_review
from . import functions

def libinfo():
    print('''
    Surveyor library structure:
    version: pre-alpha-zero.
    1. General info
    2. Total review
        - Overwiew
        - Variables review
        - Correlations
        - Samples
        - Distributions of variable
    3. Functions
        - Concatenate specified files to one df
        - Fillna (specify 'na' appearance)
        - Convert series to str
        - Convert series to date
        - Convert series to numeric (specify int or float)
        - Convert series to categorical (get label encoded series with mapping)
        - Save to excel
        - Save to html (?)
    ''')
