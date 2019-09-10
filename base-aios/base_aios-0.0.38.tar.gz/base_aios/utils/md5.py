import hashlib

def encrypt_md5(txt):
    md5 = hashlib.md5()
    md5.update(bytes(txt, encoding='utf-8'))
    return md5.hexdigest()

def encrypt_sha256(txt):
    SHA = hashlib.sha256()
    SHA.update(txt.encode('utf-8'))
    return SHA.hexdigest()