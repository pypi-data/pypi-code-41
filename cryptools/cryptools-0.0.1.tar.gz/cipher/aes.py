from Crypto.Cipher import AES
from random import randint
from functools import reduce
from binascii import hexlify
from .xor import xor
from ..util.pad import pad, unpad

def aes_ecb_encrypt(m, key, padding=True, output='hex'):
    if isinstance(m, str):
        m = m.encode('utf-8')
    if isinstance(key, str):
        key = key.encode('utf-8')

    cipher = AES.new(key, AES.MODE_ECB)
    if padding:
        m = pad(m)

    c = cipher.encrypt(m)

    if output == 'hex':
        c = hexlify(c).decode('utf-8')
    elif output == 'bytes':
        pass

    return c

def aes_ecb_decrypt(c, key, padding=True, output='bytes'):
    if isinstance(c, str):
        c = c.encode('utf-8')
    if isinstance(key, str):
        key = key.encode('utf-8')
    
    cipher = AES.new(key, AES.MODE_ECB)
    m = cipher.decrypt(c)
    if padding:
        m = unpad(m)

    if output == 'hex':
        m = hexlify(m).decode('utf-8')
    elif output == 'bytes':
        pass

    return m

def aes_cbc_encrypt(m, key, iv, padding=True, output='hex'):
    if isinstance(m, str):
        m = m.encode('utf-8')
    if isinstance(key, str):
        key = key.encode('utf-8')
    if isinstance(iv, str):
        iv = iv.encode('utf-8')
    
    cipher = AES.new(key, AES.MODE_ECB)
    if padding:
        m = pad(m)
    blocks = [m[i:i+16] for i in range(0, len(m), 16)]
    c_blocks = []
    for block in blocks:    
        iv = cipher.encrypt(xor(block, iv))
        c_blocks.append(iv)
    c = reduce(lambda x,y: x+y, c_blocks)

    if output=='hex':
        c = hexlify(c).decode('utf-8')
    elif output=='bytes':
        pass

    return c

def aes_cbc_decrypt(c, key, iv, padding=True, output='hex'):
    if isinstance(c, str):
        c = c.encode('utf-8')
    if isinstance(key, str):
        key = key.encode('utf-8')
    if isinstance(iv, str):
        iv = iv.encode('utf-8')
    
    cipher = AES.new(key, AES.MODE_ECB)
    c_blocks = [c[i:i+16] for i in range(0, len(c), 16)][::-1]
    c_blocks.append(iv)
    m_blocks = []
    for i in range(len(c_blocks) - 1):
        c_block = c_blocks[i]
        m_blocks.append(xor(cipher.decrypt(c_block), c_blocks[i+1]))
    m = reduce(lambda x,y: x+y, m_blocks[::-1])
    if padding:
        m = unpad(m)

    if output == 'hex':
        m = hexlify(m).decode('utf-8')
    elif output == 'bytes':
        pass
    return m

def aes_ctr_encrypt(m, key, nonce=b'\x00\x00\x00\x00\x00\x00\x00\x00', byteorder='little', output='hex'):
    if isinstance(m, str):
        m = m.encode('utf-8')
    if isinstance(key, str):
        key = key.encode('utf-8')
    if isinstance(nonce, str):
        nonce = nonce.encode('utf-8')
    
    cipher = AES.new(key, AES.MODE_ECB)
    m_length = len(m)
    counter = 0
    keystream = b''
    while len(keystream) < m_length:
        keystream += cipher.encrypt(nonce + counter.to_bytes(8, byteorder=byteorder))
        counter += 1
    c = xor(m, keystream[:m_length])

    if output == 'hex':
        c = hexlify(c).decode('utf-8')
    elif output == 'bytes':
        pass
    return c


def aes_ctr_decrypt(c, key, nonce=b'\x00\x00\x00\x00\x00\x00\x00\x00', byteorder='little', output='hex'):
    if isinstance(c, str):
        c = c.encode('utf-8')
    if isinstance(key, str):
        key = key.encode('utf-8')
    if isinstance(nonce, str):
        nonce = nonce.encode('utf-8')
    
    return aes_ctr_encrypt(c, key, nonce, byteorder, outputs)
