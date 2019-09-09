# coding: utf-8
from django.test import TestCase

from django_pie.decorator import test_print
from django_pie.crypto import md5, sha1, sha256, b64encode, b64decode


class TestCrypto(TestCase):
    def setUp(self):
        pass

    @test_print
    def test_md5(self):
        s = 'foobar'
        self.assertEqual(md5(s), '3858f62230ac3c915f300c664312c63f')
        self.assertEqual(md5(s, True), '3858F62230AC3C915F300C664312C63F')
        s = b'foobar'
        self.assertEqual(md5(s), '3858f62230ac3c915f300c664312c63f')

    @test_print
    def test_sha1(self):
        s = 'foobar'
        self.assertEqual(sha1(s), '8843d7f92416211de9ebb963ff4ce28125932878')
        self.assertEqual(sha1(s, True), '8843D7F92416211DE9EBB963FF4CE28125932878')
        s = b'foobar'
        self.assertEqual(sha1(s), '8843d7f92416211de9ebb963ff4ce28125932878')

    @test_print
    def test_sha256(self):
        s = 'foobar'
        self.assertEqual(sha256(s), 'c3ab8ff13720e8ad9047dd39466b3c8974e592c2fa383d4a3960714caef0c4f2')
        self.assertEqual(sha256(s, True), 'C3AB8FF13720E8AD9047DD39466B3C8974E592C2FA383D4A3960714CAEF0C4F2')
        s = b'foobar'
        self.assertEqual(sha256(s), 'c3ab8ff13720e8ad9047dd39466b3c8974e592c2fa383d4a3960714caef0c4f2')

    @test_print
    def test_base64(self):
        s = 'foobar'
        ss = b64encode(s)
        self.assertEqual(ss, b'Zm9vYmFy')
        self.assertEqual(b64decode(ss), s.encode())
