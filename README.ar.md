# FL Commons

FL Commons هو API مجتمعي مستقل للتكامل مع FL Studio. يوفر إمكانات موثقة ومتحققًا منها من خلال عقد عام مستقر. يحدد المطورون تكاملاتهم الخاصة.

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Português (Brasil)](README.pt-BR.md) · [فارسی](README.fa.md) · **العربية** · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [Ελληνικά](README.el.md)

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)

## الإمكانات الحالية

الإصدار التجريبي v0.1.0: اتصال HTTP محلي مع مصادقة، وPython SDK، وحالة التشغيل وPlay/Pause وStop عبر إضافة تستخدم SDK الرسمي. يوفر Core الاختياري فهرس أدلة لـ87 محددًا في SDK؛ إدراج عنصر لا يفعّل الأوامر تلقائيًا. MIDI اختياري، ولا تحتاج API المباشرة إلى خادم Python منفصل.

```text
transport.state
transport.play_pause
transport.stop
```

## البدء السريع

**هدف التوافق: FL Studio 25/26 وما بعدها على Windows x64.** يوزع المستودع حاليًا الكود المصدري. يتطلب البناء Python 3.10+ وMSVC 2022 Build Tools وWindows SDK و**fpsdk_20210311b** الخارجي. هذه متطلبات بناء للمطورين. فك ضغط SDK خارج المستودع واستبدل المسارات. المكوّن الأصلي المنشور ما زال يقبل إصدار البناء المختبر فقط؛ الاختيار التكيفي والتوزيع الجاهز للاستخدام لم يُنفذا بعد.

ثبّت حزمة Python من هذا المستودع ثم ابنِ المكوّن الأصلي:

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

احفظ عملك وأغلق FL بالطريقة المعتادة قبل الإعداد. يحتفظ المثبّت بالإصدارات الموجودة ولا يستبدلها. بعد التشغيل أضف **FL Commons API** إلى خانة فارغة في Mixer. يحفظ المشغّل رمز المصادقة باستخدام Windows DPAPI. تستخدم نسخة أصلية واحدة المنفذ 3211.

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

ابدأ باستعلامات القراءة فقط. نفّذ الأوامر التالية فقط عندما تريد تغيير التشغيل. يبدّل Play/Pause الحالة وليس أمر بدء يعطي النتيجة نفسها عند تكراره. بعد انتهاء مهلة الكتابة أو outcome_unknown، افحص الحالة قبل اتخاذ قرار؛ لا تُعِد المحاولة تلقائيًا.

```python
fl.transport.play_pause()
fl.transport.stop()
```

## خادم Core اختياري

يتصل SDK المباشر بالإضافة على 127.0.0.1:3211. للوصول أيضًا إلى الفهرس وعقد OpenAPI الخاص بـCore، شغّل الخادم الاختياري على المنفذ 3210. رمز العميل منفصل عن رمز DPAPI الأصلي. --demo محاكاة صريحة؛ يبدأ الخادم الافتراضي دون اتصال.

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## التحقق والحدود

**تم التحقق:** نجح محليًا 52 اختبار Python و21 اختبارًا أصليًا. نجح Python CI على Windows وLinux مع Python 3.10 و3.12 و3.14. أكدت استدعاءات FL 26.1.7.5653 تسلسل Play → Pause → Play → Stop في جلسة اختبار مصرح بها. لا يتحقق CI على Linux من إضافة FL.

**غير منفذ:** تعديل Mixer والقنوات والمشاريع، وتدفقات الأحداث العامة، والاكتشاف غير المقيد، وتحديث المحولات تلقائيًا. لم تُختبر آثار الصوت أو إصدارات البناء الأخرى. نجح أحدث إصلاح لقفل الطابور في اختبار مضبوط لعميل بطيء، لكنه لم يُحمّل مجددًا في FL؛ تُسجل بصمتا النسخة المبنية والمختبرة فعليًا بصورة منفصلة. هذا ليس اعتمادًا لكامل SDK.

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/fl-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## التوثيق

تقدم الروابط التالية توثيقًا أعمق، وهو حاليًا بالبرتغالية في معظمه. الإنجليزية هي لغة README الرئيسي؛ نرحب بتصحيح الترجمات.

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [Adaptive compatibility design — not implemented](docs/adaptive-compatibility-design.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## المساهمة والترخيص

ساهم بواجهات موثقة وأدلة قابلة لإعادة الإنتاج واختبارات. افصل الكود الأصلي ومواد SDK والبحث. العثور على رمز أو نتيجة محاكاة لا يثبت التحكم في FL.

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

الكود الأصلي لـFL Commons مرخص بموجب **MIT**. لا توزع هنا ملفات SDK الخاصة بـImage-Line أو DLL مبنية؛ تنطبق شروط SDK بشكل مستقل. FL Commons غير تابع لـImage-Line ولا معتمد أو مُدار منها. FL Studio علامة تجارية لـImage-Line.

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
