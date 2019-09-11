import tensorflow as tf
import os
import time
import numpy as np

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

"""
a = np.random.rand(10000, 10000)

x = np.random.rand(10000, 10000)

tensor = tf.constant(a)*tf.constant(x)

sess = tf.Session()

time0 = time.time()
result = sess.run(tensor)
print time.time() - time0


x = 3
a = np.arange(10000000).astype(np.float32)

time0 = time.time()
result = a*x
print time.time() - time0

"""
