#!/usr/bin/env python
#-*-coding: utf-8 -*-

import os
import sys
import json
import traceback
import urllib2
import time
from subprocess import Popen, PIPE
from kdbase.log import logger

hadoop_bin_path = '/opt/hadoop-3.1.2/bin'
kerberos_file = os.getenv('KRB_FILE')
user = os.getenv('KRB_USER')

def create_file(hdfs_path, data, overwrite=True):
    file_name = hdfs_path.split('/')[-1]
    t = int(time.time())
    file_name = '%s_%s' % (file_name, t)
    open(file_name, 'w').write(data)
    cmd = '%s/kdhadoop fs -put -f %s %s' % (hadoop_bin_path, file_name, hdfs_path)
    logger().info('create file cmd is [%s]', cmd)
    res = os.system(cmd)
    if res != 0:
        return False
    rm_cmd = 'rm %s' % file_name
    logger().info('rm file cmd is [%s]', rm_cmd)
    res = os.system(rm_cmd)
    return res == 0

def rename(hdfs_path, rename_path):
    cmd = '%s/kdhadoop fs -mv %s %s' % (hadoop_bin_path, hdfs_path, rename_path)
    logger().info('rename cmd is [%s]', cmd)
    res = os.system(cmd)
    return res == 0

def get_file_checksum(hdfs_path):
    cmd = '%s/kdhadoop fs -checksum %s' % (hadoop_bin_path, hdfs_path)
    logger().info('checksum cmd is [%s]', cmd)
    p = Popen(cmd, stdout=PIPE, shell=True)
    p.wait()
    if p.returncode == 0:
        checksum = p.stdout.read().split()[-1].strip()
        return checksum
    else:
        logger().error('get_file_checksum fail, hdfs path is %s', hdfs_path)
        raise ValueError

def get_content_sum(hdfs_path):
    cmd = '%s/kdhadoop fs -du -s %s' % (hadoop_bin_path, hdfs_path)
    logger().info('get_content_sum cmd is [%s]', cmd)
    p = Popen(cmd, stdout=PIPE, shell=True)
    p.wait()
    if p.returncode == 0:
        length = p.stdout.read().split()[0].strip()
        content = {}
        content['length'] = int(length)
        return content
    else:
        logger().error('get_content_sum fail, hdfs path is %s', hdfs_path)
        raise ValueError

def exists(hdfs_path):
    cmd = '%s/kdhadoop fs -test -e %s' % (hadoop_bin_path, hdfs_path)
    code = os.system(cmd)
    return code == 0

def listdir(hdfs_path):
    cmd = '%s/kdhadoop fs -ls %s' % (hadoop_bin_path, hdfs_path)
    ls_result = os.popen(cmd).read().strip().split('\n')
    ls_result = map(lambda x:x.split(' ')[-1].split('/')[-1], ls_result)
    return ls_result[1:]

def listdir_v2(hdfs_path):
    cmd = '%s/kdhadoop fs -ls %s' % (hadoop_bin_path, hdfs_path)
    ls_result = os.popen(cmd).read().strip().split('\n')
    ls_result = map(lambda x:x.split(' ')[-1], ls_result)
    return ls_result[1:]

def mkdirs(hdfs_path):
    cmd = '%s/kdhadoop fs -mkdir -p %s' % (hadoop_bin_path, hdfs_path)
    code = os.system(cmd)
    logger().info('mkdir hdfs_path[%s] result code:%s' % (hdfs_path, code))
    if code == 0:
        return True
    logger().error('mkdir hdfs_path[%s] fail' % hdfs_path)
    return False

def delete(hdfs_path):
    res = False
    if exists(hdfs_path):
        cmd = '%s/kdhadoop fs -rm -r %s' % (hadoop_bin_path, hdfs_path)
        code = os.system(cmd)
        logger().info('delete hdfs_path[%s] result code:%s' % (hdfs_path, code))
        res = code == 0
    else:
        logger().info('del target file[%s] not exists' % hdfs_path)
        return True
    return res

def set_xattr(path, xattr_name, xattr_value, flag=None):
    if exists(path):
        cmd = '%s/kdhadoop fs -setfattr -n %s -v %s %s' % (hadoop_bin_path,
                xattr_name, xattr_value, path)
        code = os.system(cmd)
        logger().info('setfattr path[%s], name[%s], value[%s], the result '
                'code:%s' % (path, xattr_name, xattr_value, code))
        return code == 0
    else:
        logger().info('setfattr target file[%s] not exists' % path)
        return False

def get_xattr(path, xattr_name):
    if not exists(path):
        logger().info('hdfs_path:%s not exist' % path)
        return None
    cmd = '%s/kdhadoop fs -getfattr -n %s %s' % (hadoop_bin_path, xattr_name,
            path)
    lines = os.popen(cmd).readlines()
    if len(lines) < 2:
        return None
    line = lines[1].strip()
    res = line.split('=')[1].replace('"', '')
    return res

def download(hdfs_path, local_path, retry_time = 3):
    if not exists(hdfs_path):
        logger().error('hdfs_path:%s not exists' % (hdfs_path))
        return False
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    cmd = '%s/kdhadoop fs -get -f %s %s' % (hadoop_bin_path, hdfs_path,
            local_path)
    for time in range(retry_time):
        code = os.system(cmd)
        logger().info('download dir local_path:%s, hdfs_path:%s, '
                'result code:%s, retry %s time', local_path, hdfs_path, code, time)
        if code == 0:
            return True
    return False

def download_dir(hdfs_path, local_path):
    return download(hdfs_path, local_path)

def download_sign(hdfs_path, local_path, sign):
    if not exists(hdfs_path):
        logger().error('hdfs_path:%s not exists' % (hdfs_path))
        return False
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    file_name = hdfs_path.split('/')[-1] + '_%s' % sign
    cmd = '%s/kdhadoop fs -get -f %s %s' % (hadoop_bin_path, hdfs_path,
            os.path.join(local_path, file_name))
    print cmd
    for time in range(3):
        code = os.system(cmd)
        logger().info(('download sign local_path:%s, hdfs_path:%s, sign:%s, '
            'result code:%s'), local_path, hdfs_path, sign, code)
        if code == 0:
            return True
    return False

def download_for_auto(hdfs_path, local_path):
    if not exists(hdfs_path):
        logger().error('hdfs_path:%s not exists' % (hdfs_path))
        return False
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    file_name = hdfs_path.split('/')[-1] + '_test'
    cmd = '%s/kdhadoop fs -get -f %s %s' % (hadoop_bin_path, hdfs_path,
            os.path.join(local_path, file_name))
    for time in range(3):
        code = os.system(cmd)
        logger().info(('download for auto local_path:%s, hdfs_path:%s, '
            'result code:%s'), local_path, hdfs_path, code)
        if code == 0:
            return True
    return False

def upload(local_path, hdfs_path, retry_time = 3):
    if not os.path.exists(local_path):
        logger().error('local_path:%s not exists' % (local_path))
        return False
    if not exists(hdfs_path):
        mkdirs(hdfs_path)
    cmd = '%s/kdhadoop fs -put -f %s %s' % (hadoop_bin_path, local_path,
            hdfs_path)
    for time in range(retry_time):
        code = os.system(cmd)
        logger().info('upload local_path:%s, hdfs_path:%s, '
                'result code:%s', local_path, hdfs_path, code)
        if code == 0:
            return True
    return False

def upload_dir(local_path, hdfs_path):
    return upload(local_path, hdfs_path)

def get_job_id(job_name):
    def filter_app(x):
        target_name = x['name']
        return target_name == job_name
    apps_url = config.GET_CONF('hadoop', 'yarn_apps_url')
    response = urllib2.urlopen(apps_url)
    data = response.read()
    data = json.loads(data)
    apps = data['apps']['app']
    target_apps = filter(filter_app, apps)
    if not target_apps:
        return None
    target_apps = sorted(target_apps, key=lambda x:x['startedTime'],
            reverse=True)
    target_app = target_apps[0]
    job_id = 'job' + target_app['id'].split('application_')[1]
    return job_id

def get_job_progress(job_name):
    def filter_app(x):
        target_name = x['name']
        return target_name == job_name
    apps_url = config.GET_CONF('hadoop', 'yarn_apps_url')
    response = urllib2.urlopen(apps_url)
    data = response.read()
    data = json.loads(data)
    apps = data['apps']['app']
    target_apps = filter(filter_app, apps)
    progress = 0
    if target_apps:
        target_apps = sorted(target_apps, key=lambda x:x['startedTime'],
                reverse=True)
        target_app = target_apps[0]
        progress = int(target_app['progress'])
    logger().info('mr_job_name: %s, mr_progress:%s' % (job_name, progress))
    return progress


if __name__ == '__main__':
    #print exists('/user/hwl/copy_data_result')
    #print exists('/user/hwl')
    #print listdir('/tmp')
    #print listdir_v2('/tmp')
    print creat_file('/user/hwl.test_thc', '123')
    print rename('/user/hwl.test_thc', '/user/hwl.test_thc123')
    print get_file_checksum('/user/hwl.test_thc123')
    print get_content_sum('/user/hwl.test_thc123')
    #print mkdirs('/user/hwl/hdfs_test/a/b')
    #print set_xattr('/user/hwl', 'user.time', '123', True)
    #print download_dir_v2('/user/hwl/copy_data_result', '/home/hadoop/hwl/model/123')
    #xattr_name = 'user.atime'
    #path = '/user/hwl'
    #cmd = '%s/hadoop fs -getfattr -n %s %s' % (hadoop_bin_path, xattr_name,
    #        path)
    #res = os.popen(cmd).readlines()
    #print res
    #print 'use function'
    #print get_xattr(path, xattr_name)
    #print set_xattr(path,xattr_name,'456','')
    #print get_xattr(path, xattr_name)
    #print download_for_auto('/user/hwl/sample.txt', '.')
    #print download_sign('/user/hwl/sample.txt', '.', 'sign')
