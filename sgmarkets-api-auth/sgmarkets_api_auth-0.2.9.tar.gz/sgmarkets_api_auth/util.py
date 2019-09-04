
import os
import pickle
import gzip

import datetime as dt


def topickle(path, obj, compresslevel=4):
    """
    pickle obj to disk 
    compresslevel from 0 to 9, 9 is default, slowest, most compressed
    """
    pickle.dump(obj=obj,
                file=gzip.open(path, 'wb', compresslevel=1),
                protocol=pickle.HIGHEST_PROTOCOL)


def unpickle(path):
    """
    unpickle obj from disk 
    """
    return pickle.load(gzip.open(path, 'rb'))


def save_result(df,
                folder_save='dump',
                name=None,
                tagged=True,
                excel=False):
    """
    save df to disk as csv or xlsx
    """
    if not os.path.exists(folder_save):
        os.makedirs(folder_save)
    if name is None:
        name = 'SG_Research'
    tag = ''
    if tagged:
        tag = dt.datetime.now().strftime('_%Y%m%d_%H%M%S')
    suffix = '.csv'
    filename = '{}{}{}'.format(name, tag, suffix)
    path = os.path.join(folder_save, filename)
    df.to_csv(path, index=None)
    print('file {} saved'.format(path))
    if excel:
        suffix = '.xlsx'
        filename = '{}{}{}'.format(name, tag, suffix)
        path = os.path.join(folder_save, filename)
        df.to_excel(path, index=None)
        print('file {} saved'.format(path))
