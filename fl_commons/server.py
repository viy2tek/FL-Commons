"""Small bounded loopback-only HTTP API for trusted local clients."""
import hmac
import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from flcommons_common.validation import ProtocolError, strict_json, validate_key
from . import __version__
from .errors import OperationError

MAX_BODY = 8192


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, api, token, port):
        self.api, self.token = api, validate_key(token)
        self.slots = threading.BoundedSemaphore(8)
        super().__init__(('127.0.0.1', port), Handler)

    def get_request(self):
        connection, address = super().get_request()
        connection.settimeout(5)
        return connection, address

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()


class Handler(BaseHTTPRequestHandler):
    server_version = 'FLCommons/0.1'
    sys_version = ''
    protocol_version = 'HTTP/1.0'

    def log_message(self, format, *args):
        pass  # Avoid logging Authorization, project data, or user input.

    def _json(self, status, body):
        data = json.dumps(body, allow_nan=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(data)

    def _error(self, status, code, message):
        self._json(status, {'error': {'code': code, 'message': message}})

    def _authorized(self):
        expected_host = '127.0.0.1:' + str(self.server.server_address[1])
        if self.headers.get_all('Host') != [expected_host] or 'Origin' in self.headers:
            self._error(403, 'forbidden', 'Use a direct local client')
            return False
        values = self.headers.get_all('Authorization', [])
        expected = b'Bearer ' + self.server.token
        if len(values) != 1 or not hmac.compare_digest(values[0].encode('utf-8'), expected):
            self._error(401, 'unauthorized', 'Valid bearer token required')
            return False
        return True

    def _operation_error(self, exc):
        status = {'unsupported': 422, 'invalid_params': 400, 'unavailable': 503,
                  'outcome_unknown': 504, 'session_changed': 409,
                  'handshake_required': 409, 'busy': 503,
                  'backend_unavailable': 503, 'unsupported_platform': 422,
                  'host_inspection_failed': 503}.get(exc.code, 502)
        status = {"not_connected": 503, "version_unverified": 409, "unauthorized": 401}.get(exc.code, status)
        self._error(status, exc.code, str(exc))

    def do_GET(self):
        if not self._authorized():
            return
        if self.path == '/v1/health':
            self._json(200, {'service': 'FL Commons', 'version': __version__,
                             'scope': 'service-only'})
        elif self.path == '/v1/capabilities':
            try:
                self._json(200, self.server.api.capabilities())
            except OperationError as exc:
                self._operation_error(exc)
        elif self.path == '/v1/status':
            try:
                if not hasattr(self.server.api, "status"):
                    raise OperationError("unsupported", "Status is not implemented by this adapter")
                self._json(200, self.server.api.status())
            except OperationError as exc:
                self._operation_error(exc)
        else:
            self._error(404, 'not_found', 'Unknown endpoint')

    def do_POST(self):
        if not self._authorized():
            return
        if self.path != '/v1/commands':
            self._error(404, 'not_found', 'Unknown endpoint')
            return
        if 'Transfer-Encoding' in self.headers:
            self._error(400, 'invalid_request', 'Transfer encoding is unsupported')
            return
        lengths = self.headers.get_all('Content-Length', [])
        if len(lengths) != 1 or not lengths[0].isascii() or not lengths[0].isdigit():
            self._error(411, 'length_required', 'One content length required')
            return
        if len(lengths[0]) > 8:
            self._error(413, 'too_large', 'Body exceeds 8192 bytes')
            return
        length = int(lengths[0])
        if length > MAX_BODY:
            self._error(413, 'too_large', 'Body exceeds 8192 bytes')
            return
        if self.headers.get('Content-Type', '').split(';')[0].strip().lower() != 'application/json':
            self._error(415, 'invalid_content_type', 'Use application/json')
            return
        try:
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise ProtocolError('Truncated body')
            body = strict_json(raw.decode('utf-8'))
            if (not isinstance(body, dict) or set(body) != {'method', 'params'} or
                    not isinstance(body['method'], str) or len(body['method']) > 64 or
                    not isinstance(body['params'], dict)):
                raise ProtocolError('Expected method string and params object')
        except (ProtocolError, UnicodeError, socket.timeout):
            self._error(400, 'invalid_request', 'Invalid command JSON or incomplete body')
            return
        try:
            result = self.server.api.command(body['method'], body['params'])
            self._json(200, {'result': result})
        except OperationError as exc:
            self._operation_error(exc)


def create_server(api, token, port=3210):
    return LocalServer(api, token, port)
