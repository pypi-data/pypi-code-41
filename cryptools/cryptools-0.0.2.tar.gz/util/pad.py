def pad(m, style='pkcs7'):
    if style == 'pkcs7':
        block_size = 16
        num_remaining = block_size - len(m) % block_size
        m += bytes([num_remaining]) * num_remaining
    elif style == 'md':
        ml = len(m) * 8
        m += b'\x80'
        m += bytes((56 - len(m)) % 64)
        m += ml.to_bytes(8, byteorder='big')
        return m
    else:
        raise Exception('Padding style not supported')
    return m

def unpad(m, block_size=16, style='pkcs7'):
    if style == 'pkcs7':
        block_size = 16
        # Laughably unsafe
        assert(not (len(m) % block_size))
        last_byte = m[-1]
        assert(last_byte <= block_size)
        m = m[:-last_byte]
    else:
        raise Exception('Padding style not supported')
    return m
