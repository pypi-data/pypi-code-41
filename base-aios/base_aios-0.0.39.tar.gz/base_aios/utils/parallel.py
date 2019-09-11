import os
from math import ceil
from concurrent.futures import ThreadPoolExecutor as Pool
from concurrent.futures import wait

__all__ = ('parallel',)

def _chunk(array, size=1):
    chunks = int(ceil(len(array) / float(size)))
    return [array[i * size:(i + 1) * size] for i in range(chunks)]

def parallel(task, data, return_when='ALL_COMPLETED', chunk_size=None, workers=None, debug=False):
    '''并行计算  
    workers  默认为2*N + 1, N是CPU个数  
    chunk_size  默认为len(data) / workers
    '''
    workers = workers or os.cpu_count() * 2 + 1
    chunk_size = chunk_size or ceil(len(data) / workers)
    chunk_data = _chunk(data, chunk_size)
    with Pool(max_workers=workers) as executor:
        future_tasks = [executor.submit(task, c_data) for c_data in chunk_data]
        if debug:
            for f in future_tasks:
                if f.running():
                    print('%s is running' % str(f))

            print('workers:', workers)
            print('chunk_size:', chunk_size)
    return wait(future_tasks, None, return_when=return_when)
