# FL Commons

FL Commons is an independent community API for integrations with FL Studio. It exposes documented, verified capabilities through a stable public contract. Developers define their own integrations.

**English** · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Português (Brasil)](README.pt-BR.md) · [فارسی](README.fa.md) · [العربية](README.ar.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [Ελληνικά](README.el.md)

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)

## Current capabilities

Experimental v0.1.0: authenticated local HTTP, Python SDK, playback state, Play/Pause and Stop through an official SDK plugin. The optional Core exposes an evidence catalog of 87 SDK selectors; catalog entries do not automatically enable commands. MIDI is optional; the direct API requires no separate Python server.

```text
transport.state
transport.play_pause
transport.stop
```

## Quick start

**Compatibility target: FL Studio 25/26 and later, on Windows x64.** This repository currently distributes source. Building it requires Python 3.10+, MSVC 2022 Build Tools, Windows SDK and the externally supplied **fpsdk_20210311b**. These are developer build requirements. Extract the SDK outside the repository and replace the example paths.

Install the Python package from this repository, then build the native component:

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

Save your work and close FL normally before setup. The installer preserves existing versions instead of overwriting them. After launch, add **FL Commons API** to a free Mixer slot. The launcher stores the authentication token using Windows DPAPI. One native instance uses port 3211.

```powershell
.\.venv\Scripts\python native/setup.py --dll 'C:/path/to/flcommons-build/FL Commons API.dll' --launch
```

## Python SDK

```python
from flcommons import FLStudio

fl = FLStudio.connect()
print(fl.status())
print(fl.capabilities())
print(fl.transport.state())
```

Start with read-only queries. Run the following playback commands only when you intend to change playback. Play/Pause is a toggle, not an idempotent start. After a write timeout or `outcome_unknown`, inspect the state before deciding what to do; never automatically retry.

```python
fl.transport.play_pause()
fl.transport.stop()
```

## Optional Core server

The direct SDK connects to the plugin on `127.0.0.1:3211`. If you also need the SDK catalog and the Core OpenAPI contract, start the optional server on port 3210. Its client token is separate from the native DPAPI session token. `--demo` is explicit simulation; the default server starts disconnected.

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## Validation and limits

**Verified:** 77 Python tests and 27 native tests passed locally. Python CI passed on Windows and Linux with Python 3.10, 3.12 and 3.14. Play → Pause → Play → Stop was confirmed by FL callbacks in an authorized test session on build 26.1.7.5653. Linux CI does not validate the FL plugin.

Mixer/channel/project editing and public event streams are not implemented. Adaptive resolution selects implemented interface profiles, and trusted updates support verification, staging and rollback. Other host contracts need verified profiles; no unrestricted function discovery or compatibility with every build is claimed. The new DLL has passed controlled tests but has not yet been reloaded into FL. See the compatibility guide for current evidence and native rebuild/reload requirements.

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/fl-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## Documentation

The links below provide deeper reference material, currently mostly in Portuguese. English is the primary README; corrections to translations are welcome.

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [Adaptive compatibility and trusted updates](docs/adaptive-compatibility.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## Contributing and license

Contribute documented interfaces, reproducible evidence and tests. Keep original code, SDK material and research separate. A detected symbol or simulated result is not proof of working FL control.

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

Original FL Commons source is licensed under **MIT**. Image-Line SDK files and compiled DLLs are not distributed here; SDK terms apply separately. FL Commons is not affiliated with, endorsed by or maintained by Image-Line. FL Studio is an Image-Line trademark.

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
