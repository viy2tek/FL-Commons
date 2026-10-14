// Original FL Commons plugin, MIT. Official SDK supplied separately.
#include "local_api.h"
#include <cstring>
#include <vector>
#include "transport_commands.h"
#include "session_token.h"
#pragma comment(lib, "version.lib")

namespace {
bool supported_process() {
    wchar_t path[32768];
    DWORD count = GetModuleFileNameW(nullptr, path, 32768);
    if (!count || count >= 32768) return false;
    const std::wstring name = std::wstring(path).substr(std::wstring(path).find_last_of(L"\\/") + 1);
    if (_wcsicmp(name.c_str(), L"FL64.exe") && _wcsicmp(name.c_str(), L"FL64 (scaled).exe")) return false;
    DWORD ignored = 0, length = GetFileVersionInfoSizeW(path, &ignored);
    if (!length) return false;
    std::vector<char> bytes(length);
    if (!GetFileVersionInfoW(path, 0, length, bytes.data())) return false;
    VS_FIXEDFILEINFO* info = nullptr; UINT size = 0;
    if (!VerQueryValueW(bytes.data(), L"\\", reinterpret_cast<void**>(&info), &size) || size < sizeof(*info)) return false;
    return info->dwSignature == 0xfeef04bd && info->dwProductVersionMS == MAKELONG(1, 26) &&
           info->dwProductVersionLS == MAKELONG(5653, 7);
}
std::string token_from_environment() {
    return flcommons::native_token();
}
char long_name[] = "FL Commons API", short_name[] = "FL Commons";
TFruityPlugInfo plugin_info{1, long_name, short_name,
    FPF_Type_Visual | FPF_CantSmartDisable, 0, 0, 0, 0, {}};

class Plugin final : public TFruityPlug {
    TFruityPlugHost& host_;
    const DWORD gui_ = GetCurrentThreadId();
    flcommons::LocalApi api_;
public:
    Plugin(TPluginTag tag, TFruityPlugHost& host)
        : host_(host), api_(token_from_environment(), 3211, "fl-native", host.HostVersion) {
        HostTag = tag; Info = &plugin_info;
        host_.Dispatcher(HostTag, FHD_WantIdle, 0, 2);
    }
    intptr_t __stdcall Dispatcher(intptr_t id, intptr_t, intptr_t value) override {
        if (id == FPD_SetPlaying) api_.set_playing(value != 0);
        return 0;
    }
    void __stdcall Idle_Public() override {
        api_.idle([this](const std::string& method) {
            const auto reply = flcommons::request_transport(host_, HostTag,
                method == "transport.stop" ? flcommons::TransportCommand::Stop : flcommons::TransportCommand::PlayPause, gui_);
            const char* disposition = "unknown";
            switch (reply.disposition) {
            case flcommons::Disposition::Handled: disposition = "handled"; break;
            case flcommons::Disposition::Delayed: disposition = "delayed"; break;
            case flcommons::Disposition::NotHandled: disposition = "not_handled"; break;
            case flcommons::Disposition::Unavailable: disposition = "unavailable"; break;
            case flcommons::Disposition::WrongThread: disposition = "wrong_thread"; break;
            default: break;
            }
            return std::string("{\"host_result\":") + std::to_string(reply.host_result) +
                   ",\"disposition\":\"" + disposition + "\"}";
        });
    }
    void __stdcall SaveRestoreState(IStream*, BOOL) override {}
    void __stdcall GetName(int, int, int, char* name) override { if (name) name[0] = 0; }
    int __stdcall ProcessEvent(int, int, int) override { return 0; }
    int __stdcall ProcessParam(int, int, int) override { return 0; }
    void __stdcall Eff_Render(PWAV32FS source, PWAV32FS destination, int length) override {
        if (source && destination && source != destination && length > 0)
            std::memcpy(destination, source, static_cast<size_t>(length) * sizeof(*source));
    }
    void __stdcall Gen_Render(PWAV32FS, int& length) override { length = 0; }
    TVoiceHandle __stdcall TriggerVoice(PVoiceParams, intptr_t) override { return 0; }
    void __stdcall Voice_Release(TVoiceHandle) override {}
    void __stdcall Voice_Kill(TVoiceHandle) override {}
    int __stdcall Voice_ProcessEvent(TVoiceHandle, intptr_t, intptr_t, intptr_t) override { return 0; }
    int __stdcall Voice_Render(TVoiceHandle, PWAV32FS, int& length) override { length = 0; return 0; }
    void __stdcall NewTick() override {}
    void __stdcall MIDITick() override {}
    void __stdcall MIDIIn(int&) override {}
    void __stdcall MsgIn(intptr_t) override {}
    int __stdcall OutputVoice_ProcessEvent(TOutVoiceHandle, intptr_t, intptr_t, intptr_t) override { return 0; }
    void __stdcall OutputVoice_Kill(TVoiceHandle) override {}
};
}

extern "C" __declspec(dllexport) TFruityPlug* __stdcall CreatePlugInstance(TFruityPlugHost* host, TPluginTag tag) {
    if (!host || !supported_process()) return nullptr;
    try { return new Plugin(tag, *host); }
    catch (...) { return nullptr; }
}
