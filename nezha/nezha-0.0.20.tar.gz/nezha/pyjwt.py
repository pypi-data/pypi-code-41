from typing import Dict

import jwt
from nezha.ustring import to_str


class Jwt:

    @staticmethod
    def encode(data: Dict) -> str:
        return to_str(jwt.encode(data, 'secret', algorithm='HS256'))

    @staticmethod
    def decode(encoded: str) -> Dict:
        return jwt.decode(encoded, 'secret', algorithms=['HS256'])
