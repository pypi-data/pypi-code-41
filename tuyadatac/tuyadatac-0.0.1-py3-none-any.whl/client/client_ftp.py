#!/usr/bin/python
#-*-coding:utf-8 -*-

from ftplib import FTP
from io import BytesIO
import time

class Client:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.user = ''
        self.password = ''
        self.ftp = None
    def login(self, user, password):
        self.user = user
        self.password = password
        self.ftp = FTP()
        self.ftp.connect(self.address, self.port)
        self.ftp.login(self.user, self.password)
    def get_file(self, filepath):
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
            # bios.append(bio)
            bios[file] = bio
        return bios
