# Adaptive compatibility and trusted updates

FL Commons resolves operations against implemented adapters and observed official
interface contracts. The target is FL Studio 25/26 and later on Windows x64.
A matching ProductVersion alone does not prove an ABI or operation.

## Delivered behavior

The registry maps the three existing transport operations to implemented native
methods. Unknown selectors, adapters and contracts are rejected. The new native
component reads real build metadata and checks the host interface version and a
protected policy bound to its DLL hash. Capabilities distinguish tested evidence,
experimental matching contracts, missing callbacks and unavailable operations.
Direct SDK calls and the optional Core respect that policy. Uncertain writes
are never retried after updates or reconnects.

The initial evidence covers host interface `26001007` and the real transport test
on `26.1.7.5653`. Another build with that contract is experimental, not certified.
Other host interfaces need verified profiles; no FL 25 runtime test is claimed.
The old loaded DLL still has its original exact-build restriction. Updating the
Python package does not replace a loaded DLL: build/reload the new component.
Host inventory retains all discovered FL25+ installations and every named FL
process, including unresolved process paths. Native setup defaults to the latest
installation; use `--installation 'C:/path/to/FL64.exe'` to select another discovered
installation. A running older FL instance still blocks activation.

## Update policy

```powershell
python -m pip install ".[updates]"
fl-commons updates status
fl-commons updates policy automatic
fl-commons updates check
fl-commons updates apply
```

Manual is the initial policy. Automatic checks occur at SDK connection or native
launcher preparation with a one-hour cache. No checks execute in audio/GUI callbacks.

```python
from flcommons import FLStudio
fl = FLStudio.connect(update_policy="automatic")
print(fl.update_diagnostic)
```

Use `update_policy="manual"` for no automatic network access. Omit the argument to
preserve stored policy. A channel failure preserves the active adapter. No bearer
token, project or private machine path is sent; ordinary HTTPS network metadata
is still visible to the hosting service.

Apply while FL is running reports `pending_reload`. Close FL normally and preserve
your work before applying and preparing the next native session. Source updates
report `rebuild_required`; they do not redistribute the external SDK or a DLL under
an inferred MIT grant. Build locally, preserving the previous DLL.

```powershell
fl-commons updates rollback
python native/setup.py --dll 'C:/path/to/build/FL Commons API.dll' --updates automatic --launch
```

A signed original Python runtime activates for a new process; already imported
modules remain intact. `fl-commons updates run -- serve --native` starts it from
freshly verified bytes, without fetching dependencies or running install scripts.

## Trust and recovery

The dedicated `compatibility-v1` data branch provides the initial channel:

- [Signed manifest](https://raw.githubusercontent.com/viy2tek/FL-Commons/compatibility-v1/updates/manifest.json)
- [Original profiles](https://raw.githubusercontent.com/viy2tek/FL-Commons/compatibility-v1/updates/profiles.json)

Ed25519 signatures, expiry, monotonic revisions, SHA-256 hashes and size limits
protect downloads. Only configured repository URLs and permitted GitHub asset
hosts are accepted. Foreign redirects, credential URLs, unknown keys, altered
files, old revisions and unsafe archives are rejected. Maintainers must renew
the signed feed before its expiry; an expired feed cannot install new updates.

The packaged `fl_commons/data/update-root.json` pins the public verification key.
An explicit local `root.json` in the update directory overrides it. A downloaded
manifest cannot replace the root. Missing trust reports `update_trust_unconfigured`.
Publisher keys live outside the repository, protected by Windows DPAPI. The
signing tool refuses silent rotation; a new key needs a separately reviewed
transition. DPAPI does not protect against other processes of the same user.

Immutable staging, an OS lock and an atomic state pointer retain current,
previous and pending artifacts. Interrupted activation resumes safely. Rollback
uses a retained verified artifact and preserves the highest accepted revision.
The updater never closes FL, discards a project or overwrites a loaded DLL.

## Limits and evidence

Updates select implemented alternatives. They do not infer unknown proprietary
functions or install unreviewed generated code. A profile cannot create a method
absent from the compiled runtime. Transport is the only native operation family.

[adaptive-api-smoke.json](../research/adaptive-api-smoke.json) records real HTTPS
signature verification/staging with no musical writes. It does not prove that
the new DLL was loaded in FL. Controlled fixtures and real host evidence remain
separate.
