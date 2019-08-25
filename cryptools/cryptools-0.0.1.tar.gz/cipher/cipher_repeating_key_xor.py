def repeating_xor(byte_string, byte_key):
    key_length = len(byte_key)
    result = ''
    for i in range(len(byte_string)):
        result += chr(byte_string[i] ^ byte_key[i % key_length])
    return result.encode('utf-8')
