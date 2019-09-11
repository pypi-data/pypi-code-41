import sys
import scgi_server

class ResponseHeader:
    def __init__(self, output):
        self.needed = True
        self.output = output
        self.status = None
        self.headers = []

    def write(self):
        assert self.status is not None
        if self.needed:
            self.output.write('Status: %s\r\n' % self.status)
            for k, v in self.headers:
                self.output.write('%s: %s\r\n' % (k, v))
            self.output.write('\r\n')
            self.needed = False


class Handler(scgi_server.SCGIHandler):

    def __init__(self, parent_fd, app):
        scgi_server.SCGIHandler.__init__(self, parent_fd)
        self.app = app

    def produce(self, env, bodysize, input, output):
        if (env.get('HTTPS', 'off').lower() in ('on', 'yes', '1') or
                env.get('SERVER_PORT_SECURE', '0') != '0'):
            scheme = "https"
        else:
            scheme = "http"
        env.update({
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': scheme,
            'wsgi.input': input,
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': 0,
            'wsgi.multiprocess': 1,
            'wsgi.run_once': 1,
            })
        header = ResponseHeader(output)
        def start_response(status, response_headers, exc_info=None):
            #print 'start_response', status, response_headers
            def write_data(body):
                header.write()
                output.write(body)
            header.status = status
            header.headers = response_headers
        for chunk in self.app(env, start_response):
            #print 'chunk', `chunk`
            header.write()
            output.write(chunk)
        header.write() # if app returns empty sequence
        #print 'done'



def handler_factory(app):
    def make_handler(parent_fd):
        return Handler(parent_fd, app)
    return make_handler


def run(app):
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = scgi_server.SCGIServer.DEFAULT_PORT
    print 'scgi server running on %s:%s' % ('localhost', port)
    scgi_server.SCGIServer(handler_class=handler_factory(app),
                           port=port).serve()
