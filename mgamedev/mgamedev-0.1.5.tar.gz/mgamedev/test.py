# encoding:utf-8


import sys
sys.path.append("./py_lib")
from py_lib import remote  # noqa
import logging  # noqa


def test_remote():
    HOST = "172.16.50.45"
    PORT = 22
    con = remote.RemoteCtrl(HOST, PORT, pwd="123456")
    ret = con.ssh_command("ls")
    print(con.ssh_command("cd /data0/"), "cd result")
    ret2 = con.ssh_command("ls")
    # logging.warning(ret, "--->>ret")
    print(ret)
    print(ret2)


def test_ftp():
    con = remote.RemoteCtrl(
        "118.25.105.42", usr="CeshiClinetFo", pwd="CeshiClinetFo@!@#")
    con.ftp_upload("/data0/private_git/dating_qq.apk",
                   "/usr/local/openresty/nginx/xpm/dldevbins/dating_qq.apk")


def test_sftp():
    con = remote.RemoteCtrl(
        "172.16.50.45", usr="root", pwd="123456"
    )
    con.sftp_upload("/data0/private_git/dating_qq.apk",
                    "/usr/local/openresty/nginx/xpm/dldevbins/dating_qq.apk")


class DTest:
    def test_pylib(self):
        test_remote()

    def test_ftpupload(self):
        test_ftp()


if __name__ == "__main__":
    t = DTest()
    # t.test_pylib()
    # t.test_ftpupload()
    test_sftp()
