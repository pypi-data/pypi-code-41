import time

from keras import models
from pylinac.core.image import prepare_for_classification
import numpy as np

sii = models.load_model(r'E:\Nextcloud\Programming\Python\Projects\pylinac\keras_SII.h5')

arr = prepare_for_classification(r'E:\Nextcloud\Programming\Python\Projects\pylinac\pylinac\demo_files\picket_fence\EPID-PF-LR.dcm')
arr = np.reshape(arr, (1, 100, 100, 1))
start = time.time()
p = sii.predict(arr)
print(time.time() - start)
print(p)
