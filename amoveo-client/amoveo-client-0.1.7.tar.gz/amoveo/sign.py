from .serializer import serialize, int_to_string
import hashlib
from binascii import unhexlify
from ecdsa.util import sigencode_der
from ecdsa import SigningKey, SECP256k1
import base64
from fastecdsa import keys, curve


def sign(res, private_key):
    serialized_tx = serialize(res)
    key = SigningKey.from_string(unhexlify(private_key), curve=SECP256k1, hashfunc=hashlib.sha256)
    sign = key.sign_deterministic(bytes(serialized_tx), sigencode=sigencode_der)
    return base64.b64encode(sign).decode()


def generate_wallet():
    """
    Generate Veo wallet
    :return: address, private_key, passphrase
    """
    private_key_raw, public_key = keys.gen_keypair(curve.secp256k1)
    private_key = keys.hexlify(int_to_string(private_key_raw))
    address = base64.b64encode(b'\x04' + int_to_string(public_key.x) + int_to_string(public_key.y))
    private_key = private_key.decode("utf-8")
    passphrase = private_key_raw
    address = address.decode("utf-8")
    return address, private_key, passphrase
