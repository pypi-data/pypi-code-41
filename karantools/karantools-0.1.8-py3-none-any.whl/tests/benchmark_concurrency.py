import time
import numpy as np
import multiprocessing
import karantools as kt
import functools

def get_row_average(idx):
	return np.average(A[idx])

def load_A():
	return np.random.randn(100000, 5000)

def _sublist_map_fn(map_fn, A, axis, sublist):
    return map_fn(A[sublist], axis=axis)

kt.time.start('Create/load array')
A = kt.lazy_load(load_A, 'temp_benchmark_concurrency_file.pkl')
kt.time.end()

def main():

	kt.time.start('Numpy average over 1 axis')
	np_averages = np.average(A, axis=1)
	kt.time.end()


	# kt.time.start('For loop average')
	# averages = []
	# for i in range(A.shape[0]):
	# 	averages.append(get_row_average(i))
	# kt.time.end()

	# assert(np.allclose(np_averages, averages))

	# kt.time.start('Normal pool map with 10 workers')
	# p = multiprocessing.Pool(10)
	# pool_averages = p.map(get_row_average, range(A.shape[0]), chunksize=5000)
	# kt.time.end()

	# assert(np.allclose(np_averages, pool_averages))

	kt.time.start('Kt pool with 10 workers')
	new_map_fn = functools.partial(_sublist_map_fn, np.average, A, 1)
	p = kt.VectorizedPool(2)
	
	pool_averages = p.map(new_map_fn, indices=range(A.shape[0]), chunksize=100)
	kt.time.end()

	assert(np.allclose(np_averages, pool_averages))

	kt.time.print_times()

		

if __name__=='__main__':
	main()