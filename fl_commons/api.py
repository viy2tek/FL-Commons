"""Standalone API; no implicit FL connection or MIDI dependencies."""
import threading
import sys

from .errors import OperationError

METHODS = ('transport.state', 'transport.start', 'transport.stop', 'transport.play_pause')


class API:
    def __init__(self, demo=False, backend=None):
        if demo and backend is not None:
            raise ValueError("Choose simulated or real backend")
        self.backend = backend
        self.demo = demo
        self.playing = False
        self.lock = threading.Lock()

    def capabilities(self):
        if self.backend is not None:
            info = self.backend.capabilities()
            return dict(info, capabilities=["sdk.catalog"] + info["capabilities"])
        operations = ['sdk.catalog'] + (list(METHODS) if self.demo else [])
        if not self.demo and sys.platform == 'win32':
            operations.append('host.inspect')
        return {'api_version': '0.1.0', 'mode': 'simulated' if self.demo else 'disconnected',
                'fl_version': None, 'compatibility': 'unverified',
                'capabilities': operations}

    def command(self, method, params):
        if not isinstance(method, str) or method not in METHODS + ('transport.play_pause', 'host.inspect', 'sdk.catalog'):
            raise OperationError('unsupported', 'Unknown API operation')
        if method == 'sdk.catalog':
            if not isinstance(params, dict) or set(params) - {'offset', 'limit', 'domain'}:
                raise OperationError('invalid_params', 'Catalog accepts offset, limit and domain only')
            from .catalog import sdk_catalog
            return sdk_catalog(**params)
        if not isinstance(params, dict) or params:
            raise OperationError('invalid_params', 'Expected an empty params object')
        if method == 'host.inspect':
            if self.demo:
                raise OperationError('unsupported', 'Host inspection is not simulated')
            from .host import inspect_host
            return inspect_host()
        if self.backend is not None:
            return self.backend.command(method, params)
        if not self.demo:
            raise OperationError('backend_unavailable', 'Direct FL Studio integration is not implemented')
        with self.lock:
            if method == 'transport.state':
                return {'playing': self.playing, 'recording': False, 'position': 0.0}
            self.playing = not self.playing if method == 'transport.play_pause' else method == 'transport.start'
            return None

    def status(self):
        if self.backend is not None:
            return self.backend.status()
        return {"connected": False, "mode": "simulated" if self.demo else "disconnected",
                "fl_version": None}

    def close(self):
        if self.backend is not None:
            self.backend.close()
