<div align="center">

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · **Deutsch** · [Español](README.es.md) · [Français](README.fr.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Português (Brasil)](README.pt-BR.md) · [فارسی](README.fa.md) · [العربية](README.ar.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [Ελληνικά](README.el.md)

# FL Commons

### Eine unabhängige Community-API für FL Studio.

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[GitHub](https://github.com/viy2tek/FL-Commons) · [API](docs/public-api.md) · [OpenAPI](docs/openapi.json) · [Issues](https://github.com/viy2tek/FL-Commons/issues)

</div>

FL Commons ist eine unabhängige Community-API für Integrationen mit FL Studio. Sie stellt dokumentierte und verifizierte Funktionen über einen stabilen öffentlichen Vertrag bereit. Entwickler definieren ihre eigenen Integrationen.

## Aktuelle Funktionen

Experimentelle v0.1.0: authentifiziertes lokales HTTP, Python-SDK, Wiedergabestatus, Play/Pause und Stop über ein Plugin des offiziellen SDK. Der optionale Core bietet einen Evidenzkatalog mit 87 SDK-Selektoren; Katalogeinträge aktivieren keine Befehle automatisch. MIDI ist optional; die direkte API benötigt keinen separaten Python-Server.

```text
transport.state
transport.play_pause
transport.stop
```

## Schnellstart

**Kompatibilitätsziel: FL Studio 25/26 und neuer auf Windows x64.** Dieses Repository verteilt derzeit Quellcode. Der Build benötigt Python 3.10+, MSVC 2022 Build Tools, Windows SDK und das externe **fpsdk_20210311b**. Dies sind Build-Voraussetzungen für Entwickler. Entpacke das SDK außerhalb des Repositorys und ersetze die Beispielpfade. Die veröffentlichte native Komponente akzeptiert noch nur den getesteten Build; adaptive Auswahl und sofort nutzbare Distribution sind nicht implementiert.

Installiere das Python-Paket aus diesem Repository und kompiliere die native Komponente:

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

Speichere deine Arbeit und schließe FL vor der Einrichtung regulär. Der Installer bewahrt vorhandene Versionen, statt sie zu überschreiben. Füge nach dem Start **FL Commons API** in einen freien Mixer-Slot ein. Der Launcher speichert das Token mit Windows DPAPI. Eine native Instanz verwendet Port 3211.

```powershell
.\.venv\Scripts\python native/setup.py --dll 'C:/path/to/flcommons-build/FL Commons API.dll' --launch
```

## Python-SDK

```python
from flcommons import FLStudio

fl = FLStudio.connect()
print(fl.status())
print(fl.capabilities())
print(fl.transport.state())
```

Beginne mit Leseabfragen. Führe die folgenden Befehle nur aus, wenn du die Wiedergabe ändern willst. Play/Pause schaltet um und ist kein idempotenter Start. Prüfe nach einem Schreib-Timeout oder `outcome_unknown` den Zustand, bevor du entscheidest; wiederhole niemals automatisch.

```python
fl.transport.play_pause()
fl.transport.stop()
```

## Optionaler Core-Server

Das direkte SDK verbindet sich mit dem Plugin auf `127.0.0.1:3211`. Für den SDK-Katalog und den OpenAPI-Vertrag des Core starte den optionalen Server auf Port 3210. Sein Client-Token ist vom nativen DPAPI-Token getrennt. `--demo` simuliert ausdrücklich; der Standardserver startet ohne Verbindung.

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## Validierung und Grenzen

**Verifiziert:** 52 Python-Tests und 21 native Tests bestanden lokal. Python-CI bestand auf Windows und Linux mit Python 3.10, 3.12 und 3.14. Play → Pause → Play → Stop wurde durch FL-Callbacks in einer autorisierten Testsitzung auf Build 26.1.7.5653 bestätigt. Linux-CI validiert das FL-Plugin nicht.

**Nicht implementiert:** Mixer-/Kanal-/Projektbearbeitung, öffentliche Ereignisströme, uneingeschränkte Erkennung und automatische Adapterupdates. Audioauswirkungen und andere Builds wurden nicht getestet. Die neueste Warteschlangen-Sperrkorrektur bestand einen kontrollierten Test mit langsamem Client, wurde aber noch nicht in FL neu geladen; kompilierte und live getestete Hashes werden getrennt geführt. Keine Zertifizierung des gesamten SDK.

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/fl-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## Dokumentation

Die folgenden Links führen zur vertiefenden Dokumentation, derzeit überwiegend auf Portugiesisch. Englisch ist die Hauptsprache des README; Übersetzungskorrekturen sind willkommen.

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## Beiträge und Lizenz

Trage dokumentierte Schnittstellen, reproduzierbare Nachweise und Tests bei. Halte Originalcode, SDK-Material und Forschung getrennt. Ein erkanntes Symbol oder simuliertes Ergebnis beweist keine funktionierende FL-Steuerung.

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

Der Originalcode von FL Commons steht unter **MIT**. Image-Line-SDK-Dateien und kompilierte DLLs werden hier nicht verteilt; SDK-Bedingungen gelten separat. FL Commons ist weder mit Image-Line verbunden noch von Image-Line unterstützt oder gepflegt. FL Studio ist eine Marke von Image-Line.

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
