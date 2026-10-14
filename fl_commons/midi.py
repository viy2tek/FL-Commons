"""Explicit MIDI ports via optional MIT-licensed Mido and python-rtmidi."""
import queue

from flcommons_wire.protocol import MAX_FRAME


def backend():
    try:
        import mido
        return mido, mido.Backend('mido.backends.rtmidi')
    except ImportError as exc:
        raise RuntimeError('Install fl-commons[midi] in your environment to use MIDI ports') from exc


def list_ports():
    _, provider = backend()
    return {'inputs': provider.get_input_names(), 'outputs': provider.get_output_names()}


class MidiWire:
    def __init__(self, input_name, output_name):
        self.mido, provider = backend()
        if provider.get_input_names().count(input_name) != 1 or provider.get_output_names().count(output_name) != 1:
            raise ValueError('Choose one exact, unambiguous input and output port name')
        self.queue = queue.Queue(maxsize=128)
        self.closed = False
        self.output = provider.open_output(output_name)
        try:
            self.input = provider.open_input(input_name, callback=self._received)
        except BaseException:
            self.output.close()
            raise

    def _received(self, message):
        if self.closed or message.type != 'sysex':
            return
        frame = bytes(message.bytes())
        if len(frame) > MAX_FRAME:
            return
        try:
            self.queue.put_nowait(frame)
        except queue.Full:
            pass  # Bounded loss; RPC read retries or explicit write timeout handle it.

    def send(self, frame):
        if self.closed:
            raise OSError('MIDI ports are closed')
        self.output.send(self.mido.Message('sysex', data=list(frame[1:-1])))

    def receive(self, timeout):
        if self.closed:
            raise OSError('MIDI ports are closed')
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def close(self):
        self.closed = True
        try:
            self.input.close()
        finally:
            self.output.close()
