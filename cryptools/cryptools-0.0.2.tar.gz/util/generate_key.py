from random import randint

def generate_bytes(key_size=16):
    return bytes([randint(0,255) for _ in range(key_size)])

