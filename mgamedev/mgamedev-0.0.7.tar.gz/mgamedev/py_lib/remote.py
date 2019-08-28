# encoding:utf8

from decorator import singleton
import paramiko
import os
import sys
import time
import threading
import string
import logging
import ftplib
logging.basicConfig(level=logging.INFO)


def _log_noempty(strarr):
    if len(strarr) == 0:
        pass
    else:
        logging.info("CONSOLE-->%s)" % (strarr))


@singleton
class RemoteCtrl():

    def __init__(self, host, port=22, usr="root", pwd=None, keyfile=None):
        self.HOST = host
        self.PORT = int(port)
        self._name = usr
        self._pwd = pwd
        self._keyfile = keyfile

        self._ssh = None
        self._sftp = None
        self._ftp = None

    def _get_sslcon(self):
        if (self._ssh):
            return self._ssh
        try:
            con = paramiko.SSHClient()
            con.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self._keyfile:
                con.connect(self.HOST, self.PORT, "",
                            key_filename=self._keyfile)
            else:
                con.connect(self.HOST, self.PORT, username=self._name,
                            password=self._pwd)
            logging.info(
                "SSH connect to the host-->>(%s:%s) successful!" % (self.HOST, self.PORT))
            self._ssh = con
            return con
        except:
            logging.error(
                "SSH connect to the host-->>(%s:%s) failed!" % (self.HOST, str(self.PORT)))
            sys.exit()
        return None

    def _get_sftp(self):
        if (self._sftp):
            return self._sftp
        try:
            con = paramiko.Transport((self.HOST, 22))
            con.connect(username=self._name, password=self._pwd)
            sftp = paramiko.SFTPClient.from_transport(con)
            self._sftp = sftp
            return sftp
        except:
            logging.error(
                "SFtp connect to the host-->>(%s) failed!" % self.HOST)
            sys.exit()

    def _get_ftp(self):
        if (self._ftp):
            return self._ftp
        ftp = ftplib.FTP()
        ftp.connect(self.HOST, 21)
        ftp.login(self._name, self._pwd)
        self._ftp = ftp
        return ftp

    def close(self):
        if self._sftp:
            self._sftp.close()
            self._sftp = None
        if self._ssh:
            self._ssh.close()
            self._ssh = None
        if self._ftp:
            self._ftp.close()
        self.HOST = None
        self._name = None
        self._pwd = None
        logging.info("Remote connect closed!")

    # (discard)
    def commit_file(self, localfile, netfile, proce_cb=None):
        return self.sftp_upload(localfile, netfile, proce_cb)

    # 执行远端命令
    def ssh_command(self, strcmd):
        stdin, stdout, stderr = self._get_sslcon().exec_command(strcmd)
        return stdout.read()

    # 下载目标文件
    def chkout_file(self, netfile, localfile):
        self._get_sftp().get(netfile, localfile)

    # 压缩目标目录
    def zip_tardir(self, netfile, netdir):
        stdin, stdout, stderr = self._get_sslcon().exec_command(
            "zip -q -r %s %s" % (netdir, netfile))
        _log_noempty(stdout.readlines())
        _log_noempty(stderr.readlines())

    # sftp上传文件
    def sftp_upload(self, localfile, netfile, proce_cb=None):
        logging.info("Uploading the file from local <%s> to <%s>" %
                     (localfile, netfile))
        return self._get_sftp().put(localfile, netfile, proce_cb)

    # ftp 上传文件
    def ftp_upload(self, localfile, netfile, proce_cb=None):
        logging.info("Uploading the file from local <%s> to <%s>" %
                     (localfile, netfile))
        ftp = self._get_ftp()
        BUFF_SIZE = 1024
        with open(localfile, "rb") as fp:
            ftp.storbinary("STOR " + netfile, fp, BUFF_SIZE)
        logging.info("Upload suc!")

if __name__ == "__main__":
    UNAME = "root"
    IP = "192.168.62.144"
    PWD = "123456"
    cli = RemoteCtrl(IP, UNAME, PWD)
    print(cli.ssh_command("ls"))
    cli.close()
