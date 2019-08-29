from requestutil import *
import logging
from fastai.core import *


## Common Data Util methods

def downloaderV1(url, fname=None, folder=None):
    """
    Retirve the url content & save into file name {fname}
    """
    if not fname:
        fname = url.split("/")[-1]
    resp = GetRaw(url)
    try:
        if folder: 
          p = Path(folder); p.mkdir(exist_ok=True)
          if not str(folder).endswith("/"):
            folder = folder + "/"
          fname = folder + fname
        with open(fname, 'wb') as f: f.write(resp.content)
    except Exception as e:
        print("something went wrong while writing.")
        print(e)