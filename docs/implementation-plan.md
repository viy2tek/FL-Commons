# FL Commons v0.1 Implementation Plan

Historical completed plan for the first implementation. The 2026-10-14 user
direction supersedes its main architecture: API independent of MIDI, direct demo,
explicit disconnected default, optional MIDI only. See [current design](design.md).

Goal: a runnable local Bridge, initial Python SDK and installable MIDI script bundle.
Spec: [design.md](design.md). Execution: inline in the current session, authorized by
the implementation request. No external repository creation or publication required.

- [x] Protocol and adapter: write tests for signed round-trip, tampering, bounds,
  duplicate writes, expired requests, host restart and unavailable functions. Implement
  `flcommons_wire/protocol.py`, `adapter.py` and FL callback entry point.
- [x] RPC and MIDI backend: test dropped replies, invalid replies, timeouts and write
  ambiguity. Implement bounded serial requests and explicit ports via optional Mido.
- [x] HTTP and SDK: real loopback integration tests cover token, Host/Origin rejection,
  JSON validation, command errors, capability catalog and SDK execution.
- [x] CLI, simulator and bundle: executable demo, key preparation without touching FL,
  packaging metadata, contributor docs, MIT license, third-party notices and CI.
- [x] Run full suite, compilation, package build/install and simulator smoke; record
  evidence and actual limits. Initialize local Git and deliver source archive.

Review focus: unauthorized MIDI; replay after cache eviction; mutation reply loss;
bounded socket/worker lifetime; restart invalidates commands; simulator not mistaken
for FL compatibility; no dependency or secret silently bundled into repository.
