from __future__ import annotations

import asyncio
import io
import logging
from typing import Optional, Callable, Coroutine

from smpp.pdu.operations import BindTransceiver, SubmitSM, EnquireLink, Unbind, DeliverSM
from smpp.pdu.pdu_encoding import PDUEncoder
from smpp.pdu.pdu_types import (
    CommandId, PDUResponse, PDU, AddrTon, AddrNpi, EsmClassMode, EsmClass, EsmClassType,
    RegisteredDelivery, PriorityFlag, RegisteredDeliveryReceipt, ReplaceIfPresentFlag,
    DataCodingDefault, DataCoding, PDURequest
)
from smpp.pdu.sm_encoding import SMStringEncoder


class SmppProtocol(asyncio.Protocol):
    def __init__(self,
                 new_client_cb: Callable[[SmppProtocol, str, str], Coroutine],
                 sms_received_cb: Callable[[SmppProtocol, str, str, str], Coroutine],
                 logger=None):
        """

        Args:
            new_client_cb: called when a bind_transceiver request is received
            sms_received_cb: called when a submit_sm request is received
        """
        if not asyncio.iscoroutinefunction(new_client_cb):
            raise Exception('new_client_cb must be an async callable')

        # there is a 1:1 relationship between transport and protocol
        self.transport: Optional[asyncio.Transport] = None

        self.new_client_cb: Callable[[SmppProtocol, str, str], Coroutine] = new_client_cb
        self.sms_received_cb: Callable[
            [SmppProtocol, str, str, str], Coroutine] = sms_received_cb

        # Whether bind_transceiver has been done
        self.is_bound = False

        if not logger:
            logger = logging.getLogger('server')
        self.logger = logger

    def connection_made(self, transport: asyncio.Transport) -> None:
        self.transport = transport

    def connection_lost(self, exc: Optional[Exception]) -> None:
        if exc:
            self.logger.error(f'ERROR: {exc}')
        else:
            self.logger.warning('Closing connection')
        self.transport = None
        self.is_bound = False
        super(SmppProtocol, self).connection_lost(exc)

    def _send_PDU(self, pdu: PDU):
        self.transport.write(PDUEncoder().encode(pdu))

    def _send_request(self, request: PDURequest):
        if not self.is_bound:
            raise Exception('Cannot send request to unbound client')
        self._send_PDU(request)

    def _send_response(self, response: PDUResponse):
        self._send_PDU(response)

    async def send_deliver_sm(self, sequence_number: int, source_addr: str,
                              destination_addr: str, text: str):
        short_message = text.encode()  # TODO
        deliver_sm = DeliverSM(
            sequence_number=sequence_number,
            service_type='AWSBD',
            source_addr_ton=AddrTon.INTERNATIONAL,
            source_addr_npi=AddrNpi.ISDN,
            source_addr=source_addr,
            dest_addr_ton=AddrTon.INTERNATIONAL,
            dest_addr_npi=AddrNpi.ISDN,
            destination_addr=destination_addr,
            esm_class=EsmClass(EsmClassMode.DEFAULT, EsmClassType.DEFAULT),
            protocol_id=0,
            priority_flag=PriorityFlag.LEVEL_0,
            registered_delivery=RegisteredDelivery(
                RegisteredDeliveryReceipt.NO_SMSC_DELIVERY_RECEIPT_REQUESTED),
            replace_if_present_flag=ReplaceIfPresentFlag.DO_NOT_REPLACE,
            data_coding=DataCoding(scheme_data=DataCodingDefault.LATIN_1),
            short_message=short_message,
        )
        self._send_request(deliver_sm)

    async def on_bind_transceiver(self, request: BindTransceiver):
        await self.new_client_cb(self,
                                 request.params['system_id'],
                                 request.params['password'])
        self.is_bound = True

    async def on_submit_sm(self, request: SubmitSM):
        smstring = SMStringEncoder().decode_SM(request)
        await self.sms_received_cb(self,
                                   request.params['source_addr'],
                                   request.params['destination_addr'],
                                   smstring.str)

    async def on_enquire_link(self, request: EnquireLink):
        pass

    async def on_unbind(self, request: Unbind):
        pass

    async def request_handler(self, pdu: PDU):
        if pdu.command_id == CommandId.bind_transceiver:
            request = BindTransceiver(sequence_number=pdu.sequence_number,
                                      **pdu.params)
            coro = self.on_bind_transceiver(request)
        elif pdu.command_id == CommandId.submit_sm:
            request = SubmitSM(sequence_number=pdu.sequence_number, **pdu.params)
            coro = self.on_submit_sm(request)
        elif pdu.command_id == CommandId.enquire_link:
            request = EnquireLink(sequence_number=pdu.sequence_number, **pdu.params)
            coro = self.on_enquire_link(request)
        elif pdu.command_id == CommandId.unbind:
            request = Unbind(sequence_number=pdu.sequence_number, **pdu.params)
            coro = self.on_unbind(request)
        else:
            raise Exception(f'Command {pdu.command_id} not implemented')

        self.logger.debug(f'Request received: {request}')

        await coro

        self._send_response(request.require_ack(sequence_number=request.sequence_number))

    def data_received(self, data: bytes) -> None:

        pdu = PDUEncoder().decode(io.BytesIO(data))

        self.logger.debug(f'Command received: {pdu.command_id}')

        asyncio.create_task(self.request_handler(pdu))
