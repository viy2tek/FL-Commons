# FL Commons

FL Commons è un’API comunitaria indipendente per integrazioni con FL Studio. Espone funzionalità documentate e verificate tramite un contratto pubblico stabile. Gli sviluppatori definiscono le proprie integrazioni.

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Português (Brasil)](README.pt-BR.md) · [فارسی](README.fa.md) · [العربية](README.ar.md) · [Bahasa Indonesia](README.id.md) · **Italiano** · [Ελληνικά](README.el.md)

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)

## Funzionalità attuali

v0.1.0 sperimentale: HTTP locale autenticato, SDK Python, stato di riproduzione, Play/Pause e Stop tramite un plugin dell’SDK ufficiale. Il Core opzionale offre un catalogo di evidenze per 87 selettori SDK; le voci non abilitano automaticamente i comandi. MIDI è opzionale; l’API diretta non richiede un server Python separato.

```text
transport.state
transport.play_pause
transport.stop
```

## Avvio rapido

**Compatibilità prevista: FL Studio 25/26 e successivi su Windows x64.** Il repository distribuisce codice sorgente. La compilazione richiede Python 3.10+, MSVC 2022 Build Tools, Windows SDK e **fpsdk_20210311b** esterno. Sono requisiti di compilazione per sviluppatori. Estrai l’SDK fuori dal repository e sostituisci i percorsi. Il componente nativo pubblicato accetta ancora solo il build testato; selezione adattiva e distribuzione pronta all’uso non sono implementate.

Installa il pacchetto Python da questo repository e compila il componente nativo:

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

Salva il lavoro e chiudi FL normalmente prima dell’installazione. L’installer conserva le versioni esistenti senza sovrascriverle. Dopo l’avvio, aggiungi **FL Commons API** a uno slot libero del Mixer. Il launcher salva il token con Windows DPAPI. Un’istanza nativa usa la porta 3211.

```powershell
.\.venv\Scripts\python native/setup.py --dll 'C:/path/to/flcommons-build/FL Commons API.dll' --launch
```

## SDK Python

```python
from flcommons import FLStudio

fl = FLStudio.connect()
print(fl.status())
print(fl.capabilities())
print(fl.transport.state())
```

Inizia con richieste di sola lettura. Esegui i comandi seguenti solo per cambiare la riproduzione. Play/Pause alterna lo stato, non è un avvio idempotente. Dopo un timeout di scrittura o `outcome_unknown`, controlla lo stato prima di decidere; non riprovare automaticamente.

```python
fl.transport.play_pause()
fl.transport.stop()
```

## Server Core opzionale

L’SDK diretto si collega al plugin su `127.0.0.1:3211`. Per accedere anche al catalogo e al contratto OpenAPI del Core, avvia il server opzionale sulla porta 3210. Il suo token client è distinto dal token DPAPI nativo. `--demo` è simulazione esplicita; il server predefinito parte disconnesso.

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## Verifiche e limiti

**Verificato:** 52 test Python e 21 nativi superati localmente. Il CI Python è passato su Windows e Linux con Python 3.10, 3.12 e 3.14. Play → Pause → Play → Stop è stato confermato dai callback FL in una sessione di test autorizzata sul build 26.1.7.5653. Il CI Linux non verifica il plugin FL.

**Non implementati:** modifica di Mixer/canali/progetti, eventi pubblici, rilevamento senza limiti e aggiornamenti automatici degli adattatori. Impatto audio e altri build non testati. L’ultima correzione del blocco della coda ha superato un test controllato con client lento, ma non è stata ricaricata in FL; gli hash compilato e testato sono distinti. Non certifica l’intero SDK.

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/fl-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## Documentazione

I collegamenti seguenti approfondiscono la documentazione, attualmente soprattutto in portoghese. L’inglese è la lingua principale del README; le correzioni alle traduzioni sono benvenute.

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [Adaptive compatibility design — not implemented](docs/adaptive-compatibility-design.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## Contributi e licenza

Contribuisci con interfacce documentate, evidenze riproducibili e test. Separa codice originale, materiale SDK e ricerca. Un simbolo rilevato o un risultato simulato non dimostra il controllo di FL.

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

Il codice originale di FL Commons usa la licenza **MIT**. File SDK Image-Line e DLL compilate non sono distribuiti qui; i termini SDK si applicano separatamente. FL Commons non è affiliato, approvato o mantenuto da Image-Line. FL Studio è un marchio di Image-Line.

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
