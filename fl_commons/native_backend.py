"""Closed, no-retry adapter to the separately loaded official native plugin."""
from .errors import OperationError
from .sdk import APIError, Client

METHODS = ("transport.state", "transport.play_pause", "transport.stop")
TARGET = "26.1.7.5653"


class NativeBackend:
    def __init__(self, client=None):
        self.client = client

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
        available = status["connected"] and status.get("fl_version") == TARGET
        details = {method: {
            "status": "limited" if available else "temporarily_unavailable",
            "adapter": "native_sdk",
            "tested_build": TARGET,
            "evidence": "fl-native-transport-probe.json",
            "restrictions": "Requires loaded native plugin; host focus can affect transport",
        } for method in METHODS}
        return dict(status, api_version="0.1.0", compatibility="experimental" if available else "unverified",
                    capabilities=list(METHODS) if available else [], capability_details=details)

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
        if status.get("fl_version") != TARGET:
            raise OperationError("version_unverified", "Native build is not verified for this adapter")
        if not status.get("gui_responsive"):
            raise OperationError("busy", "FL GUI callbacks are not currently responding")
        try:
            return client.command(method, params)
        except APIError as error:
            raise OperationError(error.code, str(error)) from error

    def close(self):
        pass
