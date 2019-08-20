from smppy.server import SmppProtocol


class Client:
    def __init__(self, system_id: str, protocol: SmppProtocol):
        self.system_id: str = system_id
        self.protocol: SmppProtocol = protocol
        self._sequence_number: int = 1

    def next_sequence_number(self):
        self._sequence_number += 1
        return self._sequence_number

    async def send_sms(self, source: str, dest: str, text: str) -> None:
        await self.protocol.send_deliver_sm(
            sequence_number=self.next_sequence_number(),
            source_addr=source,
            destination_addr=dest,
            text=text
        )
