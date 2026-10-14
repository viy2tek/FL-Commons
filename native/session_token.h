// Original FL Commons code, MIT. Same user-bound DPAPI file as the Python launcher.
#pragma once
#include <windows.h>
#include <wincrypt.h>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>
#pragma comment(lib, "crypt32.lib")

namespace flcommons {
inline std::string native_token() {
    char environment[257];
    const DWORD token_size = GetEnvironmentVariableA("FL_COMMONS_TOKEN", environment, sizeof(environment));
    if (token_size) {
        if (token_size >= sizeof(environment)) throw std::runtime_error("Token exceeds limit");
        return std::string(environment, token_size);
    }
    wchar_t directory[32768];
    const DWORD length = GetEnvironmentVariableW(L"LOCALAPPDATA", directory, 32768);
    if (!length || length >= 32768) throw std::runtime_error("User data directory unavailable");
    const auto path = std::filesystem::path(directory) / L"FLCommons" / L"native-session.bin";
    std::ifstream stream(path, std::ios::binary | std::ios::ate);
    if (!stream) throw std::runtime_error("Run the FL Commons launcher to prepare authentication");
    const auto size = stream.tellg();
    if (size <= 0 || size > 4096) throw std::runtime_error("Invalid protected session file");
    std::vector<unsigned char> encrypted(static_cast<size_t>(size));
    stream.seekg(0);
    if (!stream.read(reinterpret_cast<char*>(encrypted.data()), encrypted.size()))
        throw std::runtime_error("Incomplete protected session file");
    DATA_BLOB source{static_cast<DWORD>(encrypted.size()), encrypted.data()}, result{};
    if (!CryptUnprotectData(&source, nullptr, nullptr, nullptr, nullptr, CRYPTPROTECT_UI_FORBIDDEN, &result))
        throw std::runtime_error("Session token cannot be decrypted for this Windows user");
    std::string token;
    try {
        if (result.cbData < 32 || result.cbData > 256) throw std::runtime_error("Invalid native token length");
        token.assign(reinterpret_cast<char*>(result.pbData), result.cbData);
    } catch (...) {
        SecureZeroMemory(result.pbData, result.cbData); LocalFree(result.pbData); throw;
    }
    SecureZeroMemory(result.pbData, result.cbData); LocalFree(result.pbData);
    return token;
}
}
