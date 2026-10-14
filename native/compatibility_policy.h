// Original FL Commons. User-bound policy prepared by the verified installer.
#pragma once
#include <windows.h>
#include <wincrypt.h>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <regex>
#include <vector>
#pragma comment(lib, "crypt32.lib")
#pragma comment(lib, "advapi32.lib")

namespace flcommons {
inline std::string module_sha256() {
    HMODULE module = nullptr;
    if (!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                           reinterpret_cast<LPCWSTR>(&module_sha256), &module)) return {};
    wchar_t name[32768];
    if (!GetModuleFileNameW(module, name, 32768)) return {};
    std::ifstream input(std::filesystem::path(name), std::ios::binary);
    HCRYPTPROV provider = 0; HCRYPTHASH hash = 0;
    if (!input || !CryptAcquireContextW(&provider, nullptr, nullptr, PROV_RSA_AES, CRYPT_VERIFYCONTEXT)) return {};
    if (!CryptCreateHash(provider, CALG_SHA_256, 0, 0, &hash)) { CryptReleaseContext(provider, 0); return {}; }
    char buffer[8192]; bool valid = true;
    while (input.read(buffer, sizeof(buffer)) || input.gcount())
        if (!CryptHashData(hash, reinterpret_cast<BYTE*>(buffer), static_cast<DWORD>(input.gcount()), 0)) { valid = false; break; }
    BYTE digest[32]; DWORD length = sizeof(digest);
    valid = valid && input.eof() && CryptGetHashParam(hash, HP_HASHVAL, digest, &length, 0);
    CryptDestroyHash(hash); CryptReleaseContext(provider, 0);
    if (!valid) return {};
    std::string result; const char* digits = "0123456789abcdef";
    for (auto byte : digest) { result += digits[byte >> 4]; result += digits[byte & 15]; }
    return result;
}

inline unsigned native_allowed_methods(int host_api) {
    // Built-in contract evidence survives a missing/corrupt optional update policy.
    const unsigned fallback = host_api == 26001007 ? 7 : 0;
    wchar_t directory[32768];
    DWORD length = GetEnvironmentVariableW(L"LOCALAPPDATA", directory, 32768);
    if (!length || length >= 32768) return fallback;
    const auto policy_path = std::filesystem::path(directory) / L"FLCommons/native-policy.bin";
    if (!std::filesystem::exists(policy_path)) return fallback;
    std::ifstream input(policy_path, std::ios::binary | std::ios::ate);
    if (!input || input.tellg() <= 0 || input.tellg() > 4096) return 0;
    std::vector<BYTE> data(static_cast<size_t>(input.tellg())); input.seekg(0);
    if (!input.read(reinterpret_cast<char*>(data.data()), data.size())) return 0;
    DATA_BLOB source{static_cast<DWORD>(data.size()), data.data()}, plain{};
    if (!CryptUnprotectData(&source, nullptr, nullptr, nullptr, nullptr, CRYPTPROTECT_UI_FORBIDDEN, &plain)) return 0;
    std::string record;
    if (plain.cbData <= 512) record.assign(reinterpret_cast<char*>(plain.pbData), plain.cbData);
    SecureZeroMemory(plain.pbData, plain.cbData); LocalFree(plain.pbData);
    std::smatch fields;
    if (!std::regex_match(record, fields, std::regex("FLCommons-policy-v1\n([0-9a-f]{64})\nfpsdk-20210311b-v1\n([0-9]{8,11})\n([1-7])\n"))) return 0;
    if (fields[1].str() != module_sha256() || fields[2].str() != std::to_string(host_api)) return 0;
    return static_cast<unsigned>(std::stoi(fields[3].str()));
}
}
