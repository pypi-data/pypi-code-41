import base64
from typing import Union

from nezha.ustring import to_bytes, to_str


class Picture:

    @staticmethod
    def to_base64(s: Union[str, bytes, bytearray], is_file: bool = False) -> str:
        if is_file and isinstance(s, str):
            with open(s, mode='rb') as f:
                content = f.read()
        else:
            content = to_bytes(s)
        return to_str(base64.b64encode(content))
