# FL Commons

FL Commons เป็น API ชุมชนอิสระสำหรับการเชื่อมต่อกับ FL Studio โดยเปิดให้ใช้ความสามารถที่มีเอกสารและผ่านการตรวจสอบผ่านสัญญาสาธารณะที่เสถียร นักพัฒนากำหนดการเชื่อมต่อของตนเอง

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · **ไทย** · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Português (Brasil)](README.pt-BR.md) · [فارسی](README.fa.md) · [العربية](README.ar.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [Ελληνικά](README.el.md)

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)

## ความสามารถปัจจุบัน

v0.1.0 ระยะทดลอง: HTTP ภายในเครื่องพร้อมการยืนยันตัวตน, Python SDK, สถานะการเล่น, Play/Pause และ Stop ผ่านปลั๊กอิน SDK ทางการ Core แบบเลือกใช้มีแค็ตตาล็อกหลักฐานของตัวเลือก SDK 87 รายการ รายการในแค็ตตาล็อกไม่ได้เปิดใช้คำสั่งโดยอัตโนมัติ MIDI เป็นตัวเลือก และ API โดยตรงไม่ต้องมีเซิร์ฟเวอร์ Python แยก

```text
transport.state
transport.play_pause
transport.stop
```

## เริ่มต้นใช้งาน

**เป้าหมายความเข้ากันได้: FL Studio 25/26 เป็นต้นไปบน Windows x64** ที่เก็บนี้แจกซอร์สโค้ด การคอมไพล์ต้องใช้ Python 3.10+, MSVC 2022 Build Tools, Windows SDK และ **fpsdk_20210311b** จากภายนอก ซึ่งเป็นข้อกำหนดสำหรับนักพัฒนาที่คอมไพล์เอง ให้แตก SDK นอกที่เก็บและเปลี่ยนพาธ

ติดตั้งแพ็กเกจ Python จากที่เก็บโค้ดนี้ แล้วคอมไพล์ส่วนเนทีฟ:

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

บันทึกงานและปิด FL ตามปกติก่อนติดตั้ง ตัวติดตั้งจะเก็บเวอร์ชันเดิมไว้โดยไม่เขียนทับ หลังเปิด FL ให้เพิ่ม **FL Commons API** ในช่อง Mixer ที่ว่าง ตัวเปิดโปรแกรมเก็บโทเค็นด้วย Windows DPAPI อินสแตนซ์เนทีฟหนึ่งตัวใช้พอร์ต 3211

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

เริ่มด้วยการอ่านข้อมูลเท่านั้น รันคำสั่งต่อไปนี้เฉพาะเมื่อต้องการเปลี่ยนการเล่น Play/Pause เป็นการสลับสถานะ ไม่ใช่คำสั่งเริ่มที่เรียกซ้ำแล้วให้ผลเดิม หลังการเขียนหมดเวลาหรือ outcome_unknown ให้ตรวจสถานะก่อนตัดสินใจ อย่าลองซ้ำอัตโนมัติ

```python
fl.transport.play_pause()
fl.transport.stop()
```

## เซิร์ฟเวอร์ Core แบบเลือกใช้

SDK โดยตรงเชื่อมกับปลั๊กอินที่ 127.0.0.1:3211 หากต้องการแค็ตตาล็อกและสัญญา OpenAPI ของ Core ให้เปิดเซิร์ฟเวอร์แบบเลือกใช้ที่พอร์ต 3210 โทเค็นของไคลเอนต์แยกจากโทเค็น DPAPI เนทีฟ --demo เป็นการจำลองอย่างชัดเจน เซิร์ฟเวอร์เริ่มต้นจะยังไม่เชื่อมต่อ

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## การตรวจสอบและข้อจำกัด

**ตรวจสอบแล้ว:** ผ่านการทดสอบ Python 79 รายการและเนทีฟ 28 รายการในเครื่อง Python CI ผ่านบน Windows และ Linux ด้วย Python 3.10, 3.12 และ 3.14 callback ของ FL 26.1.7.5653 ยืนยัน Play → Pause → Play → Stop ในเซสชันทดสอบที่ได้รับอนุญาต CI บน Linux ไม่ได้ตรวจสอบปลั๊กอิน FL

ยังไม่มีการแก้ไข Mixer/แชนเนล/โปรเจกต์และเหตุการณ์สาธารณะ การเลือกแบบปรับตัวใช้โปรไฟล์อินเทอร์เฟซที่พัฒนาแล้ว การอัปเดตที่ตรวจสอบรองรับ staging และ rollback สัญญาอื่นต้องมีโปรไฟล์ที่ตรวจสอบแล้ว ไม่อ้างว่าค้นพบได้ไม่จำกัดหรือรองรับทุก build ดูคู่มือความเข้ากันได้

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/adaptive-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## เอกสาร

ลิงก์ด้านล่างเป็นเอกสารเพิ่มเติม ซึ่งปัจจุบันส่วนใหญ่เป็นภาษาโปรตุเกส README หลักเป็นภาษาอังกฤษ ยินดีรับการแก้ไขคำแปล

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [Adaptive compatibility and trusted updates](docs/adaptive-compatibility.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## การมีส่วนร่วมและสัญญาอนุญาต

ร่วมพัฒนาด้วยอินเทอร์เฟซที่มีเอกสาร หลักฐานที่ทำซ้ำได้ และการทดสอบ แยกโค้ดต้นฉบับ วัสดุ SDK และงานวิจัยออกจากกัน การพบสัญลักษณ์หรือผลจำลองไม่ใช่หลักฐานว่าควบคุม FL ได้จริง

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

โค้ดต้นฉบับ FL Commons ใช้สัญญาอนุญาต **MIT** ที่นี่ไม่แจกไฟล์ SDK ของ Image-Line หรือ DLL ที่คอมไพล์แล้ว ข้อกำหนด SDK ใช้แยกต่างหาก FL Commons ไม่ได้เป็นพันธมิตร ได้รับการรับรอง หรือดูแลโดย Image-Line ส่วน FL Studio เป็นเครื่องหมายการค้าของ Image-Line

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
