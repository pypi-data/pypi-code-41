import os
import binascii
import base64
from django.test import TestCase
from django.contrib.auth.models import User
from apiview.utils import model_to_json
from apiview.utils import queryset_to_json
from apiview.annotations import Boolean
from apiview.annotations import Integer
from apiview.annotations import String
from apiview.annotations import Bytes

class TestApiview(TestCase):

    def test01(self):
        u = User()
        u.username = 'test01'
        u.email = 'test01@example.com'
        u.save()
        data = model_to_json(u)
        assert data
        assert data["username"] == "test01"
    
    def test02(self):
        u = User()
        u.username = "test02"
        u.email = "test02@example.com"
        u.save()
        us = User.objects.all()
        data = queryset_to_json(us)
        assert data
        assert isinstance(data, list)

    def test03(self):
        assert Boolean("True") is True
        assert Boolean("False") is False
        assert Boolean("1") is True
        assert Boolean("0") is False
        assert Boolean("y") is True
        assert Boolean("n") is False
        assert Boolean("yes") is True
        assert Boolean("no") is False
        assert Boolean(1) is True
        assert Boolean(0) is False
        assert Boolean(True) is True
        assert Boolean(False) is False
        assert Boolean(1.1) is True
        assert Boolean(0.0) is False

    def test04(self):
        assert Integer(1) == 1
        assert Integer(0) == 0
        assert Integer("1") == 1
        assert Integer("0") == 0

    def test05(self):
        assert String("a") == "a"
        assert String("测试") == "测试"
        assert String(1) == "1"
        assert String(True) == "True"
        assert String(False) == "False"
        assert String("测试".encode("utf-8")) == "测试"
        assert String("测试".encode("gbk")) == "测试"

    def test06(self):
        assert Bytes("a") == b"a"
        assert Bytes(b"a") == b"a"
        assert Bytes("测试") == "测试".encode("utf-8")
        assert Bytes("YQ==") == b"a"
        assert Bytes("YWI=") == b"ab"
        assert Bytes("6162") == b"ab"

    def test07(self):
        s = os.urandom(16)
        t1 = binascii.hexlify(s).decode()
        t2 = base64.encodebytes(s).decode()
        t3 = base64.urlsafe_b64encode(s).decode()
        assert Bytes(t1) == s
        assert Bytes(t2) == s
        assert Bytes(t3) == s
