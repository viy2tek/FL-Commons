"""Initial synchronous Python SDK. Requests never retry automatically."""
import http.client
import json

from flcommons_common.validation import ProtocolError, strict_json, validate_key


class APIError(RuntimeError):
    def __init__(self, status, code, message):
        super().__init__(message)
        self.status, self.code = status, code


class Client:
    @classmethod
    def connect(cls, update_policy="manual"):
        """Connect directly to the official native plugin, without a Python server."""
        try:
            client = cls.from_native_session()
        except (OSError, ValueError) as error:
            raise APIError(0, "not_connected", "Native launcher session is unavailable") from error
        status = client.status()
        if not status["connected"]:
            raise APIError(0, "not_connected", "Load FL Commons API inside FL Studio")
        if update_policy not in ('manual', 'automatic'):
            raise ValueError('Update policy must be manual or automatic')
        from .native_backend import NativeBackend
        details = NativeBackend(client)._details(status, client.capabilities().get('capabilities', []))
        if not any(item['adapter_id'] for item in details.values()):
            raise APIError(409, "capability_unavailable", "No adapter matches the observed native contract")
        return client

    @property
    def transport(self):
        return Transport(self)

    @classmethod
    def from_native_session(cls):
        """Read the current Windows user's encrypted launcher token."""
        from .session import read_token, session_path
        return cls(read_token(session_path()), port=3211)

    def __init__(self, token, port=3210, timeout=20):
        validate_key(token)
        self.token, self.port, self.timeout = token, port, timeout

    def _request(self, method, path, body=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=self.timeout)
        headers = {'Authorization': 'Bearer ' + self.token}
        data = None
        if body is not None:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(body, allow_nan=False).encode('utf-8')
        try:
            connection.request(method, path, body=data, headers=headers)
            response = connection.getresponse()
            raw = response.read(16385)
            if len(raw) > 16384:
                raise APIError(502, 'protocol_error', 'HTTP response exceeds limit')
            content = strict_json(raw)
            if not isinstance(content, dict):
                raise APIError(502, "protocol_error", "Expected an object response")
            if response.status != 200:
                error = content.get('error', {})
                if not isinstance(error, dict):
                    raise APIError(502, "protocol_error", "Invalid error response")
                raise APIError(response.status, error.get('code', 'http_error'),
                               error.get('message', 'HTTP request failed'))
            return content
        except ProtocolError as exc:
            raise APIError(502, "protocol_error", "Invalid JSON response") from exc
        except (OSError, http.client.HTTPException) as exc:
            code = 'outcome_unknown' if method == 'POST' else 'unavailable'
            message = 'HTTP connection failed; writes may have executed' if method == 'POST' else 'HTTP connection failed'
            raise APIError(0, code, message) from exc
        finally:
            connection.close()

    def health(self):
        return self._request('GET', '/v1/health')

    def status(self):
        try:
            return self._request("GET", "/v1/status")
        except APIError as error:
            if error.status != 404:
                if error.code == "unavailable":
                    return {"connected": False, "mode": "disconnected", "fl_version": None}
                raise
        # Existing native v0.1 plugins expose this information at compatibility.
        try:
            profile = self.compatibility()
        except APIError as error:
            if error.code == "unavailable":
                return {"connected": False, "mode": "disconnected", "fl_version": None}
            raise
        return {"connected": profile.get("mode") == "fl-native", "mode": profile.get("mode"),
                "fl_version": profile.get("fl_build"), "session_id": profile.get("session_id"),
                "gui_responsive": profile.get("gui_responsive", False),
                "host_version_raw": profile.get('host_version_raw'),
                "state_callback_observed": profile.get('state_callback_observed', False),
                "runtime_contract": profile.get('runtime_contract', 'fpsdk-20210311b-v1' if profile.get('profile') == 'fpsdk-20210311b-transport-v1' else None),
                "compatibility": "experimental"}

    def capabilities(self):
        return self._request('GET', '/v1/capabilities')

    def compatibility(self):
        """Read native session evidence; observations do not certify compatibility."""
        return self._request('GET', '/v1/compatibility')

    def inspect_host(self):
        return self.command('host.inspect')

    def sdk_catalog(self, domain=None, offset=0, limit=32):
        params = {'offset': offset, 'limit': limit}
        if domain is not None:
            params['domain'] = domain
        return self.command('sdk.catalog', params)

    def command(self, method, params=None):
        response = self._request('POST', '/v1/commands',
                                 {'method': method, 'params': {} if params is None else params})
        if "result" not in response:
            raise APIError(502, "protocol_error", "Command response has no result")
        return response["result"]


class Transport:
    def __init__(self, client):
        self.client = client

    def state(self):
        return self.client.command("transport.state")

    def play_pause(self):
        return self.client.command("transport.play_pause")

    def stop(self):
        return self.client.command("transport.stop")
