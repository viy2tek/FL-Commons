"""Serialized authenticated RPC with read-only retry and explicit write ambiguity."""
import threading
import time
import uuid
from contextlib import contextmanager

from flcommons_wire.adapter import METHODS
from flcommons_wire.protocol import ProtocolError, decode, encode, validate_key

READS = {'bridge.hello', 'transport.state'}


from .errors import OperationError


class MidiBackend:
    def __init__(self, wire, key, timeout=1.5, read_attempts=3):
        validate_key(key)
        if not 0 < timeout <= 5 or not 1 <= read_attempts <= 3:
            raise ValueError('Invalid timeout/retry settings')
        self.wire, self.key = wire, key
        self.timeout, self.read_attempts = timeout, read_attempts
        self.client = uuid.uuid4().hex
        self.sequence = 0
        self.info = None
        self.lock = threading.RLock()

    @contextmanager
    def _operation(self):
        if not self.lock.acquire(timeout=self.timeout):
            raise OperationError('busy', 'Another MIDI operation is in progress; no command sent')
        try:
            yield
        finally:
            self.lock.release()

    def capabilities(self):
        with self._operation():
            info = self._call('bridge.hello', {}, None)
            if (not isinstance(info, dict) or info.get('protocol') != 1 or
                    not isinstance(info.get('boot'), str) or not info['boot'] or
                    not isinstance(info.get('capabilities'), list) or
                    not all(m in METHODS for m in info['capabilities'])):
                self.info = None
                raise OperationError('protocol_error', 'Invalid capability handshake')
            self.info = info
            return dict(info)

    def command(self, method, params):
        if not isinstance(method, str) or method not in METHODS:
            raise OperationError('unsupported', 'Unknown capability')
        if not isinstance(params, dict) or params:
            raise OperationError('invalid_params', 'Expected an empty params object')
        with self._operation():
            if self.info is None:
                self.capabilities()
            if method not in self.info['capabilities']:
                raise OperationError('unsupported', 'Capability unavailable on connected adapter')
            return self._call(method, params, self.info['boot'])

    def _call(self, method, params, boot):
        self.sequence += 1
        request = dict(kind='request', protocol=1, client=self.client,
                       id=uuid.uuid4().hex, seq=self.sequence, boot=boot,
                       method=method, params=params, sent_at=time.time())
        frame = encode(request, self.key)
        attempts = self.read_attempts if method in READS else 1
        for _ in range(attempts):
            try:
                self.wire.send(frame)
                deadline = time.monotonic() + self.timeout
                while time.monotonic() < deadline:
                    response = self.wire.receive(max(0, deadline - time.monotonic()))
                    if response is None:
                        break
                    try:
                        reply = decode(response, self.key)
                    except ProtocolError:
                        continue
                    if (reply.get('kind') != 'response' or reply.get('protocol') != 1 or
                            any(reply.get(k) != request[k] for k in ('id', 'client', 'seq'))):
                        continue
                    if type(reply.get('ok')) is not bool:
                        continue
                    if reply['ok']:
                        if boot is not None and reply.get('boot') != boot:
                            self.info = None
                            raise OperationError('session_changed', 'Unexpected adapter session')
                        if 'result' not in reply:
                            continue
                        return reply['result']
                    error = reply.get('error')
                    if not isinstance(error, dict) or not isinstance(error.get('code'), str):
                        continue
                    if error['code'] in ('session_changed', 'handshake_required'):
                        self.info = None
                    raise OperationError(error['code'], str(error.get('message', 'Adapter error')))
            except (OSError, RuntimeError) as exc:
                if isinstance(exc, OperationError):
                    raise
                self.info = None
                code = 'unavailable' if method in READS else 'outcome_unknown'
                raise OperationError(code, 'MIDI transport failed; reconnect ports') from exc
        self.info = None
        if method not in READS:
            raise OperationError('outcome_unknown', 'No write reply; inspect host before resubmitting')
        raise OperationError('unavailable', 'No authenticated reply from adapter')

    def close(self):
        with self.lock:
            self.wire.close()
