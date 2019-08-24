'''
Created on Apr 16, 2019

@author: danielk
'''
import EMaligner.EMaligner as ema
from EMaligner.utils import EMalignerException
import json
import tracemalloc
import linecache
import os
from trace_print import display_top

jpath = '/allen/programs/celltypes/workgroups/em-connectomics/danielk/EM_aligner_python/tmp_input.json'






def myfun():
    #tracemalloc.start()
    with open(jpath, 'r') as f:
        j = json.load(f)
    j['output_mode'] = 'none'
    j['profile_data_load'] = False
    j['input_stack']['db_interface'] = 'render'
    j['pointmatch']['db_interface'] = 'render'
    print(j.keys()) 
    
    e = ema.EMaligner(input_data=j, args=[])
    #snapshot1 = tracemalloc.take_snapshot()    
    try:
        e.run()
    except EMalignerException:
        pass
    print(e.results['precision'])


    #snapshot2 = tracemalloc.take_snapshot()
    #top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    #display_top(snapshot2) 
    #print("[ Top 10 differences ]")
    #for stat in top_stats[:10]:
    #   print(stat)

                                                     
if __name__ == '__main__':
    tracemalloc.start()                                                                       
    snapshot1 = tracemalloc.take_snapshot()                                                   
    myfun()
    snapshot2 = tracemalloc.take_snapshot()
    display_top(snapshot2)
    top_stats = snapshot2.compare_to(snapshot1, 'lineno') 
    print("[ Top 10 differences ]")          
    for stat in top_stats[:10]:      
        print(stat)                  

    print('Hello World')


