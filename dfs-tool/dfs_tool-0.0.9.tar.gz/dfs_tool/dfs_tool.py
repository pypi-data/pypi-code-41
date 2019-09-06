# -*- coding: UTF-8 -*-
from __future__ import print_function
import sys
import os
from .api import dfs_ls, dfs_download, dfs_cat, dfs_mkdir, dfs_rm, dfs_upload, dfs_move
from .tools import fail, run_command, parse_args, get_hdfs

def print_usage():
    print("dfs_tool -- A DFS tool")
    print("dfs_tool ls [-R]          <remote_path>                            -- list directory or file")
    print("dfs_tool download [-R]    <remote_filename> <local_path>           -- download file")
    print("dfs_tool cat              <remote_filename>                        -- cat a file")
    print("dfs_tool mkdir            <remote_dir_name>                        -- make a directory")
    print("dfs_tool rm [-RM]         <remote_path>                            -- remove a file or directory")
    print("dfs_tool upload [-R] [-F] <local_filename> <remote_path>           -- upload file")
    print("dfs_tool mv               <source_location> <destination_location> -- move file or directory")

def do_ls(hdfs, args, options):
    if len(args) < 2:
        fail("Missing path", os.EX_USAGE)
    recursive = "R" in options
    dfs_ls(hdfs, args[1], recursive)

def do_download(hdfs, args, options):
    if len(args) < 3:
        fail("Missing remote filename or local filename", os.EX_USAGE)
    recursive = "R" in options
    dfs_download(hdfs, args[1], args[2], recursive)

def do_cat(hdfs, args, options):
    if len(args) < 2:
        fail("Missing remote filename", os.EX_USAGE)
    dfs_cat(hdfs, args[1])

def do_mkdir(hdfs, args, options):
    if len(args) < 2:
        fail("Missing remote dir name", os.EX_USAGE)
    dfs_mkdir(hdfs, args[1])

def do_rm(hdfs, args, options):
    if len(args) < 2:
        fail("Missing remote dir name or file name", os.EX_USAGE)
    recursive = "R" in options
    match = "M" in options
    dfs_rm(hdfs, args[1], recursive, match)

def do_upload(hdfs, args, options):
    if len(args) < 3:
        fail("Missing remote filename or local filename", os.EX_USAGE)
    force = "F" in options
    recursive = "R" in options
    dfs_upload(hdfs, args[1], args[2], force, recursive)

def do_move(hdfs, args, options):
    if len(args) < 3:
        fail("Missing source or destination name", os.EX_USAGE)
    dfs_move(hdfs, args[1], args[2])

def main():
    args, options = parse_args()

    if len(args) == 0:
        print_usage()
        return

    hdfs = get_hdfs()

    if args[0] == "ls":
        do_ls(hdfs, args, options)
        return

    if args[0] == "download":
        do_download(hdfs, args, options)
        return

    if args[0] == "cat":
        do_cat(hdfs, args, options)
        return

    if args[0] == "mkdir":
        do_mkdir(hdfs, args, options)
        return

    if args[0] == "rm":
        do_rm(hdfs, args, options)
        return

    if args[0] == "upload":
        do_upload(hdfs, args, options)
        return

    if args[0] == "mv":
        do_move(hdfs, args, options)
        return

    print("{} is Unrecognized command", sys.argv[0])
    sys.exit(1)

