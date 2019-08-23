#!/usr/bin/python3

import logging

from twisted.internet.protocol import Protocol, Factory

# Volcano
from volcano.general.bin import bytes_to_str
from volcano.general.modbus import MbExceptionCode, MbException, MbLimits, MbFunctionCode, MbError

# locals
from .mb_srv_protocol import ModbusRequestReadWords, ModbusRequestReadBits, parse_req_tcp, build_response_exception, build_response_read_words, build_response_read_bits

class DropProtocol(Protocol):
    def connectionMade(self):
        self.transport.loseConnection()


class MbConnection(Protocol):
    def __init__(self, factory, devices, env):
        self.factory_ = factory
        self.devices_ = devices
        self.rcv_buf_ = bytearray()
        self.log = logging.getLogger(env.name)

    def process_mber_mbex(self, req: (ModbusRequestReadWords, ModbusRequestReadBits)):
        slave_nb = req.slave_nb
        slave = next((x for x in self.devices_ if x.slave_nb() == slave_nb), None)
        if not slave:
            raise MbException(MbExceptionCode.MB_EXC_GATEWAY_PATHS_NA, 'Slave {} (0x{:x}) does not exist'.format(slave_nb, slave_nb))

        fn_nb = req.fn_nb
        if fn_nb in (MbFunctionCode.MB_FN_READ_OUT_BITS_1, MbFunctionCode.MB_FN_READ_IN_BITS_2):
            bits = slave.mb_read_bits_mbex(req.addr, req.nb_bits)  # can raise MbException/MbError
            return build_response_read_bits(req, bits)
        elif fn_nb in (MbFunctionCode.MB_FN_READ_OUT_WORDS_3, MbFunctionCode.MB_FN_READ_IN_WORDS_4):
            data_bytes = slave.mb_read_words_mbex(req.addr, req.nb_words)  # can raise MbException/MbError
            return build_response_read_words(req, data_bytes)
        else:
            raise MbException(MbExceptionCode.MB_EXC_ILLEGAL_FN_CODE, 'Modbus function {} is not supported'.format(fn_nb))

    def dataReceived(self, data: bytes):
        assert isinstance(data, bytes), data

        self.log.debug('R< %s', bytes_to_str(data))
        self.rcv_buf_ += data
        try:
            while self.rcv_buf_:

                # MbError, None, {}
                req = parse_req_tcp(self.rcv_buf_)  # throws
                if req is None:  # not enough data
                    if len(self.rcv_buf_) >= MbLimits.MAX_FRAME_SIZE_BYTES:
                        raise MbError('Modbus rcv buffer overflow')
                    else:
                        return

                assert isinstance(req, (ModbusRequestReadWords, ModbusRequestReadBits)), req
                assert 0 < req.size_bytes <= len(self.rcv_buf_), req

                self.rcv_buf_ = self.rcv_buf_[req.size_bytes:]

                try:
                    res = self.process_mber_mbex(req)
                    self.log.debug('S> %s', bytes_to_str(res))
                    self.transport.write(res)
                except MbException as ex:
                    self.log.warning(ex)
                    res_ba = build_response_exception(req, ex.code)
                    self.transport.write(res_ba)
        except MbError as e:
            self.log.warning(e)
            self.transport.loseConnection()

    def connectionMade(self):
        self.log.debug('Modbus client connected')

    def connectionLost(self, reason):   # pylint: disable=signature-differs
        self.log.debug('Modbus client disconnected')
        self.factory_.on_connection_lost(self)


class MbFactory(Factory):
    max_connections = None

    def __init__(self, devices, env):
        super().__init__()

        self.max_connections = env.max_con
        self.env = env
        self.devices_ = devices
        self.connections_ = []
        self.log = logging.getLogger(env.name)

    def buildProtocol(self, addr):
        if len(self.connections_) >= self.max_connections:
            self.log.warning('Max number of connections [%s] reached', self.max_connections)
            return DropProtocol()

        c = MbConnection(self, self.devices_, self.env)
        self.connections_.append(c)
        return c

    def on_connection_lost(self, con):
        self.connections_.remove(con)
