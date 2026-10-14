# Adaptive compatibility — design for review

## Product definition

FL Commons is an independent community API for integrations with FL Studio.
Developers define their own integrations. The public API exposes capabilities,
data and operations; it is not designed around particular consumer applications.

## Compatibility scope

The compatibility target is Windows x64 with FL Studio 25/26 and later, rather
than a single ProductVersion. The existing test on 26.1.7.5653 is evidence for
that environment, not a prerequisite imposed on the product's intended users.
No untested version is described as validated.

The current native component, installer, Python connect() and NativeBackend
all contain exact-build restrictions. Changing README wording alone cannot
make them adaptive. These four entry points must change together.

## Contract and discovery

The public operation identifier and semantics remain stable. Installation/build,
SDK host version, available official callbacks and actual responses are observed.
Every capability records its implementation, availability, validation level and
restrictions. Version discovery and behavior verification are separate facts.

Discovery uses interfaces that expose supported methods or capabilities. The
official native SDK does not provide a general function-name search engine.
The engine therefore matches available evidence against implementations in its
adapter registry. It does not infer arbitrary proprietary functions from names,
memory addresses or snippets downloaded from the internet.

## Resolution flow

1. Detect the installed host and connect through an appropriate adapter.
2. Inspect its official interface contract and perform bounded read-only probes.
3. Resolve each requested operation against implemented candidate adapters.
4. Prefer candidates whose contract matches the observed host; distinguish
   verified support from experimental support and unavailable capabilities.
5. If no candidate works, check the configured trusted update channel.
6. Verify the update signature, integrity, schema and runtime requirements.
7. Stage the update, revalidate safe reads and promote it atomically when feasible.
8. Keep the previous adapter and restore it if activation or validation fails.
9. If no valid candidate exists, return capability_unavailable with a diagnostic.

Finding another implementation is allowed only when that implementation is known,
permitted and semantically mapped. Downloading an adapter does not prove its
behavior in a new build. No musical write is executed as an automatic probe.

## Unknown hosts and native ABI

A new FL build must not be rejected solely because its full ProductVersion differs.
It must also not be passed into an incompatible SDK ABI just to test compatibility.
The resolver checks the adapter's declared ABI requirements before loading it.
Where ABI compatibility cannot be established, discovery can report the installed
host and an unavailable native connection without patching or injecting into FL.
Any adapter capable of reporting diagnostics in that environment may be selected.

## Update distribution and policy

Use a dedicated release channel in the FL Commons GitHub repository. Ship only
original artifacts whose distribution rights are established. Do not publish the
current SDK-derived DLL as an entirely MIT artifact or assume redistribution rights.
Native components requiring the external SDK need a documented local build path
until their binary distribution terms are established.

The manifest has a monotonically increasing revision, expiry, artifact hashes,
adapter identities, interface requirements, operation mappings and a signature.
A public verification key is pinned in the client; a key supplied by a downloaded
manifest cannot replace that trust root. Publisher private keys stay outside the
repository. Key rotation requires a separately verified transition.

The initial policy offers manual and automatic updates. The automatic policy
checks at connection time with bounded caching and requests carrying no tokens,
project data or private machine paths. Unavailability of the release channel must
not disable previously verified capabilities. Network checks cannot block the
FL audio thread or GUI callback.

Unknown code, unsigned updates, downgrades and mismatched hashes are rejected.
An explicit local rollback uses an already verified retained artifact. DLL updates
are staged while FL is running and activated after normal closure/reload; the
updater does not close FL, discard projects or overwrite a loaded DLL.

## Implementation surfaces

- Native process/version detection, LocalApi metadata and capability availability.
- Native installer and preservation of existing installed versions.
- SDK connection and NativeBackend resolution, replacing scattered exact-build checks.
- Adapter registry and signed update/cache/stage/activation/rollback logic.
- CLI/SDK update policy and diagnostics, public capability schema and documentation.
- Test fixtures for versions, official host contracts, signed updates and failures.

## Acceptance checks

- FL 25/26+ selection is tested with controlled host fixtures; actual FL versions
  are recorded separately rather than manufactured into a compatibility matrix.
- Changing ProductVersion alone does not reject a compatible contract.
- Incompatible or unknown ABI never enables unsupported host calls.
- Per-operation degradation preserves capabilities that remain accessible.
- An alternative implemented adapter can serve the same stable operation.
- Missing network, corrupt downloads and invalid signatures retain working state.
- Expired/replayed manifests and unsigned key replacement are rejected.
- Interrupted activation and failed validation restore the verified prior adapter.
- Loaded DLLs and user projects remain intact; probes perform no musical writes.

## Status

Design only. No adaptive engine or remote updater is implemented by this document.
The current published runtime still has its original exact-build restrictions.
The PDF's pages 8–10 and 13 define this as detection, selection, validation,
trusted updates and controlled degradation; they do not promise autonomous
reconstruction of arbitrary undocumented functions.
