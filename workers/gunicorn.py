import asyncio
import sys
from functools import partial
from io import BytesIO

from gunicorn.workers.base import Worker as BaseWorker
from http_parser.parser import HttpParser

class DummyApp(object):

    def wsgi(self):
        return None

class Request(object):

    def __init__(self, parser, data):
        self.method  = parser.get_method()
        self.headers = parser.get_headers()
        self.body    = parser.recv_body()
        self.path    = parser.get_path()
        self.data    = data
        self.query_string = parser.get_query_string()

class Worker(BaseWorker):

    app  = DummyApp()
    loop = None

    def init_process(self):
        asyncio.get_event_loop().close()

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        for sock in self.sockets:
            coroutine = asyncio.start_server(self._parse_request, sock=sock)
            server = self.loop.run_until_complete(coroutine)

        super().init_process()

    def run(self):
        self.notify()
        self.loop.run_forever()

    def _parse_request(self, reader, writer):
        p = HttpParser()
        body = []
        while True:
            data = yield from reader.read(1024)
            if not data:
                break

            recved = len(data)
            nparsed = p.execute(data, recved)
            assert nparsed == recved

            # if p.is_headers_complete():
            #     print(p.get_headers())

            # if p.is_partial_body():
            #     body.append(p.recv_body())

            if p.is_message_complete():
                break

        request = Request(p, data)
        yield from self.handle_request((reader, writer), request)

    def get_environ(self, request):
        env = {}
        env['wsgi.version']      = (1, 0)
        env['wsgi.url_scheme']   = 'http'
        env['wsgi.input']        = BytesIO(request.body)
        env['wsgi.errors']       = sys.stderr
        env['wsgi.multithread']  = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once']     = False
        env['REQUEST_METHOD']    = request.method
        env['PATH_INFO']         = request.path
        env['SERVER_NAME']       = "localhost"
        env['SERVER_PORT']       = "8000"
        env['QUERY_STRING']     = request.query_string

        for hdr_name, hdr_value in request.headers.items():
            if hdr_name == "Content-Type":
                env['CONTENT_TYPE'] = hdr_value
                continue
            elif hdr_name == "Content-Length":
                env['CONTENT_LENGTH'] = hdr_value
                continue

            key = 'HTTP_' + hdr_name.upper().replace('-', '_')
            if key not in env:
                env[key] = hdr_value

        return env

    def start_response(self, status, response_headers, exc_info=None):
        server_headers = [
            ('Date', 'Wed, 17 May 2017 12:54:48 GMT'),
            ('Server', 'WSGIServer 0.2'),
        ]
        self.headers_set = [status, response_headers + server_headers]

    def send_response(self, streams, result):
        reader, writer = streams
        try:
            status, response_headers = self.headers_set
            head = 'HTTP/1.1 {status}\r\n'.format(status=status)
            for header in response_headers:
                head += '{0}: {1}\r\n'.format(*header)
            head += '\r\n'
            head = bytes(head, "utf-8")
            writer.write(head)

            if hasattr(result, "async") and result.async:
                channel = Channel(streams)
                yield from result.callback(channel)
            else:
                for data in result:
                    writer.write(data)
        finally:
            writer.transport.close()

    def async_response_writer(self, streams, data):
        reader, writer = streams
        writer.write(bytes(data, "utf-8"))

    @asyncio.coroutine
    def handle_request(self, streams, request):
        reader, writer = streams

        env = self.get_environ(request)

        # It's time to call our application callable and get
        # back a result that will become HTTP response body
        #start_response = partial(self.start_response, (reader, writer))
        result = self.wsgi(env, self.start_response)
        if asyncio.iscoroutine(result):
            result = yield from result

        # Construct a response and send it back to the client
        yield from self.send_response((reader, writer), result)

        print("notify")
        self.notify()


class Channel(object):

    def __init__(self, streams):
        self.reader, self.writer = streams

    def send(self, data):
        self.writer.write(bytes(data, "utf-8"))

