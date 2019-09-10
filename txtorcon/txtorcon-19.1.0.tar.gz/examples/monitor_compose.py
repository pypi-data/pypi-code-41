#!/usr/bin/env python

# Just listens for a few EVENTs from Tor (INFO NOTICE WARN ERR) and
# prints out the contents, so functions like a log monitor.

from __future__ import print_function

from twisted.internet import task, defer
from twisted.internet.endpoints import UNIXClientEndpoint
import txtorcon


@task.react
@defer.inlineCallbacks
def main(reactor):
    ep = UNIXClientEndpoint(reactor, '/var/run/tor/control')
    tor = yield txtorcon.connect(reactor, ep)

    def log(msg):
        print(msg)
    print("Connected to a Tor version", tor.protocol.version)

    state = yield tor.create_state()

    print(dir(state))
    @state.on_stream_new
    def _(circ):
        print("new stream: {}".format(circ))

    yield defer.Deferred()
