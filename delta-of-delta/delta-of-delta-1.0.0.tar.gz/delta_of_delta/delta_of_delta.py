from enum import Enum
from itertools import chain
from dataclasses import dataclass
from typing import List, Union, Any, Optional


EncodingScheme = Enum("EncodingScheme", "Timestamp Delta DeltaOfDelta")


class Encoder:
    def __init__(self, *args, **kwargs):
        super().__init__()

    def encode(self, timestamp: int) -> int:
        return timestamp


class DeltaEncoder(Encoder):
    def __init__(self, timestamp: int):
        super().__init__()
        self.prev_ts = timestamp

    def encode(self, timestamp: int) -> int:
        delta = timestamp - self.prev_ts
        self.prev_ts = timestamp
        return delta


class DeltaOfDeltaEncoder(DeltaEncoder):
    def __init__(self, timestamp: int):
        super().__init__(timestamp)
        self.prev_delta = 0

    def encode(self, timestamp: int) -> int:
        delta = timestamp - self.prev_ts
        delta_of_delta = delta - self.prev_delta
        self.prev_delta = delta
        self.prev_ts = timestamp
        return delta_of_delta


class Decoder:
    def __init__(self, *args, **kwargs):
        super().__init__()

    def decode(self, timestamp: int) -> int:
        return timestamp


class DeltaDecoder(Decoder):
    def __init__(self, timestamp: int):
        super().__init__()
        self.prev_ts = timestamp

    def decode(self, delta: int) -> int:
        self.prev_ts += delta
        return self.prev_ts


class DeltaOfDeltaDecoder(DeltaDecoder):
    def __init__(self, timestamp: int):
        super().__init__(timestamp)
        self.prev_delta = 0

    def decode(self, delta: int) -> int:
        self.prev_delta += delta
        self.prev_ts += self.prev_delta
        return self.prev_ts


@dataclass
class Encoding:
    inital_timestamp: int
    values: List[int]

    @property
    def timestamps(self):
        return self.values

    def __str__(self):
        return f"[{', '.join(map(str, chain((self.inital_timestamp,), self.timestamps)))}]"


@dataclass
class DeltaEncoding(Encoding):
    @property
    def deltas(self):
        return self.values

    def __str__(self):
        offsets = (f"+{d}" if d > 0 else str(d) for d in self.deltas)
        return f"[{', '.join(chain((str(self.inital_timestamp),), offsets))}]"


@dataclass
class DeltaOfDeltaEncoding(DeltaEncoding):
    @property
    def delta_of_deltas(self):
        return self.values

    def __str__(self):
        offsets = (f"+{d}" if d > 0 else str(d) for d in self.delta_of_deltas)
        return f"[{', '.join(chain((str(self.inital_timestamp),), offsets))}]"


def encode(timestamps: List[int], scheme: Optional[EncodingScheme] = None) -> Encoding:
    if scheme is EncodingScheme.Timestamp:
        return timestamp_encode(timestamps)
    if scheme is EncodingScheme.Delta:
        return delta_encode(timestamps)
    return delta_of_delta_encode(timestamps)


def _encode(timestamps: List[int], encoder: Encoder, encoding: Encoding) -> Encoding:
    enc = encoder(timestamps[0])
    tss = [enc.encode(ts) for ts in timestamps[1:]]
    return encoding(timestamps[0], tss)


def delta_of_delta_encode(timestamps: List[int]) -> DeltaOfDeltaEncoding:
    return _encode(timestamps, DeltaOfDeltaEncoder, DeltaOfDeltaEncoding)


def delta_encode(timestamps: List[int]) -> DeltaEncoding:
    return _encode(timestamps, DeltaEncoder, DeltaEncoding)


def timestamp_encode(timestamps: List[int]) -> List[int]:
    return _encode(timestamps, Encoder, Encoding)


def decode(encoding: Encoding) -> List[int]:
    if isinstance(encoding, DeltaOfDeltaEncoding):
        return delta_of_delta_decode(encoding)
    if isinstance(encoding, DeltaEncoding):
        return delta_decode(encoding)
    return timestamp_decode(encoding)


def _decode(encoding: Encoding, decoder: Decoder) -> List[int]:
    tss = [encoding.inital_timestamp]
    dec = decoder(encoding.inital_timestamp)
    for v in encoding.values:
        tss.append(dec.decode(v))
    return tss


def delta_of_delta_decode(dode: DeltaOfDeltaEncoding) -> List[int]:
    return _decode(dode, DeltaOfDeltaDecoder)


def delta_decode(de: DeltaEncoding) -> List[int]:
    return _decode(de, DeltaDecoder)


def timestamp_decode(e: Encoding) -> List[int]:
    return _decode(e, Decoder)


if __name__ == "__main__":
    timestamps = [1496163646, 1496163676, 1496163706, 1496163735, 1496163765]

    print(f"Timestamps:              {timestamps}")

    ts = timestamp_encode(timestamps)
    print(f"Timestamp Encoding:      {ts}")

    d = delta_encode(timestamps)
    print(f"Delta Encoding:          {d}")

    dod = delta_of_delta_encode(timestamps)
    print(f"Delta of Delta Encoding: {dod}")

