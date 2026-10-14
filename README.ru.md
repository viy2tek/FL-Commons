<div align="center">

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Türkçe](README.tr.md) · **Русский** · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Português (Brasil)](README.pt-BR.md) · [فارسی](README.fa.md) · [العربية](README.ar.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [Ελληνικά](README.el.md)

# FL Commons

### Независимый API сообщества для FL Studio.

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[GitHub](https://github.com/viy2tek/FL-Commons) · [API](docs/public-api.md) · [OpenAPI](docs/openapi.json) · [Issues](https://github.com/viy2tek/FL-Commons/issues)

</div>

Создавайте собственные инструменты для FL Studio. FL Commons стремится предоставить данные проектов, состояния и операции для FL Studio Time Machine, Universal Project Search, FL Studio Self-Healing, Universal DAW Translator и других приложений. Это будущие цели, а не реализованные возможности.

## Текущие возможности

Экспериментальная v0.1.0: локальный HTTP с аутентификацией, Python SDK, состояние воспроизведения, Play/Pause и Stop через плагин официального SDK. Необязательный Core предоставляет каталог свидетельств для 87 селекторов SDK; записи не включают команды автоматически. MIDI необязателен; прямому API не нужен отдельный Python-сервер.

```text
transport.state
transport.play_pause
transport.stop
```

## Быстрый старт

Нативная интеграция требует Windows x64, FL Studio **26.1.7.5653**, Python 3.10+, MSVC 2022 Build Tools, Windows SDK и отдельно предоставленного **fpsdk_20210311b**. Другие сборки FL отклоняются. Распакуйте SDK вне репозитория и замените пути в примерах.

Установите пакет Python из этого репозитория, затем соберите нативный компонент:

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

Сохраните работу и штатно закройте FL перед установкой. Установщик сохраняет существующие версии, не перезаписывая их. После запуска добавьте **FL Commons API** в свободный слот Mixer. Средство запуска сохраняет токен через Windows DPAPI. Один нативный экземпляр использует порт 3211.

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

Начните с запросов только для чтения. Выполняйте следующие команды лишь для изменения воспроизведения. Play/Pause переключает состояние и не является идемпотентным запуском. После тайм-аута записи или outcome_unknown сначала проверьте состояние; не повторяйте автоматически.

```python
fl.transport.play_pause()
fl.transport.stop()
```

## Необязательный сервер Core

Прямой SDK подключается к плагину на 127.0.0.1:3211. Для каталога и контракта OpenAPI Core запустите необязательный сервер на порту 3210. Его клиентский токен отделён от нативного токена DPAPI. --demo явно включает симуляцию; сервер по умолчанию запускается без подключения.

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## Проверка и ограничения

**Проверено:** локально прошли 52 Python-теста и 21 нативный тест. Python CI прошёл на Windows и Linux с Python 3.10, 3.12 и 3.14. В разрешённой тестовой сессии FL 26.1.7.5653 обратные вызовы подтвердили Play → Pause → Play → Stop. Linux CI не проверяет плагин FL.

**Не реализовано:** редактирование Mixer/каналов/проектов, публичные потоки событий, неограниченное обнаружение и автоматические обновления адаптеров. Влияние на аудио и другие сборки не проверены. Последнее исправление блокировки очереди прошло контролируемый тест с медленным клиентом, но ещё не загружено заново в FL; хеши собранной и проверенной в FL DLL указаны отдельно. Это не сертификация всего SDK.

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/fl-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## Документация

Подробная документация по ссылкам ниже сейчас преимущественно на португальском. Основной README — на английском; исправления переводов приветствуются.

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## Участие и лицензия

Предлагайте документированные интерфейсы, воспроизводимые свидетельства и тесты. Разделяйте оригинальный код, материалы SDK и исследования. Найденный символ или результат симуляции не доказывает управление FL.

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

Оригинальный код FL Commons имеет лицензию **MIT**. Файлы SDK Image-Line и собранные DLL здесь не распространяются; условия SDK действуют отдельно. FL Commons не связан с Image-Line, не одобрен и не поддерживается ею. FL Studio — товарный знак Image-Line.

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
