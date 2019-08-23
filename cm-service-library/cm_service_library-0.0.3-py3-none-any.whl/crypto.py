from hashlib import blake2b


def hash_secret(value):
    hashed_value = blake2b(digest_size=32)
    hashed_value.update(value.encode())
    return hashed_value.hexdigest()


def verify_hash(hash, value):
    return hash_secret(value) == hash
