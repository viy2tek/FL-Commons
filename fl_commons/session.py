"""User-bound Windows DPAPI storage for the native launcher's bearer token."""
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import re
import sys
import tempfile


def session_path():
    if sys.platform != "win32":
        raise OSError("Native session storage requires Windows")
    return Path(os.environ["LOCALAPPDATA"]) / "FLCommons/native-session.bin"


def _validate(token):
    if not isinstance(token, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{32,256}", token):
        raise ValueError("Native token must contain 32..256 ASCII letters, digits, underscore or hyphen")


def _dpapi(data, protect):
    if sys.platform != "win32":
        raise OSError("DPAPI requires Windows")
    class Blob(ctypes.Structure):
        _fields_ = [("size", wintypes.DWORD), ("data", ctypes.POINTER(ctypes.c_ubyte))]

    buffer = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
    source, result = Blob(len(data), buffer), Blob()
    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    function = crypt32.CryptProtectData if protect else crypt32.CryptUnprotectData
    function.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.c_void_p,
                         ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
    function.restype = wintypes.BOOL
    if not function(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(result)):
        raise ctypes.WinError(ctypes.get_last_error())
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p
    try:
        return ctypes.string_at(result.data, result.size)
    finally:
        kernel32.LocalFree(result.data)


def save_token(token, path):
    _validate(token)
    encrypted = _dpapi(token.encode("ascii"), True)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(encrypted)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def read_token(path):
    with Path(path).open("rb") as stream:
        encrypted = stream.read(4097)
    if not encrypted or len(encrypted) > 4096:
        raise OSError("Invalid native session file")
    token = _dpapi(encrypted, False).decode("ascii")
    _validate(token)
    return token
