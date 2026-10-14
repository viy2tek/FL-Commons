# FL Commons

FL Commons は FL Studio との連携のための独立したコミュニティ API です。安定した公開契約を通じて、文書化され検証された機能を提供します。開発者は独自の連携を定義できます。

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · **日本語** · [한국어](README.ko.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · [Tiếng Việt](README.vi.md) · [ไทย](README.th.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Português (Brasil)](README.pt-BR.md) · [فارسی](README.fa.md) · [العربية](README.ar.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [Ελληνικά](README.el.md)

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)

## 現在の機能

実験版 v0.1.0：認証付きローカル HTTP、Python SDK、公式 SDK プラグインによる再生状態の取得、Play/Pause、Stop。任意の Core は SDK セレクター 87 件の根拠カタログを提供しますが、掲載だけでコマンドが有効になるわけではありません。MIDI は任意で、直接 API に別の Python サーバーは不要です。

```text
transport.state
transport.play_pause
transport.stop
```

## クイックスタート

**互換性の目標：Windows x64 上の FL Studio 25/26 以降。** 現在このリポジトリはソースコードを配布しています。ビルドには Python 3.10+、MSVC 2022 Build Tools、Windows SDK、外部提供の **fpsdk_20210311b** が必要です。これらは開発者向けのビルド要件です。SDK をリポジトリ外へ展開し、例のパスを置き換えてください。

このリポジトリから Python パッケージをインストールし、ネイティブコンポーネントをビルドします：

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

セットアップ前に作業を保存し、FL を通常の方法で終了してください。インストーラーは既存バージョンを上書きしません。起動後、空いている Mixer スロットに **FL Commons API** を追加します。ランチャーは Windows DPAPI で認証トークンを保存します。ネイティブインスタンス 1 個がポート 3211 を使います。

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

まず読み取り専用の問い合わせから始めてください。以下のコマンドは再生を変更する場合のみ実行します。Play/Pause は状態の切り替えで、冪等な開始操作ではありません。書き込みタイムアウトや outcome_unknown の後は状態を確認してから判断し、自動再試行しないでください。

```python
fl.transport.play_pause()
fl.transport.stop()
```

## 任意の Core サーバー

直接 SDK は 127.0.0.1:3211 のプラグインに接続します。カタログと Core の OpenAPI 契約も必要な場合は、任意のサーバーをポート 3210 で起動します。そのクライアントトークンはネイティブ DPAPI トークンと別です。--demo は明示的なシミュレーションで、標準サーバーは未接続で起動します。

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## 検証と制限

**検証済み：**ローカルで Python テスト 79 件とネイティブテスト 28 件が成功。Python CI は Windows、Linux、Python 3.10・3.12・3.14 で成功しました。許可されたテストセッションで、FL 26.1.7.5653 のコールバックが Play → Pause → Play → Stop を確認しました。Linux CI は FL プラグインを検証しません。

Mixer・チャンネル・プロジェクト編集と公開イベントは未実装です。適応的選択は実装済みインターフェースのプロファイルを使い、検証済み更新はステージングとロールバックに対応します。その他の契約には検証済みプロファイルが必要で、無制限の検出や全ビルドの互換性は保証しません。互換性ガイドを参照してください。

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/adaptive-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## ドキュメント

以下の詳細ドキュメントは現在主にポルトガル語です。README の主言語は英語です。翻訳の修正を歓迎します。

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [Adaptive compatibility and trusted updates](docs/adaptive-compatibility.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## 貢献とライセンス

文書化されたインターフェース、再現可能な根拠、テストを提供してください。独自コード、SDK 資料、研究は分離します。シンボルの検出やシミュレーション結果だけでは FL を制御できる証明になりません。

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

FL Commons の独自コードは **MIT** ライセンスです。Image-Line SDK ファイルとコンパイル済み DLL はここでは配布しません。SDK の条件は別途適用されます。FL Commons は Image-Line と提携しておらず、同社による承認や保守も受けていません。FL Studio は Image-Line の商標です。

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
