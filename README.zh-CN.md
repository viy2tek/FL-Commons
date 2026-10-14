<div align="center">

[English](README.md) · **简体中文** · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Português (Brasil)](README.pt-BR.md) · [فارسی](README.fa.md) · [العربية](README.ar.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [Ελληνικά](README.el.md)

# FL Commons

### 面向 FL Studio 的独立社区 API。

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[GitHub](https://github.com/viy2tek/FL-Commons) · [API](docs/public-api.md) · [OpenAPI](docs/openapi.json) · [Issues](https://github.com/viy2tek/FL-Commons/issues)

</div>

为 FL Studio 构建自己的工具。FL Commons 致力于提供项目数据、状态和操作，支持 FL Studio Time Machine、Universal Project Search、FL Studio Self-Healing、Universal DAW Translator 等应用。这些应用属于未来目标，目前尚未实现。

## 当前能力

实验性 v0.1.0：经过身份验证的本地 HTTP、Python SDK，以及通过官方 SDK 插件读取播放状态、执行 Play/Pause 和 Stop。可选 Core 提供包含 87 个 SDK 选择器的证据目录；目录条目不会自动启用命令。MIDI 是可选项，直接 API 不需要独立 Python 服务器。

```text
transport.state
transport.play_pause
transport.stop
```

## 快速开始

原生集成需要 Windows x64、FL Studio **26.1.7.5653**、Python 3.10+、MSVC 2022 Build Tools、Windows SDK 和单独提供的 **fpsdk_20210311b**。其他 FL 构建版本会被拒绝。请将 SDK 解压到仓库之外，并替换示例路径。

从此仓库安装 Python 包，然后编译原生组件：

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

安装前请保存工作并正常关闭 FL。安装程序会保留现有版本，不会覆盖。启动后，将 **FL Commons API** 添加到空闲 Mixer 插槽。启动器使用 Windows DPAPI 保存身份验证令牌。一个原生实例使用端口 3211。

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

先执行只读查询。仅在需要改变播放时运行下面的命令。Play/Pause 切换播放状态，不是幂等的启动操作。写入超时或出现 outcome_unknown 后，应先检查状态再作决定，切勿自动重试。

```python
fl.transport.play_pause()
fl.transport.stop()
```

## 可选 Core 服务器

直接 SDK 连接到位于 127.0.0.1:3211 的插件。如需目录和 Core 的 OpenAPI 合约，可在端口 3210 启动可选服务器。其客户端令牌与原生 DPAPI 令牌分开。--demo 是明确的模拟模式；默认服务器以未连接状态启动。

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## 验证与限制

**已验证：**本地通过 52 项 Python 测试和 21 项原生测试。Python CI 在 Windows、Linux 和 Python 3.10、3.12、3.14 上通过。在获准的测试会话中，FL 26.1.7.5653 的回调确认了 Play → Pause → Play → Stop。Linux CI 不验证 FL 插件。

**尚未实现：**Mixer、通道、项目编辑，公共事件流，无限制发现和自动适配器更新。音频影响及其他构建版本未测试。最新队列锁修复通过了受控慢客户端测试，但尚未重新加载到 FL；编译版本与实际测试版本的哈希分别记录。这不是对整个 SDK 的认证。

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/fl-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## 文档

以下链接提供更深入的文档，目前主要使用葡萄牙语。英语是主 README 的语言，欢迎修正翻译。

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## 贡献与许可

欢迎贡献有文档支持的接口、可复现的证据和测试。请分开保存原创代码、SDK 材料和研究。发现一个符号或获得模拟结果，并不能证明可以控制 FL。

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

FL Commons 原创代码采用 **MIT** 许可。此仓库不分发 Image-Line SDK 文件或编译 DLL；SDK 条款独立适用。FL Commons 与 Image-Line 无隶属关系，也不由其认可或维护。FL Studio 是 Image-Line 的商标。

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
