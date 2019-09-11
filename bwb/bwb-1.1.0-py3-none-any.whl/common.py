import base58
import base64
import os
import random
import string

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.twofactor.hotp import HOTP
from cryptography.hazmat.primitives.hashes import Hash, SHA1, SHA256

from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.padding import PKCS7

OTP_LOOKAHEAD = 25

class common:
    def __init__(self):
        self.otp = None
        self.secret = ''
        self.otp_count = 0

    def init(self, secret=None):
        secret = secret or ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
        self.otp = HOTP(secret.encode(), 6, SHA1(), backend=default_backend(), enforce_key_length=False)
        self.secret = secret
        self.otp_count = 0
        return secret

    def get_otp(self, target):
        if not self.otp:
            raise RuntimeError('bwb not init yet')
        if not isinstance(target, int):
            raise ValueError('invalid target')
        if int(target) <= 999999:
            raise ValueError('invalid target')

        code = self.otp.generate(self.otp_count).decode()
        self.otp_count += 1
        return str(int(target) % int(code)).zfill(6)

    def get_otp_cast(self):
        if not self.otp:
            raise RuntimeError('bwb not init yet')

        code = self.otp.generate(self.otp_count).decode()
        self.otp_count += 1
        return code

    def check_otp(self, code):
        if not self.otp:
            return False

        for i in range(OTP_LOOKAHEAD):
            count = self.otp_count + i
            otp_at = self.otp.generate(count).decode()
            if otp_at == str(code): # broadcast
                self.otp_count = count + 1
                return True
            elif self.TELEGRAM_ID % int(otp_at) == int(code):
                self.otp_count = count + 1
                return True
        return False

    def to_b58(self, text):
        return 'l' + base58.b58encode(text.encode()).decode()

    def from_b58(self, text):
        if not text.startswith('l'):
            return False
        try:
            return base58.b58decode(text[1:]).decode()
        except BaseException as e:
            return False

    def enc(self, text):
        if not self.secret:
            raise RuntimeError('bwb not init yet')

        padder = PKCS7(AES.block_size).padder()
        padded = padder.update(text.encode())
        padded += padder.finalize()

        digest = Hash(SHA256(), default_backend())
        digest.update(self.secret.encode())
        key = digest.finalize()

        iv = os.urandom(4)

        cipher = Cipher(AES(key), CBC(iv * 4), default_backend())
        encryptor = cipher.encryptor()
        ct = encryptor.update(padded) + encryptor.finalize()

        return 'I' + base58.b58encode(iv + ct).decode()

    def dec(self, ciphertext):
        if not self.secret:
            return False # so we can run every message through
        if not ciphertext.startswith('I'):
            return False

        try:
            ciphertext = base58.b58decode(ciphertext[1:])
            iv = ciphertext[:4]
            ct = ciphertext[4:]

            digest = Hash(SHA256(), default_backend())
            digest.update(self.secret.encode())
            key = digest.finalize()

            cipher = Cipher(AES(key), CBC(iv * 4), default_backend())
            decryptor = cipher.decryptor()
            pt = decryptor.update(ct) + decryptor.finalize()

            unpadder = PKCS7(AES.block_size).unpadder()
            unpadded = unpadder.update(pt)
            unpadded += unpadder.finalize()

            return unpadded.decode()
        except BaseException as e:
            return False

    def wrap(self, text, target=None, b58=False, enc=False):
        if target:
            code = self.get_otp(target)
        else:
            code = self.get_otp_cast()

        text = code + text

        if enc:
            return self.enc(text)
        elif b58:
            return self.to_b58(text)
        else:
            return text

    def parse(self, text):
        return self.dec(text) or self.from_b58(text) or text

    def check_auth(self, text):
        try:
            int(text[:6])
        except ValueError:
            return False

        if self.check_otp(text[:6]):
            return True
        else:
            return False
