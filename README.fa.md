<div align="center">

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Português (Brasil)](README.pt-BR.md) · **فارسی** · [العربية](README.ar.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [Ελληνικά](README.el.md)

# FL Commons

### یک API مستقل و جامعه‌محور برای FL Studio.

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[GitHub](https://github.com/viy2tek/FL-Commons) · [API](docs/public-api.md) · [OpenAPI](docs/openapi.json) · [Issues](https://github.com/viy2tek/FL-Commons/issues)

</div>

FL Commons یک API مستقل و جامعه‌محور برای یکپارچه‌سازی با FL Studio است. قابلیت‌های مستند و تأییدشده را از طریق یک قرارداد عمومی پایدار ارائه می‌کند. توسعه‌دهندگان یکپارچه‌سازی‌های خود را تعریف می‌کنند.

## قابلیت‌های فعلی

نسخه آزمایشی v0.1.0: HTTP محلی با احراز هویت، Python SDK، وضعیت پخش، Play/Pause و Stop از طریق افزونه SDK رسمی. Core اختیاری فهرست شواهد ۸۷ انتخابگر SDK را ارائه می‌کند؛ ثبت در فهرست فرمان‌ها را خودکار فعال نمی‌کند. MIDI اختیاری است و API مستقیم به سرور Python جداگانه نیاز ندارد.

```text
transport.state
transport.play_pause
transport.stop
```

## شروع سریع

**هدف سازگاری: FL Studio 25/26 و جدیدتر روی Windows x64.** این مخزن فعلاً کد منبع توزیع می‌کند. ساخت به Python 3.10+، MSVC 2022 Build Tools، Windows SDK و **fpsdk_20210311b** خارجی نیاز دارد. این‌ها الزامات ساخت برای توسعه‌دهندگان هستند. SDK را خارج مخزن استخراج و مسیرها را عوض کنید. مؤلفه بومی منتشرشده هنوز فقط بیلد آزموده‌شده را می‌پذیرد؛ انتخاب تطبیقی و توزیع آماده استفاده پیاده‌سازی نشده‌اند.

بسته Python را از این مخزن نصب کنید و سپس مؤلفه بومی را بسازید:

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

پیش از نصب، کار خود را ذخیره و FL را به‌طور معمول ببندید. نصب‌کننده نسخه‌های موجود را حفظ می‌کند و روی آن‌ها نمی‌نویسد. پس از اجرا، **FL Commons API** را در یک جایگاه خالی Mixer اضافه کنید. اجراکننده توکن را با Windows DPAPI ذخیره می‌کند. یک نمونه بومی از پورت 3211 استفاده می‌کند.

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

با درخواست‌های فقط‌خواندنی شروع کنید. فرمان‌های زیر را فقط برای تغییر پخش اجرا کنید. Play/Pause وضعیت را عوض می‌کند و شروعی با خاصیت تکرارپذیری بدون تغییر نتیجه نیست. پس از پایان مهلت نوشتن یا outcome_unknown، ابتدا وضعیت را بررسی کنید؛ خودکار دوباره تلاش نکنید.

```python
fl.transport.play_pause()
fl.transport.stop()
```

## سرور اختیاری Core

SDK مستقیم به افزونه در 127.0.0.1:3211 متصل می‌شود. برای فهرست و قرارداد OpenAPI مربوط به Core، سرور اختیاری را روی پورت 3210 اجرا کنید. توکن کلاینت از توکن DPAPI بومی جداست. --demo شبیه‌سازی صریح است؛ سرور پیش‌فرض بدون اتصال آغاز می‌شود.

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## اعتبارسنجی و محدودیت‌ها

**تأیید شده:** ۵۲ آزمون Python و ۲۱ آزمون بومی به‌صورت محلی موفق شدند. Python CI روی Windows و Linux با Python 3.10، 3.12 و 3.14 موفق شد. در جلسه آزمایشی مجاز، callbackهای FL 26.1.7.5653 توالی Play → Pause → Play → Stop را تأیید کردند. CI لینوکس افزونه FL را اعتبارسنجی نمی‌کند.

**پیاده‌سازی نشده:** ویرایش Mixer، کانال و پروژه، جریان رویداد عمومی، کشف نامحدود و به‌روزرسانی خودکار آداپتور. اثر بر صدا و بیلدهای دیگر آزموده نشده‌اند. آخرین اصلاح قفل صف در آزمون کنترل‌شده کلاینت کند موفق بود، اما هنوز در FL دوباره بارگذاری نشده؛ هش نسخه ساخته‌شده و نسخه آزموده‌شده جدا ثبت شده‌اند. این تأیید کل SDK نیست.

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/fl-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## مستندات

پیوندهای زیر مستندات بیشتر را ارائه می‌کنند که فعلاً بیشتر به پرتغالی هستند. زبان اصلی README انگلیسی است؛ اصلاح ترجمه‌ها پذیرفته می‌شود.

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## مشارکت و مجوز

با رابط‌های مستند، شواهد قابل بازتولید و آزمون‌ها مشارکت کنید. کد اصلی، مواد SDK و پژوهش را جدا نگه دارید. کشف یک نماد یا نتیجه شبیه‌سازی، کنترل FL را ثابت نمی‌کند.

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

کد اصلی FL Commons تحت مجوز **MIT** است. فایل‌های SDK متعلق به Image-Line و DLLهای ساخته‌شده اینجا توزیع نمی‌شوند؛ شرایط SDK جداگانه اعمال می‌شود. FL Commons وابسته، مورد تأیید یا نگهداری‌شده توسط Image-Line نیست. FL Studio علامت تجاری Image-Line است.

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
