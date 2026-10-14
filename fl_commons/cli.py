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
    updates = sub.add_parser('updates', help='Verify, stage and activate trusted compatibility updates')
    updates.add_argument('update_action', choices=('status', 'check', 'apply', 'rollback', 'policy', 'run'))
    updates.add_argument('update_arguments', nargs=argparse.REMAINDER)
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
    if args.action == 'updates':
        from . import updates as updater
        from .errors import OperationError
        try:
            if args.update_action == 'run':
                arguments = args.update_arguments
                if arguments and arguments[0] == '--':
                    arguments = arguments[1:]
                return updater.run_runtime(arguments)
            if args.update_action == 'policy':
                if len(args.update_arguments) != 1:
                    parser.error('updates policy requires manual or automatic')
                result = updater.set_update_policy(args.update_arguments[0])
            else:
                if args.update_arguments:
                    parser.error('Unexpected update arguments')
                if args.update_action == 'status':
                    result = updater.update_status()
                elif args.update_action == 'check':
                    result = updater.check_updates()
                elif args.update_action == 'apply':
                    result = updater.apply_pending()
                else:
                    if updater.host_running():
                        result = {'status': 'pending_reload', 'reason': 'Close FL normally before native rollback'}
                    else:
                        result = updater.rollback_update(updater.update_directory(), updater.validate_candidate)
            print(json.dumps(result, indent=2))
        except (OperationError, OSError) as error:
            parser.error(getattr(error, 'code', 'update_io_error') + ': ' + str(error))
        return
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
