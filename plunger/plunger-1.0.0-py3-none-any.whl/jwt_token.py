"""
Plunger - A tool to inspect and clean gitlab's docker registry.
Copyright (C) 2019 Bearstech

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import jwt
import sys
import base64
import hashlib
import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization import PublicFormat


def get_token(key_file, repositories=None, **kwargs):
    """generate an admin token using the registry's private key"""
    with open(key_file, 'rb') as fd:
        cert = fd.read()
    private_key = load_pem_private_key(cert, None, default_backend())
    public_key = private_key.public_key()
    der = public_key.public_bytes(Encoding.DER,
                                  PublicFormat.SubjectPublicKeyInfo)
    kid = hashlib.sha256(der).digest()
    kid = base64.b32encode(kid[0:30])
    kid = b':'.join([kid[i:i+4] for i in range(0, 12 * 4, 4)])

    headers = {
        'typ': 'JWT',
        'alg': 'RS256',
        'kid': kid.decode('ascii'),
    }

    now = datetime.datetime.utcnow()

    payload = {
        "iss": "gitlab-issuer",
        "aud": "container_registry",
        "nbf": now - datetime.timedelta(seconds=1),
        "iat": now,
        "exp": now + datetime.timedelta(seconds=60),
        "access": [
            {
                "type": "registry",
                "name": "catalog",
                "actions": ["*"],
            },
        ]
    }
    payload.update(kwargs)

    if repositories:
        payload['access'].extend([
            {
                "type": "repository",
                "name": name,
                "actions": ["*"],
            } for name in repositories])

    token = jwt.encode(payload, private_key,
                       algorithm='RS256', headers=headers)
    return token.decode('ascii')


if __name__ == '__main__':
    print(get_token(sys.argv[1]))
