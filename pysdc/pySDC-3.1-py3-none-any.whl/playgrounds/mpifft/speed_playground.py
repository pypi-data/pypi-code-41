from mpi4py import MPI
from mpi4py_fft import PFFT, newDistArray
import time
import numpy as np

comm = MPI.COMM_WORLD
shape = (512, 512)
axes = (0, 1)

fft = PFFT(comm, shape, axes=axes, dtype=np.complex128, collapse=True)

ra = newDistArray(fft, False)
ia = newDistArray(fft, True)
print(ra.dtype, ia.dtype)

np.random.seed(1)
a = np.random.randn(*ra.shape).astype(np.float64)
a = a + 1j*np.random.randn(*ra.shape).astype(np.float64)

t0 = time.time()
ia[:] = fft.forward(a, ia)
ra[:] = fft.backward(ia, ra)
print('CPU Time:', time.time()-t0)
print('CPU Error:', np.amax(abs(a-ra)))