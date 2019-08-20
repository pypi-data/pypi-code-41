import hashlib
import ntpath
import json
import re
import logging as log
import os
import psutil
from concurrent import futures
from math import ceil


def cpu_count():
    return 2 * psutil.cpu_count() - 1


def parallel(func, list, *args, **kwrags):
    MAX_WORKERS = cpu_count()
    tasks = []
    results = []
    with futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        s = ceil(len(list) / MAX_WORKERS)
        for i in range(MAX_WORKERS):
            start = i * s
            end = (i + 1) * s
            if end >= len(list):
                end = len(list)
            tasks.append(executor.submit(func, list[start:end], *args, **kwrags))
    for future in futures.as_completed(tasks):
        results.append(future.result())
    return results


def get_fileszie(path):
    return os.stat(path).st_size


def compute_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return str(hash_md5.hexdigest())


def get_filename(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def turn_metadata(metadata):
    s = json.dumps(metadata)
    regex = r'(?<!:)"(\S*?)":'
    strip_s = re.sub(regex, "\\1:", s)
    return strip_s


def check_protoype(protoype, dictdata):
    if set(protoype) - set(dictdata):
        log.info({"your metadata should catains all protoype kyes: ": protoype})
        raise Exception({"your metadata should catains all protoype kyes: ": protoype})
    return True
