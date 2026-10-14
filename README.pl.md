# FL Commons

FL Commons to niezależne API społecznościowe do integracji z FL Studio. Udostępnia udokumentowane i zweryfikowane możliwości przez stabilny publiczny kontrakt. Programiści definiują własne integracje.

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Українська](README.uk.md) · **Polski** · [Português (Brasil)](README.pt-BR.md) · [فارسی](README.fa.md) · [العربية](README.ar.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [Ελληνικά](README.el.md)

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)

## Obecne możliwości

Eksperymentalna v0.1.0: lokalny HTTP z uwierzytelnianiem, Python SDK, stan odtwarzania, Play/Pause i Stop przez wtyczkę oficjalnego SDK. Opcjonalny Core udostępnia katalog dowodów dla 87 selektorów SDK; wpisy nie aktywują poleceń automatycznie. MIDI jest opcjonalne; bezpośrednie API nie wymaga osobnego serwera Python.

```text
transport.state
transport.play_pause
transport.stop
```

## Szybki start

**Cel zgodności: FL Studio 25/26 i nowsze na Windows x64.** Repozytorium obecnie udostępnia kod źródłowy. Budowanie wymaga Python 3.10+, MSVC 2022 Build Tools, Windows SDK i zewnętrznego **fpsdk_20210311b**. To wymagania kompilacji dla programistów. Rozpakuj SDK poza repozytorium i zastąp ścieżki.

Zainstaluj pakiet Python z tego repozytorium, a następnie zbuduj komponent natywny:

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

Zapisz pracę i normalnie zamknij FL przed instalacją. Instalator zachowuje istniejące wersje, zamiast je nadpisywać. Po uruchomieniu dodaj **FL Commons API** do wolnego slotu Mixer. Launcher zapisuje token przez Windows DPAPI. Jedna instancja natywna używa portu 3211.

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

Zacznij od zapytań tylko do odczytu. Poniższe polecenia wykonuj wyłącznie w celu zmiany odtwarzania. Play/Pause przełącza stan, nie jest idempotentnym startem. Po przekroczeniu czasu zapisu lub outcome_unknown sprawdź stan przed decyzją; nie ponawiaj automatycznie.

```python
fl.transport.play_pause()
fl.transport.stop()
```

## Opcjonalny serwer Core

Bezpośredni SDK łączy się z wtyczką na 127.0.0.1:3211. Aby korzystać także z katalogu i kontraktu OpenAPI Core, uruchom opcjonalny serwer na porcie 3210. Jego token klienta jest osobny względem natywnego tokena DPAPI. --demo jawnie symuluje; domyślny serwer startuje bez połączenia.

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## Weryfikacja i ograniczenia

**Zweryfikowano:** lokalnie przeszły 77 testy Python i 27 testów natywnych. Python CI przeszedł na Windows i Linux z Python 3.10, 3.12 i 3.14. Callbacki FL 26.1.7.5653 potwierdziły Play → Pause → Play → Stop w autoryzowanej sesji testowej. Linux CI nie weryfikuje wtyczki FL.

Edycja Mixer/kanałów/projektów i publiczne zdarzenia nie są zaimplementowane. Adaptacyjny wybór używa profili zaimplementowanych interfejsów; zweryfikowane aktualizacje obsługują staging i rollback. Inne kontrakty wymagają sprawdzonych profili; nie deklarujemy nieograniczonego wykrywania ani zgodności ze wszystkimi buildami. Nowa DLL przeszła kontrolowane testy, ale nie została ponownie załadowana w FL. Zobacz przewodnik zgodności.

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/fl-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## Dokumentacja

Dokumentacja pod poniższymi linkami jest obecnie głównie po portugalsku. Główny README jest po angielsku; poprawki tłumaczeń są mile widziane.

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [Adaptive compatibility and trusted updates](docs/adaptive-compatibility.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## Współpraca i licencja

Dodawaj udokumentowane interfejsy, odtwarzalne dowody i testy. Oddzielaj oryginalny kod, materiały SDK i badania. Wykryty symbol lub wynik symulacji nie dowodzi sterowania FL.

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

Oryginalny kod FL Commons ma licencję **MIT**. Pliki SDK Image-Line i zbudowane DLL nie są tu dystrybuowane; warunki SDK obowiązują oddzielnie. FL Commons nie jest powiązany z Image-Line, zatwierdzony ani utrzymywany przez tę firmę. FL Studio jest znakiem towarowym Image-Line.

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
