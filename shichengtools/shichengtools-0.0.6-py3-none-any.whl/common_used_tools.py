#!/usr/bin/python
# -*- coding:utf-8 -*-
# @Author  : Shi Cheng
# @Time    : 2019/7/20 20:52
import pickle
import numpy as np
import os
from functools import wraps
import multiprocessing
import h5py
import time
import urllib
import imgspy
import asyncio
import fastimage


def func_time(func):
    def inner(*args,**kw):
        start_time = time.time()
        func(*args,**kw)
        end_time = time.time()
        print('函数运行时间为：',end_time-start_time,'s')
    return inner

def auto_set_processing_number(worker):
    @wraps(worker)
    def decorated(*args, **kwargs):
        if 'job_id' in kwargs.keys() :
            job_id =  kwargs.pop('job_id')
        else :
            raise Exception("The process job_id must be included!")
        if 'job_queue' in kwargs.keys() :
            job_queue=  kwargs.pop('job_queue')
        else :
            raise Exception("The process job_queue must be included!")
        worker_ans = worker(*args, **kwargs)
        print('Process:' + str(job_id), ' work down!')
        ans_dict= {'job_id':job_id,
                    'worker_ans':worker_ans
        }
        job_queue.put(ans_dict)
    return decorated

def auto_parallel(worker):

    # 一定要有Job_list
    @wraps(worker)
    def decorated(*args, **kwargs):
        joblist = kwargs['job_list']
        processing_number = kwargs['processing_number'] if 'processing_number'in kwargs.keys() else os.cpu_count()
        keep_order = kwargs['keep_order'] if 'keep_order'in kwargs.keys() else True
        job_data = kwargs['job_data'] if 'job_data'in kwargs.keys() else None
        job_queue = multiprocessing.Queue()

        # 切分数据
        job_split = np.linspace(start=0, stop=len(joblist), num=processing_number + 1, endpoint=True, dtype=np.int16)
        processing_list = []
        for i in range(processing_number):
            print("job-", i, ':', job_split[i], ',', job_split[i + 1])

            ProcessKwargs = {'job_id':i,
            'job_queue':job_queue,
            'keep_order':keep_order}

            p = multiprocessing.Process(target=worker, args=(joblist[job_split[i]:job_split[i + 1]],job_data),kwargs=ProcessKwargs)
            p.start()
            processing_list.append(p)

        # 获取不同进程的处理结果
        all_ans_dict = dict()
        for i in range(processing_number):
            ans_dict = job_queue.get()
            job_id = ans_dict['job_id']
            worker_ans = ans_dict['worker_ans']
            all_ans_dict[job_id] = worker_ans
            print('Main: got data from Process:' + str(job_id), ' down!')

        # 按顺序合并结果(全部默认)
        final_dict=dict()
        final_List=[]
        if keep_order or True:
            all_ans = []
            for i in range(processing_number):
                if isinstance(all_ans_dict[i], list):
                    final_dict.update(all_ans_dict[i])
                elif isinstance(all_ans_dict[i], dict):
                    final_List+=all_ans_dict[i]
                elif isinstance(all_ans_dict[i], np.ndarray):
                    final_List += all_ans_dict[i]
        final_ans =None
        if isinstance(all_ans_dict[0], list):
            final_ans = final_dict
        elif isinstance(all_ans_dict[0], dict):
            final_ans =  final_List
        elif isinstance(all_ans_dict[0], np.ndarray):
            final_ans = np.vstack(final_List)
        return final_ans
    return decorated

def job_split_for_test(job_list ,split_number,test_size=200,with_id =False):
    split_job_list = []
    if isinstance(job_list , list):
        job_length = test_size
        job_section = np.linspace(start=0, stop=job_length, num= split_number + 1, endpoint=True, dtype=np.int16)
        if with_id:
            split_job_list = [ (i ,job_list[job_section[i]:job_section[i + 1]] )    for i in   range(split_number)]
        else:
            split_job_list = [job_list[job_section[i]:job_section[i + 1]]   for i in   range(split_number)]
    elif isinstance(job_list , dict):
        sub_keys_set_List = job_split_for_test(list(job_list.keys()),split_number=split_number,test_size=test_size,with_id =False)
        for i,sub_keys_set in enumerate(sub_keys_set_List):
            if with_id:
                split_job_list.append((i,dict(zip(sub_keys_set,[job_list[k] for k in sub_keys_set]))))
            else:
                split_job_list.append(dict(zip(sub_keys_set,[job_list[k] for k in sub_keys_set])))
    elif isinstance(job_list , np.ndarray):
        job_length = np.min(job_list.shape[0],test_size)
        job_section = np.linspace(start=0, stop=job_length, num= split_number + 1, endpoint=True, dtype=np.int16)
        if with_id:
            split_job_list = [(i,job_list[job_section[i]:job_section[i + 1]]) for i in range(split_number)]
        else:
            split_job_list = [job_list[job_section[i]:job_section[i + 1]] for i in   range(split_number)]
    else:
        raise Exception("Not list or dict or np.ndarray!")
    return split_job_list

def job_split(job_list ,split_number,with_id =False):
    split_job_list = []
    if isinstance(job_list , list):
        job_length = len(job_list)
        base_task = job_length //split_number
        increment_task = job_length - base_task * split_number
        start_n = 0
        end_n = 0
        for i in range(split_number):
            if(i < increment_task):
                start_n = end_n
                end_n = start_n + base_task + 1
            else:
                start_n = end_n
                end_n = start_n + base_task
                if with_id:
                    split_job_list.append((i,job_list[start_n:end_n]))
                else:
                    split_job_list.append(job_list[start_n:end_n])

    elif isinstance(job_list , dict):
        sub_keys_set_List = job_split(list(job_list.keys()), split_number,with_id =False)
        for i,sub_keys_set in enumerate(sub_keys_set_List):
            if with_id:
                split_job_list.append((i,dict(zip(sub_keys_set,[job_list[k] for k in sub_keys_set]))))
            else:
                split_job_list.append(dict(zip(sub_keys_set,[job_list[k] for k in sub_keys_set])))
    elif isinstance(job_list , np.ndarray):
        job_length = job_list.shape[0]
        job_section = np.linspace(start=0, stop=job_length, num= split_number + 1, endpoint=True, dtype=np.int16)
        if with_id:
            split_job_list = [(i,job_list[job_section[i]:job_section[i + 1]]) for i in range(split_number)]
        else:
            split_job_list = [job_list[job_section[i]:job_section[i + 1]] for i in   range(split_number)]
    else:
        raise Exception("Not list or dict or np.ndarray!")
    return split_job_list

def read_H5(path,load_into_memory =False):
    f = h5py.File(path, 'r')
    if load_into_memory:
        data = dict()
        for k, v in f.items():
            data[k] = v
        f.close()
        return data
    else:
        # 最后一定要关闭文件
        return f

def write_H5(path, data):
    f = h5py.File(path, 'w')
    for k,v in  data.items():
        f[k] = v
    f.close()

def read_pickle(path):
    f = open(path, "rb")
    data = pickle.load(f)
    f.close()
    return data

def write_pickle(path, data):
    f = open(path, 'wb')
    pickle.dump(data, f)
    f.close()

def show_in_MD(score_list, imgList, columns):
    showMD = ''
    for i in range(len(imgList)):
        showMD += "### "
        for j in range(len(score_list[i])):
            showMD += columns[j] + ':' + str(round(float(score_list[i][j]), 2))
            if (j != len(score_list[i]) - 1):
                showMD += " | "
            else:
                # showMD += "\n ![模糊图片](file:///" + imgList[i] + ")\n"
                showMD += "\n ![模糊图片](" + imgList[i] + ")\n"
    return showMD

def write_md(data, path):
    f = open(path, 'w', encoding='utf-8')
    f.write(data)
    f.close()

def save_md(df, columns, md_Home, top_k):
    # 循环排序，不排第一列用户打分
    for column_name in columns[1:]:
        temp1 = df.sort_values(by=column_name, ascending=False)
        tmp_imgList = temp1.index
        # 需要按行抽取打分生成md文件，这里按列取，转置
        score_list = np.array([temp1[colname] for colname in columns]).T
        tmp_imgList = tmp_imgList[0:top_k]
        score_list = score_list[:, 0:top_k]
        showMD = show_in_MD(score_list, tmp_imgList, columns)
        MD_path = md_Home + str(column_name) + '_high.md'
        write_md(showMD, MD_path)

        temp2 = df.sort_values(by=column_name, ascending=True)
        tmp_imgList = temp2.index
        score_list = np.array([temp2[colname] for colname in columns]).T
        tmp_imgList = tmp_imgList[0:top_k]
        score_list = score_list[:, 0:top_k]
        showMD = show_in_MD(score_list, tmp_imgList, columns)
        MD_path = md_Home + str(column_name) + '_low.md'
        write_md(showMD, MD_path)

def get_all_file_score_List(file_path):
    job_list = []
    score_list = []
    for root_path, dir_name_list, file_name_list in os.walk(file_path):
        for file_name in file_name_list:
            job_list.append(root_path + file_name)
            score_list.append(float(file_name.split('_')[1]))
    return job_list, score_list

def get_all_file_List(file_path):
    job_list = []
    for root_path, dir_name_list, file_name_list in os.walk(file_path):
        for file_name in file_name_list:
            job_list.append(root_path + file_name)
    return job_list

def frequency_count(target):
    return collections.Counter(target)


# 返回图片文件类型，图片尺寸
def get_img_type_size(url = 'https://pic.tujia.com/upload/qualifiedpics/day_181001/201810012052016276.jpg'):

    # loop = asyncio.get_event_loop()
    # result = loop.run_until_complete(fastimage.detect.get_type(url))
    # print("Type:", result)

    # fix
        # with aiohttp.Timeout(timeout):
        #  with async_timeout.timeout(timeout):

    info_dict = imgspy.info(url)
    # Out: {'type': 'jpg', 'width': 4000, 'height': 2666}
    return info_dict['type'],info_dict['width'],info_dict['height']

# 返回字节数
def get_url_file_size(url = "https://pic.tujia.com/upload/qualifiedpics/day_181001/201810012052016276.jpg"):
    site = urllib.request.urlopen(url)
    fileSize = dict(site.getheaders())['Content-Length']
    site.close()
    return fileSize


def load_txt_data(pathStr):
    f = open(pathStr, 'r')
    records = f.readlines()
    f.close()
    return records

def get_all_filepath(dir_path):
    for root_path, dirnames,filenames in os.walk(dir_path):
        return [root_path + filename for filename in filenames]

def load_test_csv(csv_path):
    return pd.read_csv(csv_path, encoding='utf-8',engine='python')

def load_big_csv(csv_path,chunkSize = 10000000,delimiter='\t'):
    chunks = []
    reader = pd.read_csv(csv_path,delimiter=delimiter,iterator=True)
    while True:
        try:
            chunk = reader.get_chunk(chunkSize)
            chunks.append(chunk)
        except StopIteration:
            print ("Iteration is stopped.")
            break
    df = pd.concat(chunks, ignore_index=True)
    return df
