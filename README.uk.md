# FL Commons

FL Commons — незалежний API спільноти для інтеграцій із FL Studio. Він надає документовані й перевірені можливості через стабільний публічний контракт. Розробники визначають власні інтеграції.

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · **Українська** · [Polski](README.pl.md) · [Português (Brasil)](README.pt-BR.md) · [فارسی](README.fa.md) · [العربية](README.ar.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [Ελληνικά](README.el.md)

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)

## Поточні можливості

Експериментальна v0.1.0: локальний HTTP з автентифікацією, Python SDK, стан відтворення, Play/Pause і Stop через плагін офіційного SDK. Необов’язковий Core надає каталог доказів для 87 селекторів SDK; записи не вмикають команди автоматично. MIDI необов’язковий; прямий API не потребує окремого Python-сервера.

```text
transport.state
transport.play_pause
transport.stop
```

## Швидкий початок

**Цільова сумісність: FL Studio 25/26 і новіші на Windows x64.** Репозиторій наразі поширює вихідний код. Збирання потребує Python 3.10+, MSVC 2022 Build Tools, Windows SDK і зовнішнього **fpsdk_20210311b**. Це вимоги для збирання розробниками. Розпакуйте SDK поза репозиторієм і замініть шляхи. Опублікований нативний компонент поки приймає лише перевірену збірку; адаптивний вибір і готове до використання постачання не реалізовані.

Встановіть пакет Python із цього репозиторію, потім зберіть нативний компонент:

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

Збережіть роботу й нормально закрийте FL перед встановленням. Інсталятор зберігає наявні версії, не перезаписуючи їх. Після запуску додайте **FL Commons API** у вільний слот Mixer. Засіб запуску зберігає токен через Windows DPAPI. Один нативний екземпляр використовує порт 3211.

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

Почніть із запитів лише для читання. Виконуйте наведені команди лише для зміни відтворення. Play/Pause перемикає стан і не є ідемпотентним запуском. Після тайм-ауту запису або outcome_unknown перевірте стан перед рішенням; не повторюйте автоматично.

```python
fl.transport.play_pause()
fl.transport.stop()
```

## Необов’язковий сервер Core

Прямий SDK підключається до плагіна на 127.0.0.1:3211. Для каталогу та контракту OpenAPI Core запустіть необов’язковий сервер на порту 3210. Його клієнтський токен відокремлений від нативного токена DPAPI. --demo явно вмикає симуляцію; типовий сервер запускається без підключення.

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## Перевірка й обмеження

**Перевірено:** локально пройшли 52 Python-тести й 21 нативний тест. Python CI пройшов на Windows і Linux із Python 3.10, 3.12 та 3.14. У дозволеній тестовій сесії FL 26.1.7.5653 зворотні виклики підтвердили Play → Pause → Play → Stop. Linux CI не перевіряє плагін FL.

**Не реалізовано:** редагування Mixer/каналів/проєктів, публічні потоки подій, необмежене виявлення та автоматичне оновлення адаптерів. Вплив на аудіо й інші збірки не перевірені. Останнє виправлення блокування черги пройшло контрольований тест із повільним клієнтом, але ще не перезавантажене у FL; хеші зібраної та перевіреної DLL записано окремо. Це не сертифікація всього SDK.

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/fl-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## Документація

Документація за посиланнями нижче зараз переважно португальською. Основний README — англійською; виправлення перекладів вітаються.

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [Adaptive compatibility design — not implemented](docs/adaptive-compatibility-design.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## Участь і ліцензія

Додавайте документовані інтерфейси, відтворювані докази й тести. Відокремлюйте оригінальний код, матеріали SDK та дослідження. Знайдений символ чи результат симуляції не доводить керування FL.

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

Оригінальний код FL Commons має ліцензію **MIT**. Файли SDK Image-Line і зібрані DLL тут не поширюються; умови SDK діють окремо. FL Commons не пов’язаний з Image-Line, не схвалений і не підтримується нею. FL Studio — торговельна марка Image-Line.

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
