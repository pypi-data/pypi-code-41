#!/usr/bin/env python3
"""
A pre-forking SCGI server that uses file descriptor passing to off-load
requests to child worker processes.
"""

import sys
import socket
import os
import select
import time
import errno
import fcntl
import signal
import re
import traceback
from StringIO import StringIO
from scgi import passfd

def log(msg):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    sys.stderr.write('[%s] %s\n' % (timestamp, msg))

# netstring utility functions
def ns_read_size(input):
    size = ""
    while 1:
        c = input.read(1)
        if c == ':':
            break
        elif not c:
            raise IOError, 'short netstring read'
        size = size + c
    return long(size)

def ns_reads(input):
    size = ns_read_size(input)
    data = ""
    while size > 0:
        s = input.read(size)
        if not s:
            raise IOError, 'short netstring read'
        data = data + s
        size -= len(s)
    if input.read(1) != ',':
        raise IOError, 'missing netstring terminator'
    return data

def parse_env(headers):
    items = headers.split("\0")
    items = items[:-1]
    if len(items) % 2 != 0:
        raise ValueError, 'malformed headers'
    env = {}
    for i in range(0, len(items), 2):
        env[items[i]] = items[i+1]
    return env

def read_env(input):
    headers = ns_reads(input)
    return parse_env(headers)

def send_http_error(code, conn):
    if code == 503:
        title = 'Service Temporarily Unavailable'
        body = ('The server is currently unable to handle '
                'the request due to a temporary overloading. '
                'Please try again later.')
    else:
        assert 0, 'unknown HTTP error code %r' % code
    pid = os.fork()
    if pid == 0:
        response = ('Status: {code}\r\n'
                    'Content-Type: text/html; charset="utf-8"\r\n'
                    '\r\n'
                    '<html><head>'
                    '<title>{title}</title>'
                    '</head><body>'
                    '<h1>{title}</h1>'
                    '{body}'
                    '</body>').format(code=code,
                                      title=title,
                                      body=body)
        conn.sendall(response)
        conn.close()
        sys.exit(0)
    else:
        conn.close()


class Child:

    MAX_QUEUE = 15

    def __init__(self, session_id, pid, fd):
        self.session_id = session_id
        self.pid = pid
        self.fd = fd
        self.queue = []
        self.closed = False
        self.last_used = time.time()

    def log_session(self, msg):
        log('%s (session=%s)' % (msg, self.session_id))

    def get_age(self):
        return (time.time() - self.last_used)

    def close(self):
        if not self.closed:
            os.close(self.fd)
            for conn in self.queue:
                conn.close()
            del self.queue[:]
            self.closed = True

    def queue_request(self, conn):
        if len(self.queue) >= self.MAX_QUEUE:
            log('server busy error (session=%s)' % self.session_id)
            send_http_error(503, conn)
        else:
            self.queue.append(conn)

    def process(self):
        assert not self.closed
        assert self.queue
        conn = self.queue[0]
        if len(self.queue) > 1:
            log('queued request (session=%s qlen=%s fileno=%s)' %
                (self.session_id, len(self.queue), conn.fileno()))
        # Try to read the single byte written by the child.
        # This can fail if the child died or the pipe really
        # wasn't ready (select returns a hint only).  The fd has
        # been made non-blocking by spawn_child.
        try:
            ready_byte = os.read(self.fd, 1)
            if not ready_byte:
                self.log_session('null read while getting child status')
                raise IOError # child died?
            assert ready_byte == "1", repr(ready_byte)
        except socket.error, exc:
            if exc[0]  == errno.EWOULDBLOCK:
                return # select was wrong, retry
            self.log_session('error while getting child status (%s)' % exc)
            self.close()
        except (OSError, IOError):
            # child died?
            self.log_session('IOError while getting child status')
            self.close()
        else:
            try:
                passfd.sendfd(self.fd, conn.fileno())
            except IOError, exc:
                if exc.errno == errno.EPIPE:
                    # broken pipe, child died?
                    self.log_session('EPIPE passing fd to child')
                    self.close()
                else:
                    # some other error that we don't expect
                    self.log_session('IOError passing fd to child (%s)' %
                                     exc.errno)
                    raise
            else:
                # fd was apparently passed okay to the child.
                # The child could die before completing the
                # request but that's not our problem anymore.
                self.last_used = time.time()
                conn.close()
                del self.queue[0]


class SCGIHandler:

    # Subclasses should override the handle_connection method.

    def __init__(self, parent_fd):
        self.parent_fd = parent_fd

    def serve(self):
        while 1:
            try:
                os.write(self.parent_fd, "1") # indicates that child is ready
                fd = passfd.recvfd(self.parent_fd)
            except (IOError, OSError):
                # parent probably exited (EPIPE comes thru as OSError)
                raise SystemExit
            conn = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
            # Make sure the socket is blocking.  Apparently, on FreeBSD the
            # socket is non-blocking.  I think that's an OS bug but I don't
            # have the resources to track it down.
            conn.setblocking(1)
            os.close(fd)
            self.handle_connection(conn)

    def read_env(self, input):
        return read_env(input)

    def handle_connection(self, conn):
        """Handle an incoming request. This used to be the function to
        override in your own handler class, and doing so will still work.
        It will be easier (and therefore probably safer) to override
        produce() or produce_cgilike() instead.
        """
        input = conn.makefile("r")
        output = conn.makefile("w")
        env = self.read_env(input)
        bodysize = int(env.get('CONTENT_LENGTH', 0))
        try:
            self.produce(env, bodysize, input, output)
        finally:
            output.close()
            input.close()
            conn.close()

    def produce(self, env, bodysize, input, output):
        """This is the function you normally override to run your
        application. It is called once for every incoming request that
        this process is expected to handle.

        Parameters:

        env - a dict mapping CGI parameter names to their values.

        bodysize - an integer giving the length of the request body, in
        bytes (or zero if there is none).

        input - a file allowing you to read the request body, if any,
        over a socket. The body is exactly bodysize bytes long; don't
        try to read more than bodysize bytes. This parameter is taken
        from the CONTENT_LENGTH CGI parameter.

        output - a file allowing you to write your page over a socket
        back to the client.  Before writing the page's contents, you
        must write an http header, e.g. "Content-Type: text/plain\\r\\n"

        The default implementation of this function sets up a CGI-like
        environment, calls produce_cgilike(), and then restores the
        original environment for the next request.  It is probably
        faster and cleaner to override produce(), but produce_cgilike()
        may be more convenient.
        """

        # Preserve current system environment
        stdin = sys.stdin
        stdout = sys.stdout
        environ = os.environ

        # Set up CGI-like environment for produce_cgilike()
        sys.stdin = input
        sys.stdout = output
        os.environ = env

        # Call CGI-like version of produce() function
        try:
            self.produce_cgilike(env, bodysize)
        finally:
            # Restore original environment no matter what happens
            sys.stdin = stdin
            sys.stdout = stdout
            os.environ = environ


    def produce_cgilike(self, env, bodysize):
        """A CGI-like version of produce. Override this function instead
        of produce() if you want a CGI-like environment: CGI parameters
        are added to your environment variables, the request body can be
        read on standard input, and the resulting page is written to
        standard output.

        The CGI parameters are also passed as env, and the size of the
        request body in bytes is passed as bodysize (or zero if there is
        no body).

        Default implementation is to produce a text page listing the
        request's CGI parameters, which can be useful for debugging.
        """
        sys.stdout.write("Content-Type: text/plain\r\n\r\n")
        for k, v in env.items():
            print "%s: %r" % (k, v)


class SCGIServer:

    DEFAULT_PORT = 4000

    SESSION_ID_PATTERN = r'session="(?P<id>[0-9a-f]+)"'
    DEFAULT_SESSION_ID = '*unknown*'

    def __init__(self, handler_class=SCGIHandler, host="", port=DEFAULT_PORT,
                 max_children=5):
        self.handler_class = handler_class
        self.host = host
        self.port = port
        self.max_children = max_children
        self.children = {} # {session_id : Child}
        self.last_prune = 0
        self.restart = 0

    #
    # Deal with a hangup signal.  All we can really do here is
    # note that it happened.
    #
    def hup_signal(self, signum, frame):
        log('got HUP signal, scheduling restart')
        self.restart = 1

    def spawn_child(self, session_id, conn=None):
        parent_fd, child_fd = passfd.socketpair(socket.AF_UNIX,
                                                socket.SOCK_STREAM)
        # make child fd non-blocking
        flags = fcntl.fcntl(child_fd, fcntl.F_GETFL, 0)
        fcntl.fcntl(child_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        pid = os.fork()
        if pid == 0:
            if conn is not None:
                conn.close()
            os.close(child_fd)
            self.socket.close()
            for child in self.children.values():
                child.close()
            self.handler_class(parent_fd).serve()
            sys.exit(0)
        else:
            os.close(parent_fd)
            self.children[session_id] = child = Child(session_id, pid, child_fd)
            log('started child (session=%s pid=%s nchild=%s)' %
                                (session_id, pid, len(self.children)))
            return child

    def get_child(self, pid):
        for child in self.children.values():
            if child.pid == pid:
                return child
        return None

    def do_stop(self):
        # Close connections to the children, which will cause them to exit
        # after finishing what they are doing.
        for child in self.children.values():
            child.close()

    def do_restart(self):
        log('restarting child processes')
        self.do_stop()
        self.restart = 0

    def extract_session_id(self, conn):
        env = {}
        # select is necessary since even with MSG_PEEK the recv() can block
        # if there is no data available
        r, w, e = select.select([conn], [], [], 0.2)
        if r:
            headers = conn.recv(4096, socket.MSG_PEEK)
            headers = ns_reads(StringIO(headers))
            env = parse_env(headers)
            cookies = env.get('HTTP_COOKIE')
            if cookies:
                m = re.search(self.SESSION_ID_PATTERN, cookies)
                if m:
                    return m.group('id')
        else:
            log('gave up waiting to peek at session id')
        ip = env.get('HTTP_X_FORWARDED_FOR') or env.get('REMOTE_ADDR')
        if ip:
            return ip
        try:
            return conn.getpeername()[0]
        except socket.error:
            return self.DEFAULT_SESSION_ID

    def delegate_request(self, conn):
        """Pass a request fd to a child process to handle.
        """
        try:
            session_id = self.extract_session_id(conn)
        except Exception:
            log('error while extracting session id, traceback follows')
            traceback.print_exc(file=sys.stderr)
            session_id = self.DEFAULT_SESSION_ID
        child = self.children.get(session_id)
        if child is None or child.closed:
            child = self.spawn_child(session_id, conn)
        child.queue_request(conn)

    def get_listening_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        return s

    def reap_children(self):
        while 1:
            try:
                (pid, status) = os.waitpid(-1, os.WNOHANG)
            except OSError:
                break # no child process?
            if pid <= 0:
                break
            child = self.get_child(pid)
            if child is not None:
                child.close()
                del self.children[child.session_id]

    def process_children(self, ready_fds):
        reap = False
        for child in self.children.values():
            if child.closed:
                reap = True
            elif child.queue and child.fd in ready_fds:
                child.process()
        if reap:
            self.reap_children()

    def prune_children(self):
        n = len(self.children)
        if n == 0:
            return
        now = time.time()
        if now - self.last_prune < 20:
            return
        self.last_prune = now
        max_age = 7200. / n
        for child in self.children.values():
            if child.get_age() > max_age:
                log('closed old child (session=%s nchild=%s)' %
                                       (child.session_id, len(self.children)))
                child.close()
                del self.children[child.session_id]
        self.reap_children()

    def get_waiting_sockets(self):
        fds = [self.socket]
        for child in self.children.values():
            if child.queue:
                fds.append(child.fd)
        return fds

    def serve_on_socket(self, s):
        self.socket = s
        self.socket.listen(40)
        signal.signal(signal.SIGHUP, self.hup_signal)
        last_prune = time.time()
        while 1:
            try:
                r, w, e = select.select(self.get_waiting_sockets(), [], [], 5)
            except select.error, exc:
                if exc[0] == errno.EINTR:
                    continue
                raise
            if self.restart:
                self.do_restart()
            self.prune_children()
            if self.socket in r:
                try:
                    conn, addr = self.socket.accept()
                    self.delegate_request(conn)
                except socket.error, exc:
                    if exc[0] != errno.EINTR:
                        raise # something weird
                r.remove(self.socket)
            if r:
                self.process_children(r)


    def serve(self):
        self.serve_on_socket(self.get_listening_socket())


def main():
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = SCGIServer.DEFAULT_PORT
    SCGIServer(port=port).serve()

if __name__ == "__main__":
    main()
