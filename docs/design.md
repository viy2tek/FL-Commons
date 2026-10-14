# FL Commons v0.1 — API architecture, 2026-10-14

FL Commons is an independent community API for integrations with FL Studio.
It exposes documented, verified capabilities through a stable public contract.
Developers define their own integrations; API domains and data contracts are
general-purpose. Transport is an initial proof, not the complete product scope.
See [mission and capability needs](master-spec-alignment.md).
The implemented registry, protected native policy and signed updater are described
in [adaptive compatibility](adaptive-compatibility.md). The initial signed channel
contains evidenced host API profiles; it does not certify all target builds.
Project snapshots, stable object identities, dependency diagnostics, musical data
models and verified operations must distinguish live state, saved files and
inaccessible data. Preserve native integration, optional MIDI and the compatibility
target scope: FL Studio 25/26 and later. The product is the API; consumers are
external integrations. See [adaptive compatibility design](adaptive-compatibility-design.md).

The experimental native/plugin.cpp now hosts a separate loopback endpoint
inside FL, with the external official SDK. Python Client connects directly on
port 3211; no Python server or MIDI is required for this path. Only state,
Play/Pause and Stop are exposed. Idle_Public consumes a cancellable queue on
the creating thread; HTTP workers never call the host. State is unknown until
the host callback arrives. See native/README.md. Loading in FL and rejection of
unauthenticated requests were observed. The installed SDK recovered the encrypted
launcher token and read real compatibility/state snapshots. A reversed factory
parameter order was detected by the first write test and corrected to (Host, Tag),
matching the supplied SDK examples. A build-time assertion protects this ABI.
The corrected DLL completed Play-Pause-Play-Stop with callback-confirmed states.
HostVersion now reports 26001007; the build remains checked via executable metadata.

Current investigation scope is the broader software system, not an isolated search
feature. `sdk.catalog` exposes a paginated evidence inventory of the supplied SDK
dispatcher. It is independent of FL runtime, reports unverified interfaces explicitly,
and never enables arbitrary host calls. The catalog uses typed per-operation params;
other existing commands continue to require an empty params object. Full backend/source
recovery is not established by this inventory.

User direction supersedes the original implementation: FL Commons is an independent
API. There is no separate Bridge service in the main path. HTTP, authentication,
the Python SDK, capability reporting and input validation run without MIDI imports,
MIDI ports, SysEx or FL MIDI Scripting. Only the API exposes product operations.

`fl_commons.api.API` currently provides explicit direct simulation (`--demo`) and
a disconnected default. It does not claim a native connection: default capabilities
contain no music-control operations and control commands fail with `backend_unavailable`. Direct FL integration
is implemented separately in the native plugin with read/write transport evidence;
the optional --native Core mode routes known commands to that component and serves
status/catalog over one interface. FLStudio.connect() uses the plugin directly. Ghidra
and REA are research tools; successful analysis of a fixture proves no FL capability.

The Windows API now offers `host.inspect`: bounded read-only installation/process
inventory via documented OS interfaces. It does not activate music-control commands
or claim a connection to a project. The default remains `mode: disconnected`, with
this one system-inspection capability on Windows. See [direct access plan](direct-access-plan.md).

For specific occasions only, `--midi` opts into `optional_midi.MidiBackend`, retaining
the already tested MIDI implementation as a secondary integration. SDK and HTTP
have no dependency on that module. `flcommons_common.validation` provides shared
strict JSON and secret validation without importing any integration. The optional
script bundle includes the portable common and wire packages, with license notices.

The server continues to bind 127.0.0.1 only, require authentication, reject foreign
Host/browser Origin, bound bodies/connections, and avoid automatic HTTP write retries.
No arbitrary execution, patched FL executable or undocumented APIs enter the stable
implementation. MIDI-specific replay/session rules apply only to its optional path.

Verification: standalone API import must not load MIDI/wire modules; explicit demo
must work over real local HTTP; default must report disconnected without simulated
success; ports require explicit `--midi`; all prior optional-integration tests remain.

## Historical design below — superseded as the main architecture

Independent community bridge for documented FL Studio MIDI Scripting. No executable
patching, injected code, private APIs, scraping of binary internals or unrestricted
discovery. FL Commons is not affiliated with, endorsed by, or supported by Image-Line.

The Python service binds only 127.0.0.1, requires a bearer token on every endpoint,
rejects browser origins and foreign Host headers, bounds request sizes and workers.
The SDK uses the same HTTP contract. Core and simulator use only the standard library.
Optional Mido/RtMidi connect explicitly selected MIDI input/output ports. Windows users
provide their own permitted MIDI routing; no driver is redistributed or installed.

Wire: bounded ASCII JSON inside experimental/non-commercial SysEx (0x7D), protocol
1, HMAC-SHA256 authentication, timestamp expiry, correlated request/reply, boot nonce,
client sequence watermark and bounded duplicate-response cache. One RPC at a time.
Reads retry identical frames; writes never retry automatically and timeout reports
unknown outcome. Restart requires a fresh handshake. No exactly-once guarantee across
host restart, HTTP resubmission or crashes during execution.

Adapter executes only on FL event callbacks, advertises an allowlist from callable
documented functions and MIDI API version. Initial commands: transport state, start,
stop. A callable capability is not a hardware-tested compatibility claim. Incoming
commands are queued, bounded and dispatched in OnIdle; no FL calls on external threads.
Results go to the linked MIDI output. No arbitrary method invocation or Python eval.

Tests use the real codec, adapter dispatcher, RPC, HTTP server and SDK with a simulated
host and in-memory wire; separate optional backend tests check actual Mido encoding.
Physical routing and embedded FL Python require manual verification on each build.
MIT code, community contributions and transparent per-build validation records.
