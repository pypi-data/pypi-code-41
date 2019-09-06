#!/usr/bin/env python
#
# Barcerlona Supercomputing Center - Centro Nacional de Supercomputacion
#        Earth Sciences Department - Computational Earth Sciences
#     
#     Authors: Jesus Pena-Izquierdo (jesus.pena@bsc.es) 
#              Ivan Cernicharo Ortiz (ivan.cernicharo@bsc.es)             
#

import pandas as pd
import cdsapi
import time
import datetime
import os

def downloader(dataset, form, download_file, 
                url = None, key = None,
                logpath = None, user = 'user'):

    #This function uses the cdsapi.Client().retrieve() function to download any specified dataset from the CDS while storing key features of the download
    #in a log file (in csv format) for latter analysis. This log file is stored in the folder specified by logpath. Download features related with a
    # download request for same dataset type and a same user will be added in a same log file. 

    #dataset: same first input as in the cdsapi.Client().retrieve(). It specifies the name of the dataset to be downloaded
    #form: same second input as in the cdsapi.Client().retrieve(). It specifies all the corresponding detail of the download
    #download_file: same third input as in the cdsapi.Client().retrieve(). It specifies the path and file name of the corresponding download file

    #url: url used by the cdsapi.Client(url, key)
    #key: user key used by the cdsapi.Client(url, key)
    
    #logpath: path for the log file of the download features. By the fault it is '/data/logs_cds_download/'. If this folder does not exist it is
    #created.
    #user: the name of the user to be added to the log file.

    #Definition of logpath in case is not specified
    if logpath is None:
        logpath = '/data/logs_cds_download/'
        if not os.path.exists(logpath):
            os.makedirs(logpath)

    #Date and time of the request
    dt_request = datetime.datetime.now()
    time0 = time.time()
    
    #Start the cdsapi download request
    download_error = None
    try:
        c = cdsapi.Client(url = url, key = key)
        c.retrieve(dataset,
                    form,
                    download_file)

        #size of the download file
        file_size = round(os.stat(download_file).st_size/1000./1000.,1)
        
    #if the download fails
    except Exception as e:
	print(e)
        file_size = None
        
        #keep the download error
        download_error = e

    #keep the download time
    time1 = time.time()
    dtime_download = (time1 - time0)/60

    #Generate all the download features
    log_dict = form.copy()
    for id in log_dict.keys():
        log_dict[id] = str(log_dict[id])
    log_dict['dataset_name'] = dataset
    log_dict['file_size'] = file_size
    log_dict['download_error'] = download_error
    log_dict['datetime_request'] = dt_request.strftime('%m%d%y-%H%M%S')
    log_dict['weekday'] = dt_request.weekday()
    log_dict['download_time'] = dtime_download
    log_dict['user'] = user

    #Generate the log file as a csv file
    logfile = dataset + '.csv'
    logpathfile = logpath + logfile
    log_df = pd.DataFrame(log_dict, index=[0])
    log_df = log_df[sorted(log_df.columns)]
    
    #Add request features to an already log file or create a new one otherwise
    if os.path.exists(logpathfile):
        with open(logpathfile, 'a') as f:
            log_df.to_csv(f, index = False, header = False)
    else:
        log_df.to_csv(logpathfile, index = False)
    
