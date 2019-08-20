import base64
import json
import zlib

from errors import Error, ErrorCodes

class Compressor:

    def __init__(self, data):
        self.data = data

    def compress(self):
        """Returns the compressed data"""
        try:
            compressed_data = base64.b64encode(
                zlib.compress(
                    json.dumps(self.data).encode('utf-8')
                )
            ).decode('ascii')
        except ValueError as e:
            raise Error(ErrorCodes.DataCompressionError, data=self.data)
        return compressed_data

    def decompress(self):
        """Decompresses the compressed data"""
        try:
            decompressed_data = zlib.decompress(base64.b64decode(self.data)).decode('utf-8')
        except TypeError as e:
            raise Error(ErrorCodes.DataDecompressionError, data=self.data)
        return decompressed_data


c = Compressor('eJxNjUELgkAQhf+KzDlFu1Qew6igQxCdZdJRltxdcUdJxP/eTKeO73vfm1mAjaXAaHvII9im2T5OD/EONhFU3oXRGteWgYbJVKSGQO1kE7Cl0tQK/5J09OEBFeOr0tzjwIaNDPMolSzfeAwq3J/H2/VxORWq+aYJxIKz32buPOrxBd40qzxhNxKsUrLvTaWooCk5+xptgq1LjGs8rF+lWECp')
print(c.decompress())


# {"payload": "eJx1UtuO2jAU/JXKz5S145DbW5dFK6ouoKW0qqoqcnwpLiYOTgyliH/vMZDtRe1LLp45kzkzOaGtbFv2VZZaoKJ/QQPU2UZzOHmQ++GjFWw71PVe1p11R3hSFihWqVZ2qCBZOkANc53utK1RgWFag1LHtg0o4OyORHcRJvkrkhV0VJB4iCnJQAEonW+Bs1yNx5PlEgWdo7EMvJz+54zxTu91dyxrtpWATGf389XsoRzPnxbvJu8nQVe6veayZzxPxpPph+nsESAndx6sXUVHImMkFymNIhkryllUJQmmMU1VlKRpDHy+ZnUtDSpqb8wAKW+UNmYLSZQcLtL1iGAdC66tE9K9McZyFuJYMAcmgNcGsF3rJsy216nzAL2kumpAQS5+rd84KzwP1M8noEG4zJSwvIfbrjtC7hGGqP1lTvyJxAHpZ8DKBggX5LeBv45b6x2X/Ta3j5fC7Mt24yErgkmWQCA7z2po+tgzudEhDO8vieJ4hBXhicp4Gmc4zRmvZMplXBGSZioCAWNf2Cn/8Xb98XCP2Zwuvx3Ep9XrUF/lwRn8WGjxPH0KB/I7BFjDKj2C/9VEryqgwQQTyXEOrVYihyZpFOM4qkhCKQVBEX6BXuy6R7B1203Lvp8v0NDBuo0y9jAVt8Pz+SdshRFd", "compression": true}