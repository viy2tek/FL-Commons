<div align="center">

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Deutsch](README.de.md) · **Español** · [Français](README.fr.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Português (Brasil)](README.pt-BR.md) · [فارسی](README.fa.md) · [العربية](README.ar.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [Ελληνικά](README.el.md)

# FL Commons

### Una API comunitaria independiente para FL Studio.

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[GitHub](https://github.com/viy2tek/FL-Commons) · [API](docs/public-api.md) · [OpenAPI](docs/openapi.json) · [Issues](https://github.com/viy2tek/FL-Commons/issues)

</div>

Crea tus propias herramientas para FL Studio. FL Commons busca proporcionar datos de proyectos, estado y operaciones para FL Studio Time Machine, Universal Project Search, FL Studio Self-Healing, Universal DAW Translator y más. Estas aplicaciones son objetivos futuros, todavía no implementados.

## Capacidades actuales

v0.1.0 experimental: HTTP local autenticado, SDK Python, estado de reproducción, Play/Pause y Stop mediante un plugin del SDK oficial. El Core opcional ofrece un catálogo de evidencias de 87 selectores del SDK; sus entradas no habilitan comandos automáticamente. MIDI es opcional; la API directa no necesita un servidor Python separado.

```text
transport.state
transport.play_pause
transport.stop
```

## Inicio rápido

La integración nativa requiere Windows x64, FL Studio **26.1.7.5653**, Python 3.10+, MSVC 2022 Build Tools, Windows SDK y **fpsdk_20210311b** suministrado externamente. Se rechazan otros builds de FL. Extrae el SDK fuera del repositorio y sustituye las rutas de ejemplo por las tuyas.

Instala el paquete Python desde este repositorio y compila el componente nativo:

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

Guarda tu trabajo y cierra FL normalmente antes de instalar. El instalador conserva las versiones existentes, sin sobrescribirlas. Tras iniciar FL, añade **FL Commons API** a una ranura libre del Mixer. El lanzador guarda el token con Windows DPAPI. Una instancia nativa usa el puerto 3211.

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

Empieza con consultas de lectura. Ejecuta los comandos siguientes solo si quieres cambiar la reproducción. Play/Pause alterna el estado; no es un inicio idempotente. Tras un timeout de escritura o `outcome_unknown`, consulta el estado antes de decidir; no reintentes automáticamente.

```python
fl.transport.play_pause()
fl.transport.stop()
```

## Servidor Core opcional

El SDK directo conecta al plugin en `127.0.0.1:3211`. Para acceder también al catálogo y al contrato OpenAPI del Core, inicia el servidor opcional en el puerto 3210. Su token de cliente es distinto del token DPAPI nativo. `--demo` es simulación explícita; el servidor predeterminado inicia desconectado.

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## Validación y límites

**Verificado:** pasaron 52 pruebas Python y 21 nativas localmente. El CI Python pasó en Windows y Linux con Python 3.10, 3.12 y 3.14. Play → Pause → Play → Stop fue confirmado por callbacks de FL en una sesión de prueba autorizada del build 26.1.7.5653. El CI Linux no valida el plugin de FL.

**Sin implementar:** edición de Mixer/canales/proyectos, eventos públicos, descubrimiento sin restricciones y actualizaciones automáticas de adaptadores. No se probaron el impacto en audio ni otros builds. La última corrección del bloqueo de la cola pasó una prueba controlada con un cliente lento, pero no se recargó en FL; los hashes compilado y probado se registran por separado. No certifica todo el SDK.

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/fl-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## Documentación

Los enlaces siguientes amplían la documentación, actualmente mayormente en portugués. El README principal está en inglés; se agradecen correcciones de traducción.

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## Contribuciones y licencia

Contribuye con interfaces documentadas, evidencias reproducibles y pruebas. Separa código original, material del SDK e investigación. Un símbolo detectado o un resultado simulado no demuestra control de FL.

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

El código original de FL Commons tiene licencia **MIT**. Aquí no se distribuyen archivos del SDK Image-Line ni DLL compiladas; los términos del SDK se aplican por separado. FL Commons no está afiliado, avalado ni mantenido por Image-Line. FL Studio es una marca de Image-Line.

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
