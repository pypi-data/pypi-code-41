import xxhash as xx


def fingerprint(fname):
    hash = xx.xxh64()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()
