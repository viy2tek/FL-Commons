"""Explicit demo host, never evidence of FL Studio compatibility."""
import queue

from flcommons_wire.adapter import Adapter, METHODS


class SimulatedHost:
    def __init__(self):
        self.playing = False

    def information(self):
        return {'fl_version': None, 'midi_api_version': None, 'mode': 'simulated'}

    def capabilities(self):
        return list(METHODS)

    def execute(self, method, params):
        if method == 'transport.state':
            return {'playing': self.playing, 'recording': False, 'position': 0.0}
        self.playing = method == 'transport.start'
        return None


class SimulatedWire:
    def __init__(self, key):
        self.adapter = Adapter(SimulatedHost(), key)
        self.queue = queue.Queue(maxsize=128)

    def send(self, frame):
        reply = self.adapter.handle(frame)
        if reply is not None:
            self.queue.put_nowait(reply)

    def receive(self, timeout):
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def close(self):
        pass
