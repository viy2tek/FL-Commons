# Adaptive Compatibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for native execution, or superpowers:subagent-driven-development if the user selects delegated execution. Implement task by task and check off the steps below.

**Goal:** Resolve FL Commons operations by observed interface capabilities and install trusted compatibility updates with rollback, targeting FL Studio 25/26 and later.

**Architecture:** A shared registry selects implemented adapters by interface requirements rather than an exact executable build. The native component reports observations and enforces the selected policy; Python preserves the public contract and never retries uncertain writes. A separate updater verifies signed artifacts, stages them outside FL and activates them only at a safe lifecycle boundary.

**Tech stack:** Existing Python 3.10+ standard library, unittest, Windows x64 C++17/MSVC, official external FL Plugin SDK. Use the optional `cryptography` dependency for Ed25519 verification; do not implement signature primitives ourselves. Reference: [official Ed25519 documentation](https://cryptography.io/en/stable/hazmat/primitives/asymmetric/ed25519/).

**Spec:** [Approved adaptive compatibility design](../../adaptive-compatibility-design.md). Approved by the user on 2026-10-14.

## Global constraints

- FL Commons is an API for integrations; no consumer application defines its scope.
- Target Windows x64 and FL Studio 25/26 and later; never claim untested builds are validated.
- Stable public operation semantics; no mandatory MIDI, Python server or research tooling in the direct path.
- Official/permitted interfaces only; no executable patches, private offsets or arbitrary function execution.
- No musical writes as automatic probes and no automatic retry of uncertain writes.
- Check declared SDK ABI compatibility before enabling host calls; unknown contracts stay unavailable.
- No signature trust established by a key received from the download itself.
- No private keys, tokens, projects or private paths in public artifacts or update requests.
- Updates run outside audio/GUI callbacks. Never close FL or overwrite a loaded DLL.
- SDK-derived binaries remain local until distribution rights are established; source/build updates must say when a local rebuild is required.

## File map

| Surface | Responsibility |
| --- | --- |
| `fl_commons/compatibility.py` (new) | Strict profile validation, candidate selection and per-operation availability |
| `fl_commons/data/compatibility.json` (new) | Built-in evidence and declared requirements, separated from SDK declaration catalog |
| `native/compatibility_policy.h` (new) | Read protected local activation policy and gate native operations |
| `native/plugin.cpp`, `native/local_api.h`, `native/setup.py` | Real host metadata, ABI preflight, diagnostics, safe installation |
| `fl_commons/sdk.py`, `native_backend.py` | Stable client behavior and capability-based resolution |
| `fl_commons/updates.py` (new) | Manifest verification, bounded download, staging, activation journal and rollback |
| `tools/sign_update.py` (new) | Maintainer signing tool using an externally stored private key |
| `fl_commons/cli.py`, `pyproject.toml` | Update policy commands and optional cryptographic dependency |
| `tests/test_compatibility.py`, `test_updates.py` (new), existing native/SDK tests | Contract and failure tests |
| `docs/adaptive-compatibility.md` (new), README translations, public API/OpenAPI/security docs | Actual delivered behavior and limitations |

## Review focus

1. New ProductVersion with the same documented interface contract: select it without falsely marking it tested (Task 1).
2. Connected plugin lacking an official callback or ABI evidence: retain diagnostics but disable affected operations (Tasks 2–3).
3. Endpoint/redirect attempts to forward credentials or fetch an untrusted artifact: reject without changing working state (Task 4).
4. Crash between staging and activation, or concurrent activation: recover one coherent previous/current state (Task 5).
5. FL restart during an uncertain write or update: do not duplicate the write, replace a loaded DLL or restore an older update revision silently (Tasks 3, 5).

## Task 1 — Registry and capability resolution

**Files:** create `fl_commons/compatibility.py`, `fl_commons/data/compatibility.json`, `tests/test_compatibility.py`.

**Interfaces:**
- `validate_profile(data: dict) -> dict` raises `OperationError` for invalid fields.
- `resolve_operation(method: str, observed: dict, profiles: list[dict]) -> dict` returns `adapter_id`, `method`, `status`, `reason`, `requirements`, `tested_builds`.
- Profile fields: `schema=1`, `adapter_id`, `runtime_contract`, `host_major_min`, `host_api_versions`, `operations`, `tested_builds`. Adapter IDs and operation mappings reference implemented registry entries only.
- Built-in evidence keeps 26.1.7.5653 as a tested build. SDK-v1 contract evidence is explicit; major >=25 alone never proves an ABI or operation.

- [ ] Write `test_product_build_change_preserves_matching_contract`: observed build changes while host API contract stays compatible; candidate is retained and new build is `experimental`, not `supported` by fabricated evidence.
- [ ] Write `test_missing_contract_and_unknown_mapping_disable_operation`: unknown ABI, missing callback, unregistered adapter, arbitrary native selector and malformed version all produce unavailable/invalid-profile results.
- [ ] Run `python -m unittest tests.test_compatibility -v`; confirm the new behavior fails before implementation.
- [ ] Implement the strict registry and deterministic selection: compatible verified candidate first, compatible implemented experimental candidate second, otherwise unavailable. Per-operation failures do not disable unrelated operations.
- [ ] Run the tests; commit the registry, data and tests.

## Task 2 — Native metadata and contract gate

**Files:** create `native/compatibility_policy.h`; modify `native/plugin.cpp`, `native/local_api.h`, `native/setup.py`, native controlled-host and setup tests.

**Consumes:** profile schema and resolution rules from Task 1.

**Produces:** authenticated compatibility metadata containing actual `fl_build`, `host_version_raw`, `runtime_contract`, callback observations, per-operation availability and diagnostic reason. Retain old response fields for SDK compatibility.

- [ ] Add controlled-host tests `test_real_build_is_reported`, `test_unverified_contract_disables_host_dispatch` and `test_read_only_probe_never_dispatches_transport`.
- [ ] Add installer fixtures for FL 25, 26 and newer builds: version detection alone no longer returns the old exact-build error; a missing compatible contract returns a distinct diagnostic and performs no installation/launch into an unknown ABI.
- [ ] Run native/setup tests and C++ assertions; confirm the new behavior fails.
- [ ] Replace the full-build literal in metadata with ProductVersion read through the existing Windows version APIs. Preserve host identity checks and factory `(Host, Tag)` signature assertion.
- [ ] Add native policy preflight. The installer writes the verified selected policy as a user-bound DPAPI record bound to the native component hash and interface contract. The component validates that binding before host calls. Protect policy with a distinct record format, not the bearer-token file.
- [ ] Gate operations inside the native handler, including direct HTTP callers. A version difference alone is not a rejection; unknown ABI evidence still prevents SDK access. State begins unknown until a real callback. Read-only probes check health, metadata and callbacks only.
- [ ] Rebuild using the external SDK; run the complete native suite. Commit only original source/tests, never the SDK or locally built DLL.

## Task 3 — SDK and Core integration

**Files:** modify `fl_commons/sdk.py`, `fl_commons/native_backend.py`, existing SDK/backend/HTTP tests.

**Consumes:** `resolve_operation(...)` and native metadata from Tasks 1–2.

**Produces:** `Client.connect(update_policy="manual")`, compatible existing `Client()` behavior, and capability metadata with availability, adapter, requirements, restrictions and evidence.

- [ ] Replace `test_unknown_build_and_invalid_params_do_not_dispatch` with separate contract tests: compatible changed build is selectable; unknown ABI is unavailable; invalid arguments still never dispatch.
- [ ] Add `test_partial_degradation_keeps_read_available` and `test_restart_or_uncertain_write_is_not_replayed`. Assert at most one POST for a write, including an update/reconnect failure.
- [ ] Run `python -m unittest discover -s tests -v`; confirm failing new assertions first.
- [ ] Remove duplicated exact-build checks from connect/backend. Use the native observations and resolver. A legacy plugin is recognized by its old profile and retained exact evidence; it must not gain capabilities simply because the new client is installed.
- [ ] Preserve method names, aliases and status fallback. Unsupported writes return `capability_unavailable`; disconnected state remains `not_connected`. Checking for an alternative candidate never replays an uncertain write.
- [ ] Run all Python tests and installed-wheel read-only smoke; commit the client/backend changes.

## Task 4 — Signed manifests and update staging

**Files:** create `fl_commons/updates.py`, `tools/sign_update.py`, `tests/test_updates.py`; modify `pyproject.toml` and third-party notices.

**Interfaces:**
- `verify_manifest(envelope: bytes, trusted_keys: dict[str, bytes], min_revision: int, now: int) -> dict`.
- `stage_update(manifest: dict, cache_dir: Path, fetch: callable) -> Path`.
- Signing envelope: strict JSON `key_id`, base64 `payload`, base64 `signature`; verify Ed25519 over `b"FLCommons-update-v1\x00" + payload_bytes` before parsing trusted payload fields.
- Payload fields: `schema=1`, positive monotonic `revision`, UTC epoch `expires_at`, `min_runtime`, `artifacts`. Each artifact has `id`, `kind`, `url`, `sha256`, `size`, `runtime_contract` and `distribution_status`.
- Artifact kinds: `adapter_profile`, `python_runtime`, `native_source`; no arbitrary executable or third-party SDK artifacts. Profiles select registered implementations; new code requires a reviewed signed runtime artifact.

- [ ] Add tests for valid signature, changed payload, unknown key, unsigned replacement key, duplicate JSON keys, expired/replayed revision and runtime mismatch. Test keys are isolated fixtures, never production roots.
- [ ] Add tests for mismatched artifact hash/size, oversized response, external redirect, download interruption and source archive traversal/symlink entries. Previously active files must be unchanged in each failure case.
- [ ] Confirm the new tests fail; implement signature verification using optional `cryptography` imported only for updates.
- [ ] Bound manifest to 64 KiB, artifacts to declared size with a 32 MiB maximum, network timeout to 5 seconds. Allow HTTPS only from the configured FL Commons GitHub release channel and its explicitly validated GitHub asset redirect hosts. Never copy bearer authentication headers to update requests.
- [ ] Require a locally pinned trusted public key. If no publisher trust root is configured, return `update_trust_unconfigured`; never silently trust a key fetched from the server. Automatic checks may report this diagnostic without breaking existing capabilities.
- [ ] Implement immutable content-addressed staging and the signing tool. Private key input is a protected external file; never print or store it in repo artifacts. The signing tool validates artifact kinds/distribution status before signing.
- [ ] Run update tests on Windows and Linux; commit source and optional dependency metadata.

## Task 5 — Activation, recovery and rollback

**Files:** extend `fl_commons/updates.py`, native installer/policy code and update/setup tests.

**Interfaces:**
- `activate_update(stage: Path, state_dir: Path, validate: callable, host_running: bool) -> dict` returns `active`, `pending_reload` or `rebuild_required`.
- `rollback_update(state_dir: Path, validate: callable) -> dict` selects an already verified retained artifact without reducing the persisted highest accepted manifest revision.
- Activation state: `schema=1`, `highest_revision`, `current`, `previous`, `pending`, `policy`, `last_check`. Referenced artifacts are verified content hashes, not arbitrary filesystem paths.

- [ ] Add tests `test_failed_activation_restores_previous`, `test_interrupted_activation_recovers_consistently`, `test_concurrent_activation_is_rejected`, `test_running_fl_only_stages_native_update` and `test_rollback_does_not_reset_replay_floor`.
- [ ] Confirm failures, then implement a process lock and replace the small activation-state file atomically on the same filesystem. Keep staged artifacts immutable. Recover an unfinished journal on the next connection.
- [ ] Profile activation revalidates read-only observations and respects the compiled adapter allowlist. Python runtime artifacts activate in a separate versioned environment/process boundary, never by mutating imported modules in place; dependency resolution must not fetch unsigned runtime code during activation.
- [ ] A native-source artifact remains staged until built with the external SDK through the documented original build procedure. Report `rebuild_required`; do not describe this as a ready binary update. Native activation waits for normal FL closure/reload, verifies the DLL/policy binding and preserves the previous DLL.
- [ ] Run update/setup tests; commit activation and rollback logic. A failed update must leave working capabilities usable.

## Task 6 — Policy, release channel and end-to-end validation

**Files:** modify CLI/SDK integration, native setup, public API/OpenAPI/security docs, README translations and CI; create `docs/adaptive-compatibility.md`.

**Consumes:** update verification/staging/activation and resolver interfaces above.

**Produces:** `fl-commons updates status|check|apply|rollback` and `fl-commons updates policy manual|automatic`. Update operations use the same engine as `Client.connect(update_policy=...)`; no FL bearer token is required to verify public update artifacts.

- [ ] Test manual policy performs no network access; automatic policy checks once per connection with a one-hour bounded cache and never runs in GUI/audio callbacks. A network failure, trust diagnostic or update error does not invalidate the existing adapter.
- [ ] Test a signed compatible profile update → bounded safe probe → activation → rejected corrupt next update → explicit rollback, using a local controlled HTTPS fixture and a trusted test key. Assert no musical writes, no real SDK redistribution and no credential/project fields in requests.
- [ ] Implement CLI diagnostics and policy persistence. Native standalone installation/launcher invokes the update engine at preparation time outside FL; direct SDK connection does not require running the Core server.
- [ ] Prepare the dedicated GitHub release channel with original signed artifacts only. Publish the selected public verification key through the reviewed client distribution; retain publisher private keys outside repository and artifacts. If production trust or artifact rights are not established, clearly report that the production feed is not activated; fixture success is not a live deployment claim.
- [ ] Document capabilities versus tested evidence, native rebuild/reload requirements, update failures and rollback. Mark the delivered subset precisely; preserve the general API purpose and all language navigation.
- [ ] Run Python/native suites, build and install the wheel, check source-only archives and perform read-only smoke against the available real FL. Compare hashes of compiled and actually loaded DLLs.
- [ ] Real transport testing only in the previously authorized disposable session with recording disarmed; do not claim FL 25 or later builds tested without the corresponding real environment. Record fixture coverage separately.
- [ ] Review the final branch, publish through a PR, wait for CI and integrate the authorized completed change. Keep metadata truthful if the production feed or native reload remains pending.

## Plan self-review and execution boundary

The six tasks cover registry resolution, native ABI/metadata enforcement, SDK routing,
signed staging, lifecycle/rollback and update policy/distribution. All five review
focus items have explicit owning tests. New interfaces above use matching names in
the consuming tasks. No task enables undocumented functions or invents new native
adapter implementations. A data-only profile cannot implement a function that the
installed runtime does not contain.

This is an implementation plan, not completed code. Compatibility with every
future build cannot be certified in advance. Native binary distribution and
production trust enrollment are explicit activation conditions, not silently
assumed accomplishments.

Recommended execution: **native in this chat**, task by task, followed by one
independent whole-branch review. The tasks share protocol and lifecycle state;
keeping implementation in one session minimizes interface drift.
