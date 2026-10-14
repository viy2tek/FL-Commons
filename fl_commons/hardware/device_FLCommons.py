# name=FL Commons
"""Community MIDI adapter. Not affiliated with Image-Line.

Copy the prepared bundle into the user Hardware folder, then explicitly link
input/output ports. Configuration is generated separately; never commit secrets.
"""
from collections import deque

import device
import general
import transport
import ui
from flcommons_config import SECRET
from flcommons_wire.adapter import Adapter, OfficialHost
from flcommons_wire.protocol import MAX_FRAME, PREFIX

_adapter = None
_incoming = deque()


def OnInit():
    global _adapter
    _incoming.clear()
    _adapter = Adapter(OfficialHost(general, ui, transport), SECRET)


def OnDeInit():
    global _adapter
    _adapter = None
    _incoming.clear()


def OnSysEx(event):
    frame = bytes(event.sysex)
    if not frame.startswith(PREFIX):
        return
    event.handled = True
    if _adapter is not None and len(frame) <= MAX_FRAME and len(_incoming) < 16:
        _incoming.append(frame)


def OnIdle():
    if _adapter is None or not device.isAssigned():
        return
    # Defer reply to idle, avoiding reentrant send from a MIDI input callback.
    # Host/build-specific SysEx behavior still requires real FL testing.
    for _ in range(min(2, len(_incoming))):
        reply = _adapter.handle(_incoming.popleft())
        if reply is not None:
            try:
                device.midiOutSysex(reply)
            except Exception:
                print('FL Commons: MIDI output failed; inspect routing before retrying writes')
