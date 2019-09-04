#!/usr/bin/python
# -*-coding:utf-8 -*-

import ftplib
from ftplib import FTP
from io import BytesIO
import time
from PIL import Image
import numpy as np
import cv2
from contextlib import closing


import sys ,os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# from client_workspace import Workspace

class Client:

    # def __init__(self, address, port):
    #     self.address = address
    #     self.port = port
    #     self.common_init()
    #
    # def __init__(self, workspace):
    #     self.address = workspace.address()
    #     self.port = workspace.port()
    #     self.common_init()

    def common_init(self):
        self.user = ''
        self.password = ''
        self.ftp = None
        self.current_dir = '/'

#登录相关
    def login_workspace(self, connect, workspace):
        self.connect = connect
        self.workspace = workspace
        self.login(connect.address(), connect.port(),
                   workspace.username(), workspace.password())
        self.cd(workspace.workspace())

    def login(self, address, port, user, password):
        self.common_init()
        self.address = address
        self.port = port
        self.user = user
        self.password = password
        self.ftp = FTP()
        self.retry(self.address, self.port, self.user, self.password)

    def retry(self, address, port, user, password):
        self.ftp.connect(address, port)
        self.ftp.login(user, password)
        self.ftp.passive = True
        # self.ftp.voidcmd('TYPE I')

    # 获取文件相关
    def get_file(self, filepath):
        self.keep()
        bio = BytesIO()

        def handle_binary(data):
            bio.write(data)

        resp = self.ftp.retrbinary("RETR " + filepath, callback=handle_binary)
        bio.seek(0)
        return bio, resp

    def get_files(self, filepaths):
        bios = {}
        for file in filepaths:
            time.sleep(0.01)
            bio, resp = self.get_file(file)
            bios[file] = bio
        return bios

    def transfer(self, filepath, BUFFER_LEN, callback):
        def request_file():
            # self.ftp.voidcmd('TYPE I')
            self.keep()
            conn = self.ftp.transfercmd('retr ' + filepath)
            return conn
        conn = request_file()
        while True:
            chunk = conn.recv(BUFFER_LEN)
            if not chunk:
                break
            callback(chunk)
        conn.close()
        self.cd(self.workspace.workspace())
        # with contextlib.closing(request_file()) as conn:
        #     while True:
        #         chunk = conn.recv(BUFFER_LEN)
        #         if not chunk:
        #             break
        #         callback(chunk)
        # conn.close()

    # 上传文件相关
    def upload_file(self, local, remote):
        self.keep()
        bufsize = 1024 * 1024
        fp = open(local, 'rb')
        self.ftp.storbinary('STOR ' + remote, fp)  # 上传文件
        self.ftp.set_debuglevel(0)
        fp.close()  # 关闭文件

# 文件列表相关
    def cd(self, path):
        self.keep()
        is_success = True
        try:
            self.ftp.cwd(path)
        except ftplib.error_perm:
            is_success = False
        return self.pwd(), is_success

    def pwd(self):
        self.keep()
        self.current_dir = self.ftp.pwd()
        return self.current_dir

    def ls(self):
        self.keep()
        return self.ftp.nlst()


    def keep(self):
        # 暂时先不写while 做循环看看情况再说
        if self.status() == False:
            print('Lost connect, retry ... ')
            self.retry(self.address, self.port, self.user, self.password)

    def status(self):
        try:
            self.ftp.voidcmd("NOOP")
            return True
        except (BrokenPipeError, IOError, ftplib.error_temp):
            return False

    def get_img(self, filepaths, mode="RGB"):
        bio, resp = self.get_file(filepaths)
        img = Image.open(bio)
        if mode == "RGB":
            img = np.asarray(img)
        elif mode == "BGR":
            img = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
        else:
            raise ValueError(f"no mode named {mode}, only support RGB and BGR")
        return img

