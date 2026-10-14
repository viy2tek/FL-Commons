"""Allowlisted dispatcher; runs exclusively on FL Studio callback thread."""
import math
import os
import time
from collections import OrderedDict

from .protocol import ProtocolError, decode, encode, validate_key

METHODS = ('transport.state', 'transport.start', 'transport.stop')


class OfficialHost:
    def __init__(self, general, ui, transport):
        self.general, self.ui, self.transport = general, ui, transport

    def information(self):
        return {'fl_version': self.ui.getVersion(),
                'midi_api_version': self.general.getVersion(), 'mode': 'fl-studio'}

    def capabilities(self):
        required = {'transport.state': ('isPlaying', 'isRecording', 'getSongPos'),
                    'transport.start': ('start',), 'transport.stop': ('stop',)}
        return [method for method in METHODS if all(
            callable(getattr(self.transport, name, None)) for name in required[method])]

    def execute(self, method, params):
        if method == 'transport.state':
            return {'playing': bool(self.transport.isPlaying()),
                    'recording': bool(self.transport.isRecording()),
                    'position': self.transport.getSongPos()}
        if method == 'transport.start':
            self.transport.start()
        elif method == 'transport.stop':
            self.transport.stop()
        else:
            raise ValueError('Unsupported method')
        return None


class Adapter:
    def __init__(self, host, key):
        validate_key(key)
        self.host, self.key = host, key
        self.boot = os.urandom(16).hex()
        self.cache = OrderedDict()
        self.watermarks = {}

    def handle(self, frame):
        try:
            request = decode(frame, self.key)
        except ProtocolError:
            return None  # Unauthenticated input receives no response.
        if not self._valid_request(request):
            return None
        reply = {'kind': 'response', 'protocol': 1, 'id': request['id'],
                 'client': request['client'], 'seq': request['seq'], 'boot': self.boot}

        def fail(code, message):
            return encode(dict(reply, ok=False, error={'code': code, 'message': message}), self.key)

        if abs(time.time() - request['sent_at']) > 30:
            return fail('expired', 'Request timestamp outside 30 second window')
        method = request['method']
        if method != 'bridge.hello' and request['boot'] != self.boot:
            return fail('session_changed', 'Adapter restarted; handshake required')
        client, seq = request['client'], request['seq']
        cache_key = (client, seq)
        if cache_key in self.cache:
            original, response = self.cache[cache_key]
            if original != request:
                return fail('replay', 'Sequence reused with different request')
            return response
        if seq <= self.watermarks.get(client, 0):
            return fail('replay', 'Sequence already consumed')
        if client not in self.watermarks:
            if method != 'bridge.hello':
                return fail('handshake_required', 'Unknown client')
            if len(self.watermarks) >= 16:
                return fail('client_limit', 'Adapter client limit reached; reload script')
        self.watermarks[client] = seq
        if request['params'] != {}:
            response = fail('invalid_params', 'This method accepts an empty object only')
        else:
            try:
                capabilities = [m for m in self.host.capabilities() if m in METHODS]
                if method == 'bridge.hello':
                    result = dict(self.host.information(), boot=self.boot,
                                  protocol=1, capabilities=capabilities,
                                  adapter_version='0.1.0', compatibility='unverified')
                    response = encode(dict(reply, ok=True, result=result), self.key)
                elif method not in capabilities:
                    response = fail('unsupported', 'Capability unavailable')
                else:
                    result = self.host.execute(method, {})
                    response = encode(dict(reply, ok=True, result=result), self.key)
            except Exception:
                # A write may have run before the host raised: never invite retry.
                response = fail('host_error', 'Host operation failed; write outcome may be unknown')
        self.cache[cache_key] = (request, response)
        while len(self.cache) > 128:
            self.cache.popitem(last=False)
        return response

    @staticmethod
    def _valid_request(r):
        fields = {'kind', 'protocol', 'client', 'id', 'seq', 'boot', 'method', 'params', 'sent_at'}
        return (set(r) == fields and r['kind'] == 'request' and
                type(r['protocol']) is int and r['protocol'] == 1 and
                all(isinstance(r[k], str) and 0 < len(r[k]) <= 64
                    for k in ('client', 'id', 'method')) and
                type(r['seq']) is int and 0 < r['seq'] < 2**53 and
                (r['boot'] is None or isinstance(r['boot'], str) and len(r['boot']) <= 64) and
                isinstance(r['params'], dict) and type(r['sent_at']) in (int, float) and
                abs(r['sent_at']) <= 1e12 and
                math.isfinite(r['sent_at']))
