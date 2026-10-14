import argparse
import json
import os
from pathlib import Path
import shutil

from flcommons_common.validation import validate_key
from .api import API
from .server import create_server


def prepare_adapter(output, key):
    import flcommons_common
    import flcommons_wire
    validate_key(key)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    shared = Path(flcommons_wire.__file__).parent
    shutil.copytree(shared, output / 'flcommons_wire', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copytree(Path(flcommons_common.__file__).parent, output / 'flcommons_common',
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copyfile(Path(__file__).parent / 'hardware' / 'device_FLCommons.py', output / 'device_FLCommons.py')
    config = output / 'flcommons_config.py'
    config.write_text('# Local secret. Never commit or share this file.\nSECRET = ' + repr(key) + '\n', encoding='utf-8')
    os.chmod(config, 0o600)


def build_api(demo, midi, input_name, output_name, key, native=False):
    if sum((demo, midi, native)) > 1:
        raise ValueError('Choose demo or the optional MIDI integration')
    if not midi:
        if input_name or output_name:
            raise ValueError('MIDI ports require explicit --midi')
        if native:
            from .native_backend import NativeBackend
            return API(backend=NativeBackend())
        return API(demo=demo)
    if not input_name or not output_name:
        raise ValueError('Optional MIDI integration requires --input and --output')
    from .midi import MidiWire
    from .optional_midi import MidiBackend
    return MidiBackend(MidiWire(input_name, output_name), key)


def main(argv=None):
    parser = argparse.ArgumentParser(prog='fl-commons', description='FL Commons independent community API')
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('ports', help='List available MIDI ports without opening FL Studio')
    prepare = sub.add_parser('prepare-adapter', help='Create a new bundle; never modifies FL installations')
    prepare.add_argument('--output', required=True)
    serve = sub.add_parser('serve')
    serve.add_argument('--demo', action='store_true', help='Simulated host, no FL Studio connection')
    serve.add_argument('--midi', action='store_true', help='Explicitly enable optional MIDI Scripting integration')
    serve.add_argument('--native', action='store_true', help='Route commands to the official native plugin')
    serve.add_argument('--input', help='Exact MIDI input carrying replies from FL')
    serve.add_argument('--output', help='Exact MIDI output carrying requests to FL')
    serve.add_argument('--port', type=int, default=3210)
    args = parser.parse_args(argv)
    if args.action == 'ports':
        from .midi import list_ports
        print(json.dumps(list_ports(), indent=2))
        return
    token = os.environ.get('FL_COMMONS_TOKEN', '')
    midi_key = os.environ.get('FL_COMMONS_MIDI_KEY', token)
    try:
        validate_key(token)
        if args.action == 'prepare-adapter' or args.action == 'serve' and args.midi:
            validate_key(midi_key)
    except ValueError:
        parser.error('Set FL_COMMONS_TOKEN to a random ASCII secret of at least 32 characters')
    if args.action == 'prepare-adapter':
        prepare_adapter(args.output, midi_key)
        print('Adapter bundle created. Keep its local secret private.')
        return
    try:
        api = build_api(args.demo, args.midi, args.input, args.output, midi_key, native=args.native)
    except ValueError as exc:
        parser.error(str(exc))
    server = None
    try:
        server = create_server(api, token, args.port)
        print('FL Commons listening at http://127.0.0.1:' + str(server.server_address[1]), flush=True)
        print('SIMULATED HOST' if args.demo else 'OPTIONAL MIDI INTEGRATION' if args.midi
              else 'NATIVE ADAPTER — availability reported by /v1/status' if args.native
              else 'API READY — direct FL integration unavailable', flush=True)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if server is not None:
            server.server_close()
        api.close()
