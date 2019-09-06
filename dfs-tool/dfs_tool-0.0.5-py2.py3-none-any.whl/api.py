from __future__ import print_function
from pywebhdfs.errors import FileNotFound, PyWebHdfsException
from datetime import datetime
import os
import sys
import json
from .tools import get_filename, permission_to_str, fail, cut_tail_slash, add_tail_slash, get_config
import subprocess
from fnmatch import fnmatch

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__DOWNLOAD_CHUNK_SIZE = 1024*1024
__UPLOAD_CHUNK_SIZE   = 1024*1024

def __mkdir(local_path):
    try:
        os.mkdir(local_path)
    except FileExistsError:
        pass

def __get_files(hdfs, remote_filename):
    try:
        return hdfs.list_dir(remote_filename)["FileStatuses"]["FileStatus"]
    except PyWebHdfsException as e:
        msg = json.loads(e.msg.decode("utf-8"))
        if msg.get("RemoteException", {}).get("exception") == "AccessControlException":
            return []
        else:
            raise


def dfs_ls(hdfs, remote_filename, recursive, indent=''):
    r = hdfs.get_file_dir_status(remote_filename)

    if r["FileStatus"]["type"] == "FILE":
        remote_filename = cut_tail_slash(remote_filename)
        r["FileStatus"]["pathSuffix"] = get_filename(remote_filename)
        result = [r["FileStatus"]]
    else:
        try:
            result = hdfs.list_dir(remote_filename)["FileStatuses"]["FileStatus"]
        except PyWebHdfsException as e:
            msg = json.loads(e.msg.decode("utf-8"))
            if msg.get("RemoteException", {}).get("exception") == "AccessControlException":
                return
            else:
                raise

    max_namelen = 0
    max_ownerlen = 0
    max_grouplen = 0
    for file_summary in result:
        max_namelen = max(max_namelen, len(file_summary["pathSuffix"]))
        max_ownerlen = max(max_ownerlen, len(file_summary["owner"]))
        max_grouplen = max(max_grouplen, len(file_summary["group"]))

    fmt = '{{permission_str}} {{owner:{}}} {{group:{}}} {{length:16}} {{modification_time:10}} {{filename:{}}}'.format(
        max_ownerlen, max_grouplen, max_namelen)
    for file_summary in result:
        modification_time = datetime.fromtimestamp(file_summary["modificationTime"] / 1000).strftime(
            "%Y-%m-%d %H:%M:%S")

        if recursive:
            print("{}{}".format(indent, file_summary["pathSuffix"]))
            if file_summary["type"] == "DIRECTORY":
                dfs_ls(
                    hdfs, 
                    "{}/{}".format(remote_filename, file_summary["pathSuffix"]),
                    True,
                    indent + '    '
                )
        else:
            print(
                fmt.format(
                    permission_str=permission_to_str(file_summary),
                    owner=file_summary["owner"],
                    group=file_summary["group"],
                    filename=file_summary["pathSuffix"],
                    length=file_summary["length"],
                    modification_time=modification_time,
                )
            )

def _download_internal(
        hdfs,
        remote_filename,
        local_filename,
        local_file_handle=None,
        opened_in_binary_moode=False
):
    chunk_size = get_config().get("download_chunk_size", __DOWNLOAD_CHUNK_SIZE)
    # if caller supply local_file_handle, then opened_in_binary_moode tells
    # if the file is opened in text mode or binary mode
    if local_filename is None and local_file_handle is None:
        fail("You must provide local_filename or local_file_handle")

    def do_copy(f, opened_in_binary_moode):
        offset = 0
        while True:
            b = hdfs.read_file(
                remote_filename,
                offset=offset,
                length=chunk_size
            )
            if len(b) > 0:
                if opened_in_binary_moode:
                    f.write(b)
                else:
                    f.buffer.write(b)
            if len(b) < chunk_size:
                break
            offset += len(b)


    if local_file_handle is None:
        with open(local_filename, "wb") as f:
            do_copy(f, True)
    else:
        do_copy(local_file_handle, opened_in_binary_moode)

def dfs_download(hdfs, remote_filename, local_filename, recursive):
    remote_filename = cut_tail_slash(remote_filename)
    # local_filename = os.path.join(local_filename, get_filename(remote_filename))
    
    try:
        r = hdfs.get_file_dir_status(remote_filename)
        if r["FileStatus"]["type"] not in ['DIRECTORY', 'FILE']:
            print("skipped, {} is not a file, nor a directory".format(remote_filename))
            # we only copy files or directories
            return
        if r["FileStatus"]["type"] == "DIRECTORY":
            if not recursive:
                fail("{} is a directory, specify -R if you want to download directory".format(remote_filename))
                return
            subprocess.call(["mkdir", "-p", local_filename])
            for file_summary in __get_files(hdfs, remote_filename):
                dfs_download(
                    hdfs, 
                    os.path.join(remote_filename, file_summary["pathSuffix"]),
                    os.path.join(local_filename,  file_summary["pathSuffix"]),
                    True
                )
            return
        else:
            print("download: {}".format(remote_filename))
            _download_internal(hdfs, remote_filename, local_filename)
    except FileNotFound:
        fail("File not found: {}".format(remote_filename))

def dfs_cat(hdfs, remote_filename):
    _download_internal(
        hdfs, 
        remote_filename, 
        None, 
        local_file_handle=sys.stdout, 
        opened_in_binary_moode=False
    )

def dfs_mkdir(hdfs, remote_filename):
    try:
        r = hdfs.get_file_dir_status(remote_filename)
        if r["FileStatus"]["type"] == "FILE":
            fail("File with the same name exists")
        if r["FileStatus"]["type"] == "DIRECTORY":
            # shortcut, since the directory already exist
            return
    except FileNotFound:
        pass
    hdfs.make_dir(remote_filename)

def dfs_rm(hdfs, remote_filename, recursive, match):
    if not match:
        # remote_filename could be either a directory or file
        print("Delete {}".format(remote_filename))
        hdfs.delete_file_dir(remote_filename, recursive=recursive)
        return
    
    pattern = get_filename(remote_filename)
    remote_basename = remote_filename[:-len(pattern)-1]

    r = hdfs.get_file_dir_status(remote_basename)
    if r["FileStatus"]["type"] != "DIRECTORY":
        fail("{} is not a directory".format(remote_basename))
    result = hdfs.list_dir(remote_basename)["FileStatuses"]["FileStatus"]
    print("Deleting files in {} using pattern \"{}\"".format(remote_basename, pattern))
    for file_summary in result:
        if fnmatch(file_summary["pathSuffix"], pattern):
            remote_filename_to_del = os.path.join(remote_basename, file_summary["pathSuffix"])
            print("Delete {}".format(remote_filename_to_del))
            hdfs.delete_file_dir(remote_filename_to_del, recursive=recursive)


# When force is True, if file already exist on the target, it will remote it
def dfs_upload(hdfs, local_filename, remote_filename, force, recursive):
    local_filename = cut_tail_slash(local_filename)
    # remote_filename could be a path name

    isfile = os.path.isfile(local_filename)
    isdir  = os.path.isdir(local_filename)

    if not isfile and not isdir:
        print("skipped, {} is not a file, nor a directory".format(remote_filename))
        return
    
    if isdir:
        print("create directory in HDFS: {}".format(remote_filename))
        hdfs.make_dir(remote_filename)
        for filename in os.listdir(local_filename):
            dfs_upload(
                hdfs, 
                os.path.join(local_filename, filename),
                os.path.join(remote_filename, filename),
                force,
                recursive
            )
        return

    print("Upload to {}".format(remote_filename))
    # if remote_filename is a path, file gets copied into that directory
    try:
        r = hdfs.get_file_dir_status(remote_filename)
        if r["FileStatus"]["type"] in ["FILE", "DIRECTORY"]:
            if force:
                # let's delete it since we are going to replace it
                hdfs.delete_file_dir(remote_filename, recursive=True)
            else:
                fail("{} already exist, use -F if you want to overwrite".format(remote_filename))
    except FileNotFound:
        # it is ok if the remote file does not exist
        # how the caller created the directory first
        pass

    hdfs.create_file(remote_filename, b'')
    chunk_size = get_config().get("upload_chunk_size", __UPLOAD_CHUNK_SIZE)
    with open(local_filename, "rb") as f:
        while True:
            b = f.read(chunk_size)
            if len(b) > 0:
                hdfs.append_file(remote_filename, b)
            if len(b) < chunk_size:
                break

def dfs_move(hdfs, source_filename, destination_filename):
    r = hdfs.rename_file_dir(source_filename, destination_filename)
    if not r["boolean"]:
        fail("Move file failed")
