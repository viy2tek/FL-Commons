# FL Commons

FL Commons, FL Studio entegrasyonları için bağımsız bir topluluk API’sidir. Belgelenmiş ve doğrulanmış yetenekleri kararlı bir genel sözleşmeyle sunar. Geliştiriciler kendi entegrasyonlarını tanımlar.

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · **Türkçe** · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Português (Brasil)](README.pt-BR.md) · [فارسی](README.fa.md) · [العربية](README.ar.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [Ελληνικά](README.el.md)

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)

## Mevcut yetenekler

Deneysel v0.1.0: kimlik doğrulamalı yerel HTTP, Python SDK, resmi SDK eklentisi üzerinden çalma durumu, Play/Pause ve Stop. İsteğe bağlı Core, 87 SDK seçicisinin kanıt kataloğunu sunar; katalog girdileri komutları otomatik etkinleştirmez. MIDI isteğe bağlıdır; doğrudan API ayrı Python sunucusu gerektirmez.

```text
transport.state
transport.play_pause
transport.stop
```

## Hızlı başlangıç

**Uyumluluk hedefi: Windows x64 üzerinde FL Studio 25/26 ve sonrası.** Depo şu an kaynak kod dağıtır. Derleme Python 3.10+, MSVC 2022 Build Tools, Windows SDK ve harici **fpsdk_20210311b** gerektirir. Bunlar geliştirici derleme gereksinimleridir. SDK’yı depo dışına çıkarın ve örnek yolları değiştirin. Yayımlanan yerel bileşen hâlâ yalnızca test edilen derlemeyi kabul eder; adaptif seçim ve kullanıma hazır dağıtım uygulanmadı.

Python paketini bu depodan kurun, ardından yerel bileşeni derleyin:

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

Kurulumdan önce çalışmanızı kaydedip FL’yi normal şekilde kapatın. Kurucu mevcut sürümleri üzerine yazmadan korur. Açılıştan sonra boş bir Mixer yuvasına **FL Commons API** ekleyin. Başlatıcı, belirteci Windows DPAPI ile saklar. Bir yerel örnek 3211 numaralı bağlantı noktasını kullanır.

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

Salt okunur sorgularla başlayın. Aşağıdaki komutları yalnızca çalmayı değiştirmek istediğinizde çalıştırın. Play/Pause durum değiştirir; idempotent başlatma değildir. Yazma zaman aşımı veya outcome_unknown sonrasında karar vermeden önce durumu kontrol edin; otomatik yeniden denemeyin.

```python
fl.transport.play_pause()
fl.transport.stop()
```

## İsteğe bağlı Core sunucusu

Doğrudan SDK, 127.0.0.1:3211 üzerindeki eklentiye bağlanır. Katalog ve Core OpenAPI sözleşmesi için isteğe bağlı sunucuyu 3210 üzerinde başlatın. İstemci belirteci, yerel DPAPI belirtecinden ayrıdır. --demo açık simülasyondur; varsayılan sunucu bağlantısız başlar.

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## Doğrulama ve sınırlar

**Doğrulandı:** yerelde 52 Python ve 21 yerel bileşen testi geçti. Python CI, Windows ve Linux üzerinde Python 3.10, 3.12 ve 3.14 ile geçti. Yetkili test oturumunda FL 26.1.7.5653 geri çağrıları Play → Pause → Play → Stop dizisini doğruladı. Linux CI, FL eklentisini doğrulamaz.

**Uygulanmadı:** Mixer/kanal/proje düzenleme, genel olay akışları, sınırsız keşif ve otomatik adaptör güncelleme. Ses etkisi ve diğer derlemeler test edilmedi. Son kuyruk kilidi düzeltmesi kontrollü yavaş istemci testini geçti ancak FL’ye yeniden yüklenmedi; derlenen ve canlı test edilen hash’ler ayrıdır. Tüm SDK için sertifikasyon değildir.

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/fl-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## Belgeler

Aşağıdaki ayrıntılı belgeler çoğunlukla Portekizcedir. Ana README dili İngilizcedir; çeviri düzeltmeleri memnuniyetle karşılanır.

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [Adaptive compatibility design — not implemented](docs/adaptive-compatibility-design.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## Katkı ve lisans

Belgelenmiş arayüzler, tekrarlanabilir kanıtlar ve testlerle katkıda bulunun. Özgün kodu, SDK materyalini ve araştırmayı ayırın. Bulunan bir sembol veya simülasyon sonucu FL kontrolünü kanıtlamaz.

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

Özgün FL Commons kodu **MIT** lisanslıdır. Image-Line SDK dosyaları ve derlenmiş DLL’ler burada dağıtılmaz; SDK koşulları ayrı uygulanır. FL Commons, Image-Line’a bağlı değildir; onun tarafından onaylanmaz veya sürdürülmez. FL Studio, Image-Line markasıdır.

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
