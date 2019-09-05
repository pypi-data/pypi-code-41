# coding=utf-8
import hashlib


# 生成MD5
def genearteMD5(str):
    # 创建md5对象
    hl = hashlib.md5()

    # Tips
    # 此处必须声明encode
    # 否则报错为：hl.update(str)    Unicode-objects must be encoded before hashing
    hl.update(str.encode(encoding='utf-8'))

    print('MD5加密前为 ：' + str)
    print('MD5加密后为 ：' + hl.hexdigest())

    return hl.hexdigest()


if __name__ == '__main__':
    genearteMD5("123456")