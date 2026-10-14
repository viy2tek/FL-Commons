#include "../session_token.h"
#include <cassert>
int wmain(int argc, wchar_t** argv) {
    if (argc != 2) return 2;
    SetEnvironmentVariableW(L"LOCALAPPDATA", argv[1]);
    SetEnvironmentVariableA("FL_COMMONS_TOKEN", nullptr);
    try {
        assert(flcommons::native_token() == std::string(64, 'a'));
        SetEnvironmentVariableA("FL_COMMONS_TOKEN", std::string(64, 'b').c_str());
        assert(flcommons::native_token() == std::string(64, 'b'));
        SetEnvironmentVariableA("FL_COMMONS_TOKEN", std::string(300, 'c').c_str());
        bool refused = false;
        try { flcommons::native_token(); } catch (const std::runtime_error&) { refused = true; }
        assert(refused);
    } catch (const std::runtime_error&) { return 1; }
    return 0;
}
