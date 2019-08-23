import collections

from volcano.general.bin import get_crc16_as_bytes, hi_byte, lo_byte
from volcano.general.modbus import MbLimits, MbFunctionCode, ErrorCode, MbError

ModbusRequestReadWords = collections.namedtuple('ModbusRequestReadWords', 'size_bytes trans_id slave_nb fn_nb addr nb_words')
ModbusRequestReadBits = collections.namedtuple('ModbusRequestReadBits', 'size_bytes trans_id slave_nb fn_nb addr nb_bits')


def _word_ml(ba: (bytes, bytearray), offset: int) -> int:
    assert isinstance(ba, (bytes, bytearray)), ba
    assert isinstance(offset, int), offset
    assert len(ba) > (offset + 1)

    return (ba[offset] << 8) | ba[offset + 1]


# Response:
#   - None = not enough data
#   - MbError,  (MbException not raisen!)
#   - (bytes_parsed: int, request: MbServerRequest)
def parse_req_tcp(ba: (bytes, bytearray), offset: int = 0, nb: (None, int) = None) -> (None, ModbusRequestReadWords, ModbusRequestReadBits):    # pylint: disable=bad-whitespace
    assert isinstance(ba, (bytes, bytearray)), ba
    assert isinstance(offset, int), offset
    assert nb is None or isinstance(nb, int), nb

    if nb is None:
        nb = len(ba) - offset

    if nb < 6:
        return None

    rtu_size = _word_ml(ba, offset + 4)
    tcp_size = rtu_size + 6

    if nb < tcp_size:
        return None

    if rtu_size < 2:
        raise MbError(ErrorCode.BadData)

    rtu_offset = 6
    trans_id = _word_ml(ba, offset + 0)
    slave_nb = ba[rtu_offset + 0]
    fn_nb = ba[rtu_offset + 1]

    if fn_nb in (MbFunctionCode.MB_FN_READ_OUT_BITS_1, MbFunctionCode.MB_FN_READ_IN_BITS_2):
        # REQ: Slave,Fn,AddrH,AddrL,NbBitsH,NbBitsL
        if rtu_size != 6:
            raise MbError(ErrorCode.BadData)

        addr = _word_ml(ba, rtu_offset + 2)
        nb_bits = _word_ml(ba, rtu_offset + 4)

        if nb_bits == 0 or nb_bits > MbLimits.MAX_READ_BITS_NB or (addr + nb_bits - 1) > 0xffff:
            raise MbError(ErrorCode.BadData)

        return ModbusRequestReadBits(tcp_size, trans_id, slave_nb, fn_nb, addr, nb_bits)

    elif fn_nb in (MbFunctionCode.MB_FN_READ_OUT_WORDS_3, MbFunctionCode.MB_FN_READ_IN_WORDS_4):
        # REQ: Slave,Fn,AddrH,AddrL,NbWordsH,NbWordsL
        if rtu_size != 6:
            raise MbError(ErrorCode.BadData)

        addr = _word_ml(ba, rtu_offset + 2)
        nb_words = _word_ml(ba, rtu_offset + 4)

        if nb_words == 0 or nb_words > MbLimits.MAX_READ_WORDS_NB or (addr + nb_words - 1) > 0xffff:
            raise MbError(ErrorCode.BadData)

        return ModbusRequestReadWords(tcp_size, trans_id, slave_nb, fn_nb, addr, nb_words)

    else:
        raise MbError(ErrorCode.UnknownFn)


def _wrap_res_tcp(trans_id: int, rtu_data: (bytes, bytearray)) -> bytes:
    assert isinstance(trans_id, int), trans_id
    assert isinstance(rtu_data, (bytes, bytearray)), rtu_data

    if trans_id < 0 or trans_id > 0xffff:
        raise MbError(ErrorCode.BadData)

    return bytes([hi_byte(trans_id), lo_byte(trans_id), 0, 0, hi_byte(len(rtu_data)), lo_byte(len(rtu_data))]) + rtu_data


def _wrap_res_rtu(rtu_data: (bytes, bytearray)) -> bytes:
    assert isinstance(rtu_data, (bytes, bytearray)), rtu_data

    return bytes(rtu_data + get_crc16_as_bytes(rtu_data))


def build_response_exception(req: (ModbusRequestReadWords, ModbusRequestReadBits), exc_code: int) -> bytes:
    assert isinstance(req, (ModbusRequestReadWords, ModbusRequestReadBits)), req
    assert isinstance(exc_code, int), exc_code

    if req.slave_nb < 0 or req.slave_nb > 0xff:
        raise MbError(ErrorCode.BadData)

    if req.fn_nb < 0 or req.fn_nb > 0xff:
        raise MbError(ErrorCode.BadData)

    if exc_code <= 0 or exc_code > 0xff:
        raise MbError(ErrorCode.BadData)

    resp = bytes([req.slave_nb, req.fn_nb | 0x80, exc_code])
    return _wrap_res_rtu(resp) if req.trans_id is None else _wrap_res_tcp(req.trans_id, resp)


def build_response_read_words(req: ModbusRequestReadWords, data_bytes: (bytes, bytearray)) -> bytes:
    assert isinstance(req, ModbusRequestReadWords), req
    assert isinstance(data_bytes, (bytes, bytearray)), data_bytes
    assert len(data_bytes) == (req.nb_words * 2), data_bytes

    # REPLY: Slave,Fn,NbBytes,DATA
    rtu = bytes([req.slave_nb, req.fn_nb, len(data_bytes)]) + data_bytes

    return _wrap_res_rtu(rtu) if req.trans_id is None else _wrap_res_tcp(req.trans_id, rtu)


def build_response_read_bits(req: ModbusRequestReadBits, bits) -> bytes:
    assert isinstance(req, ModbusRequestReadBits), req
    assert bits
    assert len(bits) == req.nb_bits, (bits, req.nb_bits)

    # REPLY: Slave,Fn,NbBytes,DATA
    nb_bytes = (req.nb_bits + 7) // 8
    d_bytes = bytearray()
    src_bit_idx = 0
    for i_byte in range(nb_bytes):  # pylint: disable=unused-variable
        byte_val = 0
        for i_bit in range(8):
            if bits[src_bit_idx]:
                byte_val |= 1 << i_bit
            src_bit_idx += 1
            if src_bit_idx == req.nb_bits:
                break
        d_bytes.append(byte_val)

    rtu = bytes([req.slave_nb, req.fn_nb, len(d_bytes)]) + d_bytes

    return _wrap_res_rtu(rtu) if req.trans_id is None else _wrap_res_tcp(req.trans_id, rtu)
