import random
import logging
from os.path import exists, join
from socket import gethostname

from OpenSSL import crypto

CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"

logger = logging.getLogger(__name__)

def gen_ssl_cert_if_none(config_dir):
    """
    If cert.pem and key.pem are not found in ~/.braincube, generate them (self-signed certificate)
    """
    if not exists(join(config_dir, CERT_FILE)) \
            or not exists(join(config_dir, KEY_FILE)):
        # create a key pair
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)
        # create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().C = "FR"  # country code
        cert.get_subject().L = "Issoire"  # locality
        cert.get_subject().OU = "Braincube"  # organisation
        cert.get_subject().CN = gethostname()
        cert.set_serial_number(random.getrandbits(128))
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        logger.info("Generate self-signed ssl certificate.")
        cert.sign(key, 'sha256')
        open(join(config_dir, CERT_FILE), "wb").write(
            crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        open(join(config_dir, KEY_FILE), "wb").write(
            crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
