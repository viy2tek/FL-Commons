# FL Commons

FL Commons là API cộng đồng độc lập dành cho tích hợp với FL Studio. API cung cấp khả năng có tài liệu và đã kiểm chứng thông qua hợp đồng công khai ổn định. Nhà phát triển tự xác định các tích hợp của mình.

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Türkçe](README.tr.md) · [Русский](README.ru.md) · **Tiếng Việt** · [ไทย](README.th.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Українська](README.uk.md) · [Polski](README.pl.md) · [Português (Brasil)](README.pt-BR.md) · [فارسی](README.fa.md) · [العربية](README.ar.md) · [Bahasa Indonesia](README.id.md) · [Italiano](README.it.md) · [Ελληνικά](README.el.md)

[![Tests](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml/badge.svg)](https://github.com/viy2tek/FL-Commons/actions/workflows/tests.yml)

## Khả năng hiện tại

v0.1.0 thử nghiệm: HTTP cục bộ có xác thực, Python SDK, trạng thái phát, Play/Pause và Stop qua plugin SDK chính thức. Core tùy chọn cung cấp danh mục bằng chứng cho 87 selector SDK; mục trong danh mục không tự kích hoạt lệnh. MIDI là tùy chọn; API trực tiếp không cần máy chủ Python riêng.

```text
transport.state
transport.play_pause
transport.stop
```

## Bắt đầu nhanh

**Mục tiêu tương thích: FL Studio 25/26 trở lên trên Windows x64.** Kho mã hiện phân phối mã nguồn. Biên dịch cần Python 3.10+, MSVC 2022 Build Tools, Windows SDK và **fpsdk_20210311b** bên ngoài. Đây là yêu cầu biên dịch dành cho nhà phát triển. Giải nén SDK ngoài kho mã và thay đường dẫn.

Cài gói Python từ kho mã này, rồi biên dịch thành phần native:

```powershell
git clone https://github.com/viy2tek/FL-Commons.git
cd FL-Commons
python -m venv .venv
.\.venv\Scripts\python -m pip install .
.\native\build.ps1 -SdkDirectory 'C:/path/to/extracted-sdk' -OutputDirectory 'C:/path/to/flcommons-build'
```

Lưu công việc và đóng FL bình thường trước khi cài đặt. Trình cài giữ các phiên bản hiện có thay vì ghi đè. Sau khi khởi chạy, thêm **FL Commons API** vào một slot Mixer trống. Trình khởi chạy lưu token bằng Windows DPAPI. Một instance native dùng cổng 3211.

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

Bắt đầu bằng truy vấn chỉ đọc. Chỉ chạy các lệnh dưới đây khi muốn thay đổi phát lại. Play/Pause chuyển đổi trạng thái, không phải lệnh bắt đầu có tính lũy đẳng. Sau timeout ghi hoặc outcome_unknown, kiểm tra trạng thái trước khi quyết định; không tự động thử lại.

```python
fl.transport.play_pause()
fl.transport.stop()
```

## Máy chủ Core tùy chọn

SDK trực tiếp kết nối plugin tại 127.0.0.1:3211. Để dùng cả danh mục và hợp đồng OpenAPI của Core, khởi chạy máy chủ tùy chọn trên cổng 3210. Token phía client tách biệt với token DPAPI native. --demo là mô phỏng rõ ràng; máy chủ mặc định khởi động ở trạng thái chưa kết nối.

```powershell
$env:FL_COMMONS_TOKEN = .\.venv\Scripts\python -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\python -m fl_commons serve --native
```

## Kiểm chứng và giới hạn

**Đã kiểm chứng:** 79 kiểm thử Python và 28 kiểm thử native đã đạt cục bộ. Python CI đạt trên Windows, Linux và Python 3.10, 3.12, 3.14. Callback FL 26.1.7.5653 xác nhận Play → Pause → Play → Stop trong phiên kiểm thử được cho phép. CI Linux không kiểm chứng plugin FL.

Chưa triển khai sửa Mixer/kênh/dự án và sự kiện công khai. Lựa chọn thích ứng dùng hồ sơ giao diện đã triển khai; cập nhật xác minh hỗ trợ staging và rollback. Hợp đồng khác cần hồ sơ đã kiểm chứng; không tuyên bố khám phá vô hạn hay tương thích mọi build. Xem hướng dẫn tương thích.

[Validation](docs/validation.md) · [Native evidence](research/native-api-validation.json) · [Live transport](research/adaptive-native-transport-probe.json)

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## Tài liệu

Các liên kết dưới đây dẫn đến tài liệu chi tiết, hiện chủ yếu bằng tiếng Bồ Đào Nha. README chính bằng tiếng Anh; hoan nghênh sửa bản dịch.

- [Public API and Python SDK](docs/public-api.md)
- [Native build, installation and authentication](native/README.md)
- [HTTP API](docs/api.md) · [OpenAPI](docs/openapi.json)
- [Architecture](docs/design.md) · [Mission and roadmap](docs/master-spec-alignment.md)
- [Adaptive compatibility and trusted updates](docs/adaptive-compatibility.md)
- [SDK assessment](research/sdk-assessment.md) · [Research](research/README.md)
- [Optional MIDI integration](docs/setup-fl-studio.md)
- [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## Đóng góp và giấy phép

Đóng góp giao diện có tài liệu, bằng chứng tái lập được và kiểm thử. Tách mã gốc, tài liệu SDK và nghiên cứu. Một ký hiệu được tìm thấy hoặc kết quả mô phỏng không chứng minh khả năng điều khiển FL.

[Contributing](CONTRIBUTING.md) · [Request a capability](https://github.com/viy2tek/FL-Commons/issues/new?template=capability.yml)

Mã gốc FL Commons dùng giấy phép **MIT**. Không phân phối tệp SDK Image-Line hoặc DLL đã biên dịch tại đây; điều khoản SDK áp dụng riêng. FL Commons không liên kết, được bảo trợ hay được duy trì bởi Image-Line. FL Studio là nhãn hiệu của Image-Line.

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md)
