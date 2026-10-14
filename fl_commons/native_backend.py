"""Closed, no-retry adapter to the separately loaded official native plugin."""
from .errors import OperationError
from .sdk import APIError, Client
from .compatibility import METHODS, builtin_profiles, resolve_operation

class NativeBackend:
    def __init__(self, client=None, profiles=None):
        self.client = client
        self.profiles = profiles

    def _client(self):
        # Reload the protected token after FL restarts; never replay a failed write.
        return self.client if self.client is not None else Client.from_native_session()

    def status(self):
        try:
            return self._client().status()
        except (OSError, ValueError):
            return {"connected": False, "mode": "disconnected", "fl_version": None}
        except APIError as error:
            if error.code in ("unavailable", "not_connected"):
                return {"connected": False, "mode": "disconnected", "fl_version": None}
            raise OperationError(error.code, str(error)) from error

    def capabilities(self):
        status = self.status()
        client = self._client() if status['connected'] else None
        advertised = self._advertised(client) if client else []
        details = self._details(status, advertised)
        available = [method for method in METHODS if details[method]['status'] in ('limited', 'experimental', 'supported')]
        return dict(status, api_version="0.1.0", compatibility="experimental" if available else "unverified",
                    capabilities=available, capability_details=details)

    def _advertised(self, client):
        try:
            methods = client.capabilities().get('capabilities')
        except APIError as error:
            raise OperationError(error.code, str(error)) from error
        if not isinstance(methods, list) or any(not isinstance(m, str) for m in methods):
            raise OperationError('protocol_error', 'Invalid native capability list')
        return methods

    def _details(self, status, advertised):
        observed = dict(status, fl_build=status.get('fl_version'))
        details = {}
        for method in METHODS:
            item = resolve_operation(method, observed, self.profiles if self.profiles is not None else builtin_profiles())
            if not status.get('connected'):
                item.update(status='temporarily_unavailable', reason='Native component is disconnected')
            elif method not in advertised:
                item.update(status='unsupported', reason='Native component does not advertise this operation')
            details[method] = dict(item, adapter='native_sdk', evidence='fl-native-transport-probe.json',
                                   restrictions='Requires compatible native contract and responsive GUI; transport can depend on focus')
        return details

    def command(self, method, params):
        if method not in METHODS:
            raise OperationError("unsupported", "Native adapter does not implement this command")
        if not isinstance(params, dict) or params:
            raise OperationError("invalid_params", "Expected empty params")
        try:
            client = self._client()
            status = client.status()
        except (OSError, ValueError) as error:
            raise OperationError("not_connected", "Native authentication session is unavailable") from error
        except APIError as error:
            raise OperationError(error.code, str(error)) from error
        if not status["connected"]:
            raise OperationError("not_connected", "FL Commons native component is not connected")
        item = self._details(status, self._advertised(client))[method]
        if item['status'] == 'unsupported':
            raise OperationError('capability_unavailable', item['reason'])
        if not status.get("gui_responsive"):
            raise OperationError("busy", "FL GUI callbacks are not currently responding")
        if item['status'] == 'temporarily_unavailable':
            raise OperationError('capability_unavailable', item['reason'])
        try:
            return client.command(method, params)
        except APIError as error:
            raise OperationError(error.code, str(error)) from error

    def close(self):
        pass
