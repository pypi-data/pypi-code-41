# This program is free software: you can redistribute it and/or modify it under the
# terms of the Apache License (v2.0) as published by the Apache Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the Apache License for more details.
#
# You should have received a copy of the Apache License along with this program.
# If not, see <https://www.apache.org/licenses/LICENSE-2.0>.

"""Queue server/client implementation."""

# standard libs
from abc import ABC as AbstractBase, abstractmethod
from multiprocessing.managers import BaseManager
from multiprocessing import JoinableQueue
from typing import Tuple


# default connection details
ADDRESS = 'localhost', 5050
AUTHKEY = b'--BADKEY--'
MAXSIZE = 1000


class QueueServer(BaseManager):
    """Server for managing queue."""

    queue: JoinableQueue

    def __init__(self, address: Tuple[str, int] = ADDRESS, authkey: bytes = AUTHKEY, maxsize: int = MAXSIZE) -> None:
        """Initialize manager."""
        super().__init__(address=address, authkey=authkey)
        self.queue = JoinableQueue(maxsize=maxsize)
        self.register('get_queue', callable=lambda:self.queue)

    def __enter__(self) -> 'QueueServer':
        """Start the server."""
        self.start()
        return self

    def __exit__(self, *exc) -> None:
        """Shutdown the server."""
        self.shutdown()


class QueueClient(BaseManager):
    """Client connection to queue manager."""

    queue: JoinableQueue = None

    def __init__(self, address: Tuple[str, int] = ADDRESS, authkey: bytes = AUTHKEY) -> None:
        """Initialize manager."""
        super().__init__(address=address, authkey=authkey)
        self.register('get_queue')

    def __enter__(self) -> 'QueueClient':
        """Connect to the server."""
        self.connect()
        self.queue = self.get_queue()  # pylint: disable=no-member
        return self

    def __exit__(self, *exc) -> None:
        """Disconnect from the server."""
