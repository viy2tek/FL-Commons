# FL Commons

FL Commons 是供 FL Studio 整合使用的獨立社群 API。它透過穩定的公開合約提供有文件支持且經過驗證的能力。開發者自行定義自己的整合。

[English](README.md) · [简体中文](README.zh-CN.md) · **繁體中文** · [日本語](README.ja.md) · [한국어](README.ko.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Português (Brasil)](README.pt-BR.md) · [فارسی](README.fa.md) · [العربية](README.ar.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [Ελληνικά](README.el.md)

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)

## 目前能力

實驗性 v0.1.0：具驗證機制的本機 HTTP、Python SDK，以及透過官方 SDK 外掛取得播放狀態、執行 Play/Pause 與 Stop。選用 Core 提供 87 個 SDK 選擇器的證據目錄；目錄項目不會自動啟用指令。MIDI 為選用功能，直接 API 不需要獨立 Python 伺服器。

```text
transport.state
transport.play_pause
transport.stop
```

## 快速開始

**相容性目標：Windows x64 上的 FL Studio 25/26 及後續版本。** 此儲存庫目前散布原始碼。編譯需要 Python 3.10+、MSVC 2022 Build Tools、Windows SDK 與外部提供的 **fpsdk_20210311b**。這些是開發者的編譯需求。請將 SDK 解壓縮到儲存庫之外並替換範例路徑。

從此儲存庫安裝 Python 套件，再編譯原生元件：

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

安裝前請儲存工作並正常關閉 FL。安裝程式會保留現有版本，不會覆寫。啟動後，將 **FL Commons API** 加入空的 Mixer 插槽。啟動器使用 Windows DPAPI 儲存驗證權杖。一個原生執行個體使用連接埠 3211。

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

先執行唯讀查詢。只有要改變播放時才執行下列指令。Play/Pause 會切換狀態，並非冪等的開始操作。寫入逾時或出現 outcome_unknown 後，先確認狀態再決定；不要自動重試。

```python
fl.transport.play_pause()
fl.transport.stop()
```

## 選用 Core 伺服器

直接 SDK 連線至 127.0.0.1:3211 的外掛。如需目錄與 Core 的 OpenAPI 合約，可在連接埠 3210 啟動選用伺服器。其用戶端權杖與原生 DPAPI 權杖分開。--demo 是明確的模擬模式；預設伺服器啟動時未連線。

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## 驗證與限制

**已驗證：**本機通過 77 項 Python 測試與 27 項原生測試。Python CI 在 Windows、Linux 及 Python 3.10、3.12、3.14 上通過。於獲准的測試工作階段中，FL 26.1.7.5653 的回呼確認了 Play → Pause → Play → Stop。Linux CI 不驗證 FL 外掛。

尚未實作 Mixer、通道、專案編輯與公開事件。自適應選擇使用已實作介面的設定檔；經驗證的更新支援暫存與回復。其他介面合約需要經驗證的設定檔，不保證無限制探索或相容所有組建版本。新 DLL 通過受控測試，但尚未重新載入 FL。請參閱相容性指南。

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/fl-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## 文件

下列連結提供進一步文件，目前主要以葡萄牙語撰寫。英文是主 README 的語言，歡迎修正翻譯。

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [Adaptive compatibility and trusted updates](docs/adaptive-compatibility.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## 貢獻與授權

歡迎貢獻有文件的介面、可重現的證據與測試。請區分原創程式碼、SDK 材料與研究。找到符號或取得模擬結果並不能證明可控制 FL。

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

FL Commons 原創程式碼採 **MIT** 授權。此處不散布 Image-Line SDK 檔案或編譯 DLL；SDK 條款另行適用。FL Commons 不隸屬 Image-Line，也不由其認可或維護。FL Studio 是 Image-Line 的商標。

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
