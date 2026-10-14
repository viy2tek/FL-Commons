"""Sign original update artifacts; keep the user-bound private key outside the repo."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import time

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from fl_commons.session import _dpapi
from fl_commons.updates import PREFIX, verify_manifest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--key', required=True, type=Path)
    parser.add_argument('--create-key', action='store_true')
    parser.add_argument('--public-output', type=Path)
    parser.add_argument('--payload', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    key_path = args.key.resolve()
    if key_path.is_relative_to(REPO):
        parser.error('Private signing key must remain outside the repository')
    if args.create_key:
        if key_path.exists():
            parser.error('Key exists; never silently rotate publisher trust')
        key = Ed25519PrivateKey.generate()
        raw = key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
        encrypted = _dpapi(b'FLCommons-publisher-v1\x00' + raw, True)
        key_path.parent.mkdir(parents=True, exist_ok=True)
        with key_path.open('xb') as stream:
            stream.write(encrypted)
    else:
        encrypted = key_path.read_bytes()
        if len(encrypted) > 4096:
            parser.error('Invalid protected key file')
        raw = _dpapi(encrypted, False)
        marker = b'FLCommons-publisher-v1\x00'
        if not raw.startswith(marker) or len(raw) != len(marker) + 32:
            parser.error('Invalid publisher key record')
        key = Ed25519PrivateKey.from_private_bytes(raw[len(marker):])
    public = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    key_id = hashlib.sha256(public).hexdigest()[:16]
    root = {key_id: base64.b64encode(public).decode()}
    if args.public_output:
        if args.public_output.exists() and json.loads(args.public_output.read_text()) != root:
            parser.error('Existing trust root differs; key rotation needs a verified transition')
        args.public_output.parent.mkdir(parents=True, exist_ok=True)
        args.public_output.write_text(json.dumps(root, indent=2) + '\n', encoding='utf-8')
    if args.payload:
        if not args.output:
            parser.error('Provide --output for the signed manifest')
        payload = args.payload.read_bytes()
        envelope = json.dumps({'key_id': key_id, 'payload': base64.b64encode(payload).decode(),
                               'signature': base64.b64encode(key.sign(PREFIX + payload)).decode()}).encode()
        verify_manifest(envelope, {key_id: public}, 0, int(time.time()))
        args.output.write_bytes(envelope)
    print('Publisher public key ID: ' + key_id)


if __name__ == '__main__':
    main()
