import Lib.base64 as sys_base64


class Base64(object):

    @staticmethod
    def encode(src: str, encoding="utf8") -> str:
        """
        base64编码
        :param src: 待编码文本
        :param encoding: 编码类型
        :return:
        """
        return sys_base64.b64encode((bytes(src, encoding=encoding))).decode()

    @staticmethod
    def decode(src: str, encoding="utf8") -> str:
        """
        base64解码
        :param src: 待解码文本
        :param encoding: 编码类型
        :return:
        """
        return sys_base64.b64decode(bytes(src, encoding=encoding)).decode()

    @staticmethod
    def encode_multilines(src_lines: [], encoding="utf8") -> []:
        """
        base64多行编码
        :param src_lines: 待编码的多行文本
        :param encoding: 编码类型
        :return:
        """
        base64_lines = []
        for line in src_lines:
            base64_str = sys_base64.b64encode(bytes(line, encoding=encoding)).decode()  # 编码
            base64_lines.append(base64_str)
        return base64_lines

    @staticmethod
    def decode_multilines(src_lines: [], encoding="utf8") -> []:
        """
        base64多行解码
        :param src_lines: 待解码的多行文本
        :param encoding: 编码类型
        :return:
        """
        base64_lines = []
        for line in src_lines:
            base64_str = sys_base64.b64decode(bytes(line, encoding=encoding)).decode()  # 解码
            base64_lines.append(base64_str)
        return base64_lines
