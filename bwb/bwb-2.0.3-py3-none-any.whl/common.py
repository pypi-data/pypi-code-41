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

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives.asymmetric.ec import ECDH
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

OTP_LOOKAHEAD = 25

class common:
    def __init__(self):
        self.init_secret = ''
        self.key = None
        self.master_pub = None
        self.otp = None
        self.otp_secret = ''
        self.otp_count = 0

    def set_otp(self, otp_secret):
        self.otp = HOTP(otp_secret.encode(), 6, SHA1(), backend=default_backend(), enforce_key_length=False)
        self.otp_secret = otp_secret
        self.otp_count = 0
        return True

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

    def enc(self, text, key=None):
        if not key:
            key = self.otp_secret.encode()
        if not key:
            raise RuntimeError('bwb not init yet')

        padder = PKCS7(AES.block_size).padder()
        padded = padder.update(text.encode())
        padded += padder.finalize()

        digest = Hash(SHA256(), default_backend())
        digest.update(key)
        key = digest.finalize()

        iv = os.urandom(4)

        cipher = Cipher(AES(key), CBC(iv * 4), default_backend())
        encryptor = cipher.encryptor()
        ct = encryptor.update(padded) + encryptor.finalize()

        return 'I' + base58.b58encode(iv + ct).decode()

    def dec(self, ciphertext, key=None):
        if not key:
            key = self.otp_secret.encode()
        if not key:
            return False # so we can run every message through
        if not ciphertext.startswith('I'):
            return False

        try:
            ciphertext = base58.b58decode(ciphertext[1:])
            iv = ciphertext[:4]
            ct = ciphertext[4:]

            digest = Hash(SHA256(), default_backend())
            digest.update(key)
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

    def get_pub(self):
        self.key = X25519PrivateKey.generate()
        pub_key = self.key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        return base58.b58encode(pub_key).decode()

    def init(self):
        self.init_secret = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(14))
        return self.get_pub()

    def handshake(self, text):
        self.init_secret = '' # clear it
        self.master_pub = X25519PublicKey.from_public_bytes(base58.b58decode(text))
        slave_pub = self.get_pub()
        self.set_otp(slave_pub)
        return slave_pub

    def secret(self, text):
        if not self.init_secret: return
        self.set_otp(text)
        slave_pub = X25519PublicKey.from_public_bytes(base58.b58decode(text))
        shared_key = self.key.exchange(slave_pub)
        derived_key = HKDF(SHA256(), length=32, salt=b'Qot.', info=None, backend=default_backend()).derive(shared_key)
        return self.enc(self.init_secret, derived_key)

    def set_secret(self, text):
        shared_key = self.key.exchange(self.master_pub)
        derived_key = HKDF(SHA256(), length=32, salt=b'Qot.', info=None, backend=default_backend()).derive(shared_key)
        otp_secret = self.dec(text, derived_key)
        return self.set_otp(otp_secret)
