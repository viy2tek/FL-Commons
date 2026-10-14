<div align="center">

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · **한국어** · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Português (Brasil)](README.pt-BR.md) · [فارسی](README.fa.md) · [العربية](README.ar.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [Ελληνικά](README.el.md)

# FL Commons

### FL Studio를 위한 독립적인 커뮤니티 API.

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[GitHub](https://github.com/viy2tek/FL-Commons) · [API](docs/public-api.md) · [OpenAPI](docs/openapi.json) · [Issues](https://github.com/viy2tek/FL-Commons/issues)

</div>

FL Commons는 FL Studio 통합을 위한 독립적인 커뮤니티 API입니다. 안정적인 공개 계약을 통해 문서화되고 검증된 기능을 제공합니다. 개발자가 자신의 통합을 정의합니다.

## 현재 기능

실험적 v0.1.0: 인증된 로컬 HTTP, Python SDK, 공식 SDK 플러그인을 통한 재생 상태, Play/Pause 및 Stop. 선택적 Core는 SDK 선택자 87개의 근거 카탈로그를 제공합니다. 카탈로그 항목이 명령을 자동으로 활성화하지는 않습니다. MIDI는 선택 사항이며 직접 API에는 별도의 Python 서버가 필요 없습니다.

```text
transport.state
transport.play_pause
transport.stop
```

## 빠른 시작

**호환성 목표: Windows x64의 FL Studio 25/26 이상.** 현재 저장소는 소스 코드를 배포합니다. 빌드에는 Python 3.10+, MSVC 2022 Build Tools, Windows SDK 및 외부 제공 **fpsdk_20210311b**가 필요합니다. 이는 개발자 빌드 요구 사항입니다. SDK를 저장소 밖에 압축 해제하고 예제 경로를 바꾸세요. 배포된 네이티브 구성 요소는 아직 테스트된 빌드만 허용합니다. 적응형 선택과 바로 사용할 수 있는 배포 패키지는 미구현입니다.

이 저장소에서 Python 패키지를 설치한 다음 네이티브 구성 요소를 빌드하세요:

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

설치 전에 작업을 저장하고 FL을 정상적으로 종료하세요. 설치 프로그램은 기존 버전을 덮어쓰지 않고 보존합니다. 실행 후 빈 Mixer 슬롯에 **FL Commons API**를 추가하세요. 실행기는 Windows DPAPI로 인증 토큰을 저장합니다. 네이티브 인스턴스 하나가 포트 3211을 사용합니다.

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

읽기 전용 조회부터 시작하세요. 다음 명령은 재생을 변경하려는 경우에만 실행하세요. Play/Pause는 전환 작업이며 멱등적인 시작이 아닙니다. 쓰기 시간 초과 또는 outcome_unknown 이후에는 상태를 확인하고 결정하세요. 자동 재시도하지 마세요.

```python
fl.transport.play_pause()
fl.transport.stop()
```

## 선택적 Core 서버

직접 SDK는 127.0.0.1:3211의 플러그인에 연결됩니다. 카탈로그와 Core OpenAPI 계약도 필요하면 포트 3210에서 선택적 서버를 실행하세요. 클라이언트 토큰은 네이티브 DPAPI 토큰과 별개입니다. --demo는 명시적 시뮬레이션이며 기본 서버는 연결 없이 시작합니다.

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## 검증과 한계

**검증됨:** 로컬 Python 테스트 52개와 네이티브 테스트 21개가 통과했습니다. Python CI는 Windows, Linux 및 Python 3.10, 3.12, 3.14에서 통과했습니다. 승인된 테스트 세션에서 FL 26.1.7.5653 콜백으로 Play → Pause → Play → Stop을 확인했습니다. Linux CI는 FL 플러그인을 검증하지 않습니다.

**미구현:** Mixer/채널/프로젝트 편집, 공개 이벤트 스트림, 무제한 탐색 및 자동 어댑터 업데이트. 오디오 영향과 다른 빌드는 테스트하지 않았습니다. 최신 큐 잠금 수정은 느린 클라이언트 제어 테스트를 통과했지만 FL에 다시 로드하지 않았습니다. 빌드 및 실제 검증 해시는 별도로 기록됩니다. SDK 전체에 대한 인증이 아닙니다.

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/fl-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## 문서

아래 링크의 상세 문서는 현재 대부분 포르투갈어입니다. README의 기본 언어는 영어이며 번역 수정을 환영합니다.

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## 기여와 라이선스

문서화된 인터페이스, 재현 가능한 근거와 테스트로 기여하세요. 자체 코드, SDK 자료와 연구를 분리하세요. 심볼 발견이나 시뮬레이션 결과만으로 FL 제어가 입증되지는 않습니다.

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

FL Commons의 자체 소스 코드는 **MIT** 라이선스입니다. Image-Line SDK 파일과 빌드된 DLL은 여기서 배포하지 않으며 SDK 조건은 별도로 적용됩니다. FL Commons는 Image-Line과 제휴하지 않고 승인이나 유지보수도 받지 않습니다. FL Studio는 Image-Line의 상표입니다.

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
