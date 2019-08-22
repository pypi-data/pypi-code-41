# -*- coding: utf-8 -*-

import argparse
import logging
import os
import pickle
import sys
import time
from logging import handlers

from torrent import torrent
from tracker_list import get_tracker_list, tracker_list_url

cache_path = 'tracker.dat'
log_path = 'AutoTrackers.log'
now_time = time.strftime('%Y%m%d')
loger = logging.getLogger('AutoTrackers')
loger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(lineno)d - %(message)s')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
loger.addHandler(stream_handler)
file_handler = logging.handlers.TimedRotatingFileHandler(log_path, 'd', 1, 3, 'utf-8')
file_handler.suffix = '%Y-%m-%d.log'
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
loger.addHandler(file_handler)


def auto_get_tracker_list_from_data(key):
    if file_is_normal(cache_path):
        f = open(cache_path, 'rb')
        try:
            tracker_data = pickle.load(f)
        except EOFError:
            loger.error('无法解析 ' + cache_path + ' 中的数据')
            f.close()
            tracker_data = None
    else:
        if recreate_file(cache_path):
            tracker_data = None
        else:
            loger.error(cache_path + ' 文件创建失败')
            sys.exit()
    if tracker_data_is_vaild(tracker_data, key):
        s = tracker_data[key]
        return s[1]

    loger.warning('Tracker 数据有问题,准备重新下载')

    try:
        s = get_tracker_list(tracker_list_url[key])
    except:
        loger.error('Tracker List 数据下载失败')
        s = []

    t = int(now_time)
    v = (t, s)

    if not isinstance(tracker_data, dict):
        tracker_data = {}
    tracker_data[key] = v

    with open(cache_path, 'wb') as f:
        pickle.dump(tracker_data, f)
        loger.info(cache_path + ' 文件中的数据已更新')

    return s


def recreate_file(file):
    if not os.path.exists(file):
        open(file, 'wb')
        return True

    if os.path.isfile(file):
        os.remove(file)
        open(file, 'wb')
        return True

    return False


def tracker_data_is_vaild(data, key):
    if not data:
        loger.warning('Tracker 数据的数据为空')
        return False

    if key not in data.keys():
        loger.warning('Tracker 数据缺少 ' + key + ' 类型的数据')
        return False

    v = data.get(key)
    if not isinstance(v, tuple):
        loger.warning('Tracker 中' + key + '的数据为空')
        return False

    if len(v) != 2:
        loger.warning('Tracker 中' + key + '的数据有错误')
        return False

    if not isinstance(v[0], int):
        loger.warning('Tracker 中' + key + '的数据有错误')
        return False

    if v[0] < int(now_time):
        loger.warning('Tracker 中' + key + '的数据过期了')
        return False

    if not isinstance(v[1], list):
        loger.warning('Tracker 中' + key + '的数据有错误')
        return False

    return True


def file_is_normal(file):
    if not os.path.exists(file):
        loger.error('文件不存在,文件为：' + file)
        return False

    if not os.path.isfile(file):
        loger.error('文件不存在,文件为：' + file)
        return False

    if not os.access(file, os.R_OK):
        loger.error('缺少文件读取权限,文件为：' + file)
        return False

    if not os.access(file, os.W_OK):
        loger.error('缺少文件写入权限,文件为：' + file)
        return False

    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='torrent 文件路径')
    parser.add_argument('-type', help='添加哪种类型的 tracker，默认为 best',
                        choices=('best', 'all', 'udp', 'http', 'https', 'ws', 'best_ip', 'all_ip'), default='best')
    parser.add_argument('-rt', help='保留原有的 tracker 服务器地址，0：不保留，1：保留，默认为 1', choices=(0, 1), default=1, type=int)
    parser.add_argument('-o', help='文件输出路，默认为直接覆盖原文件')

    args = parser.parse_args()
    if not file_is_normal(args.file):
        sys.exit()

    v = auto_get_tracker_list_from_data(args.type)
    t = torrent(args.file)
    t.add_tracker(v, args.rt)
    t.save_torrent(args.o if args.o else args.file)
