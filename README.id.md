<div align="center">

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Português (Brasil)](README.pt-BR.md) · [فارسی](README.fa.md) · [العربية](README.ar.md) · **Bahasa Indonesia** · [Italiano](README.it.md) · [Ελληνικά](README.el.md)

# FL Commons

### API komunitas independen untuk FL Studio.

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[GitHub](https://github.com/viy2tek/FL-Commons) · [API](docs/public-api.md) · [OpenAPI](docs/openapi.json) · [Issues](https://github.com/viy2tek/FL-Commons/issues)

</div>

FL Commons adalah API komunitas independen untuk integrasi dengan FL Studio. API menyediakan kemampuan terdokumentasi dan terverifikasi melalui kontrak publik yang stabil. Pengembang menentukan integrasi mereka sendiri.

## Kemampuan saat ini

v0.1.0 eksperimental: HTTP lokal terautentikasi, Python SDK, status pemutaran, Play/Pause dan Stop melalui plugin SDK resmi. Core opsional menyediakan katalog bukti untuk 87 selector SDK; entri katalog tidak otomatis mengaktifkan perintah. MIDI opsional; API langsung tidak memerlukan server Python terpisah.

```text
transport.state
transport.play_pause
transport.stop
```

## Mulai cepat

**Target kompatibilitas: FL Studio 25/26 dan setelahnya pada Windows x64.** Repositori ini masih mendistribusikan kode sumber. Build memerlukan Python 3.10+, MSVC 2022 Build Tools, Windows SDK dan **fpsdk_20210311b** eksternal. Ini persyaratan build untuk pengembang. Ekstrak SDK di luar repositori dan ganti jalur. Komponen native yang diterbitkan masih hanya menerima build yang diuji; pemilihan adaptif dan distribusi siap pakai belum diimplementasikan.

Instal paket Python dari repositori ini, lalu kompilasi komponen native:

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

Simpan pekerjaan dan tutup FL secara normal sebelum pemasangan. Installer mempertahankan versi yang ada tanpa menimpanya. Setelah FL dibuka, tambahkan **FL Commons API** ke slot Mixer kosong. Launcher menyimpan token menggunakan Windows DPAPI. Satu instance native memakai port 3211.

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

Mulai dengan kueri baca saja. Jalankan perintah berikut hanya untuk mengubah pemutaran. Play/Pause beralih status, bukan perintah mulai yang idempoten. Setelah timeout penulisan atau outcome_unknown, periksa status sebelum memutuskan; jangan mencoba ulang otomatis.

```python
fl.transport.play_pause()
fl.transport.stop()
```

## Server Core opsional

SDK langsung terhubung ke plugin di 127.0.0.1:3211. Untuk katalog dan kontrak OpenAPI Core, jalankan server opsional pada port 3210. Token kliennya terpisah dari token DPAPI native. --demo adalah simulasi eksplisit; server standar mulai tanpa koneksi.

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## Validasi dan batasan

**Terverifikasi:** 52 tes Python dan 21 tes native lulus secara lokal. Python CI lulus pada Windows dan Linux dengan Python 3.10, 3.12, dan 3.14. Callback FL 26.1.7.5653 mengonfirmasi Play → Pause → Play → Stop dalam sesi tes yang diizinkan. CI Linux tidak memvalidasi plugin FL.

**Belum tersedia:** penyuntingan Mixer/channel/proyek, aliran peristiwa publik, penemuan tanpa batas, dan pembaruan adapter otomatis. Dampak audio dan build lain belum diuji. Perbaikan kunci antrean terbaru lulus tes terkendali dengan klien lambat, tetapi belum dimuat ulang di FL; hash hasil kompilasi dan hasil uji langsung dicatat terpisah. Ini bukan sertifikasi seluruh SDK.

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/fl-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## Dokumentasi

Tautan berikut memberikan dokumentasi lebih lanjut, saat ini sebagian besar dalam bahasa Portugis. Bahasa utama README adalah Inggris; koreksi terjemahan dipersilakan.

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## Kontribusi dan lisensi

Kontribusikan antarmuka terdokumentasi, bukti yang dapat direproduksi, dan tes. Pisahkan kode asli, materi SDK, dan penelitian. Simbol yang terdeteksi atau hasil simulasi bukan bukti kendali FL.

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

Kode asli FL Commons berlisensi **MIT**. Berkas SDK Image-Line dan DLL hasil kompilasi tidak didistribusikan di sini; ketentuan SDK berlaku terpisah. FL Commons tidak berafiliasi, didukung secara resmi, atau dikelola oleh Image-Line. FL Studio adalah merek dagang Image-Line.

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
