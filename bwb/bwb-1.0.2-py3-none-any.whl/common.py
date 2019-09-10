import base58
import base64
import pyotp
import random
import string

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256, SHA512, MD5
from Crypto.Util.Padding import pad, unpad

OTP_LOOKAHEAD = 25

class common:
    def __init__(self):
        self.otp = None
        self.secret = ''
        self.otp_count = 0

    def init(self, secret=None):
        secret = secret or ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
        encoded = secret.encode()
        b32 = base64.b32encode(encoded)
        self.otp = pyotp.HOTP(b32)
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

        code = self.otp.at(self.otp_count)
        self.otp_count += 1
        return str(int(target) % int(code)).zfill(6)

    def get_otp_cast(self):
        if not self.otp:
            raise RuntimeError('bwb not init yet')

        code = self.otp.at(self.otp_count)
        self.otp_count += 1
        return code

    def check_otp(self, code):
        if not self.otp:
            return False

        for i in range(OTP_LOOKAHEAD):
            count = self.otp_count + i
            if self.otp.at(count) == str(code): # broadcast
                self.otp_count = count + 1
                return True
            elif self.TELEGRAM_ID % int(self.otp.at(count)) == int(code):
                self.otp_count = count + 1
                return True
        return False

    def check_auth(self, text):
        try:
            int(text[:6])
        except ValueError:
            return False, None

        if self.check_otp(text[:6]):
            return True, text[6:]
        else:
            return False, text[6:]

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

        key = SHA256.new(self.secret.encode()).digest()
        iv = get_random_bytes(4)
        cipher = AES.new(key, AES.MODE_CBC, iv * 4)
        ct = cipher.encrypt(pad(text.encode(), AES.block_size))
        return 'I' + base58.b58encode(iv + ct).decode()

    def dec(self, ciphertext):
        if not self.secret:
            return False # so we can run every message through
        if not ciphertext.startswith('I'):
            return False

        try:
            ciphertext = base58.b58decode(ciphertext)
            key = SHA256.new(self.secret.encode()).digest()
            iv = ciphertext[:4]
            ct = ciphertext[4:]
            cipher = AES.new(key, AES.MODE_CBC, iv * 4)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            return pt.decode()
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
        decoded = self.dec(text) or self.from_b58(text) or text
        return self.check_auth(decoded) # returns tuple
