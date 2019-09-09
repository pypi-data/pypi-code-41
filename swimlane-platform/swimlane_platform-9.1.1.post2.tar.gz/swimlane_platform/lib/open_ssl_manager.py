from OpenSSL import crypto
from OpenSSL.crypto import PKey, X509
from typing import Tuple


def create_cert(country="US", state="Colorado", location="Lousville", company="Swimlane Inc", application='swimlane'):
    # type: (str, str, str, str, str) -> Tuple[X509, PKey]
    """
    Creates default self generated cert and key.
    :return: Tuple with cert and key
    """
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 1024)
    cert = crypto.X509()
    cert.get_subject().C = country
    cert.get_subject().ST = state
    cert.get_subject().L = location
    cert.get_subject().OU = company
    cert.get_subject().CN = application
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha1')
    return cert, k
