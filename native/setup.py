"""Install the original native plugin without overwriting; optionally launch FL."""
import argparse
import hashlib
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fl_commons.host import inspect_host
from fl_commons.session import save_token, session_path
from fl_commons.compatibility import builtin_profiles, select_install_profile, save_native_policy, host_api_from_build
from fl_commons.errors import OperationError

def install_plugin(binary, installation):
    binary, installation = Path(binary).resolve(strict=True), Path(installation).resolve(strict=True)
    if binary.name != "FL Commons API.dll" or binary.read_bytes()[:2] != b"MZ":
        raise ValueError("Expected compiled FL Commons API.dll")
    effects = installation / "Plugins/Fruity/Effects"
    if not effects.is_dir() or effects.resolve() != effects:
        raise ValueError("Expected native effects directory without redirected paths")
    directory = effects / "FL Commons API"
    if directory.is_symlink() or (directory.exists() and directory.resolve() != directory):
        raise ValueError("Redirected plugin directory refused")
    directory.mkdir(exist_ok=True)
    destination = directory / "FL Commons API_x64.dll"
    content = binary.read_bytes()
    if destination.exists():
        if not destination.is_symlink() and destination.read_bytes() == content:
            return destination
        raise FileExistsError("Another plugin version exists; preserve it before updating")
    with destination.open("xb") as stream:
        stream.write(content)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dll", required=True, type=Path)
    parser.add_argument("--launch", action="store_true")
    args = parser.parse_args()
    inventory = inspect_host()
    try:
        profile = select_install_profile(inventory['selected_version'], builtin_profiles())
    except OperationError as error:
        parser.error(str(error))
    if inventory["processes"]:
        parser.error("FL is already running; close it normally before setup")
    candidates = [entry for entry in inventory["installations"]
                  if Path(entry["path"]).name.lower() == "fl64.exe"]
    if len(candidates) != 1:
        parser.error("Expected exactly one latest standard FL64.exe")
    executable = Path(candidates[0]["path"])
    token = os.environ.get("FL_COMMONS_TOKEN") or secrets.token_hex(32)
    if args.launch and not re.fullmatch(r"[a-zA-Z0-9_-]{32,256}", token):
        parser.error("FL_COMMONS_TOKEN is invalid")
    destination = install_plugin(args.dll, executable.parent)
    save_native_policy(destination, profile, host_api_from_build(inventory['selected_version']),
                       session_path().with_name('native-policy.bin'))
    print("Installed: " + str(destination))
    print("SHA256: " + hashlib.sha256(destination.read_bytes()).hexdigest())
    if args.launch:
        save_token(token, session_path())
        subprocess.Popen([str(executable)], cwd=executable.parent,
                         env=dict(os.environ, FL_COMMONS_TOKEN=token))
        print("FL started; token stored with Windows DPAPI. Load FL Commons API in a free Mixer slot")


if __name__ == "__main__":
    main()
