// Original FL Commons code, MIT. Windows loopback API, independent of SDK headers.
#pragma once
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <bcrypt.h>
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <functional>
#include <map>
#include <memory>
#include <mutex>
#include <regex>
#include <stdexcept>
#include <string>
#include <thread>
#pragma comment(lib, "ws2_32.lib")
#pragma comment(lib, "bcrypt.lib")

namespace flcommons {
class LocalApi {
    struct Pending {
        std::string method, result;
        bool started = false, done = false, cancelled = false;
    };
    SOCKET listener_ = INVALID_SOCKET, active_ = INVALID_SOCKET;
    std::string token_, mode_, build_;
    bool abi_available_;
    unsigned methods_;
    unsigned short port_ = 0;
    DWORD owner_ = GetCurrentThreadId();
    std::atomic<bool> stopping_{false};
    std::atomic<int> playing_{-1};
    std::atomic<ULONGLONG> last_idle_{0};
    std::string session_id_;
    int host_version_;
    std::mutex socket_mutex_, queue_mutex_;
    std::condition_variable changed_;
    std::shared_ptr<Pending> pending_;
    std::thread worker_;

    static std::string lower(std::string s) {
        for (char& c : s) if (c >= 'A' && c <= 'Z') c += 'a' - 'A';
        return s;
    }
    static std::string trim(std::string s) {
        const auto first = s.find_first_not_of(" \t");
        if (first == std::string::npos) return {};
        return s.substr(first, s.find_last_not_of(" \t") - first + 1);
    }
    static void respond(SOCKET s, int status, const std::string& json) {
        const std::string message = "HTTP/1.1 " + std::to_string(status) + " Response\r\n"
            "Content-Type: application/json\r\nConnection: close\r\nCache-Control: no-store\r\n"
            "Content-Length: " + std::to_string(json.size()) + "\r\n\r\n" + json;
        size_t offset = 0;
        while (offset < message.size()) {
            const int n = send(s, message.data() + offset, static_cast<int>(message.size() - offset), 0);
            if (n <= 0) break;
            offset += n;
        }
    }
    static void error(SOCKET s, int status, const char* code) {
        respond(s, status, std::string("{\"error\":{\"code\":\"") + code + "\",\"message\":\"" + code + "\"}}");
    }
    bool authenticated(const std::string& value) const {
        const std::string expected = "Bearer " + token_;
        unsigned difference = static_cast<unsigned>(value.size() ^ expected.size());
        for (size_t i = 0; i < expected.size(); ++i)
            difference |= static_cast<unsigned char>(expected[i]) ^
                          static_cast<unsigned char>(i < value.size() ? value[i] : 0);
        return difference == 0;
    }
    std::string available_methods() const {
        std::string json = "[";
        const char* names[] = {"transport.state", "transport.play_pause", "transport.stop"};
        for (unsigned i = 0; i < 3; ++i) if (abi_available_ && (methods_ & (1u << i))) {
            if (json.size() > 1) json += ",";
            json += std::string("\"") + names[i] + "\"";
        }
        return json + "]";
    }
    std::string compatibility() const {
        const auto idle = last_idle_.load();
        const auto age = idle ? std::to_string(GetTickCount64() - idle) : "null";
        return "{\"profile\":\"fpsdk-20210311b-transport-v1\",\"mode\":\"" + mode_ +
            "\",\"session_id\":\"" + session_id_ + "\",\"fl_build\":" +
            (mode_ == "fl-native" ? "\"" + build_ + "\"" : "null") +
            ",\"runtime_contract\":" + (abi_available_ ? "\"fpsdk-20210311b-v1\"" : "null") +
            ",\"host_version_raw\":" + std::to_string(host_version_) +
            ",\"gui_dispatch_observed\":" + (idle ? "true" : "false") +
            ",\"gui_responsive\":" + (idle && GetTickCount64() - idle <= 2000 ? "true" : "false") +
            ",\"last_gui_idle_age_ms\":" + age +
            ",\"state_callback_observed\":" + (playing_.load() >= 0 ? "true" : "false") +
            ",\"available_operations\":" + available_methods() +
            ",\"fl_runtime_validated\":false,\"automatic_updates\":false,\"operations\":["
            "{\"method\":\"transport.state\",\"interface\":\"FPD_SetPlaying\","
            "\"validation\":\"unverified\",\"experimental\":true,\"automatically_probed\":false},"
            "{\"method\":\"transport.play_pause\",\"interface\":\"FHD_Transport/FPT_Play\","
            "\"validation\":\"unverified\",\"experimental\":true,\"automatically_probed\":false},"
            "{\"method\":\"transport.stop\",\"interface\":\"FHD_Transport/FPT_Stop\","
            "\"validation\":\"unverified\",\"experimental\":true,\"automatically_probed\":false}]}";
    }
    int receive(SOCKET socket, char* buffer, int length, ULONGLONG deadline) {
        while (!stopping_ && GetTickCount64() < deadline) {
            fd_set ready; FD_ZERO(&ready); FD_SET(socket, &ready);
            timeval timeout{0, 50000};
            const int result = select(0, &ready, nullptr, nullptr, &timeout);
            if (result < 0) return -1;
            if (result > 0) return recv(socket, buffer, length, 0);
        }
        return -1;
    }
    void handle(SOCKET socket) {
        const auto deadline = GetTickCount64() + 2000;
        std::string request;
        char buffer[2048];
        size_t boundary;
        while ((boundary = request.find("\r\n\r\n")) == std::string::npos) {
            const int n = receive(socket, buffer, sizeof(buffer), deadline);
            if (n <= 0) return;
            request.append(buffer, n);
            if (request.size() > 8192) { error(socket, 413, "request_too_large"); return; }
        }
        const auto first_end = request.find("\r\n");
        const std::string line = request.substr(0, first_end);
        const auto space = line.find(' '), last = line.rfind(' ');
        if (space == std::string::npos || space == last || line.substr(last + 1) != "HTTP/1.1") {
            error(socket, 400, "invalid_request"); return;
        }
        const std::string verb = line.substr(0, space), path = line.substr(space + 1, last - space - 1);
        std::map<std::string, std::string> headers;
        size_t start = first_end + 2;
        while (start < boundary) {
            const auto end = request.find("\r\n", start), colon = request.find(':', start);
            if (colon == std::string::npos || colon >= end) { error(socket, 400, "invalid_headers"); return; }
            const std::string key = lower(request.substr(start, colon - start));
            if (key.empty() || key.find_first_not_of("abcdefghijklmnopqrstuvwxyz0123456789-") != std::string::npos ||
                !headers.emplace(key, trim(request.substr(colon + 1, end - colon - 1))).second) {
                error(socket, 400, "invalid_headers"); return;
            }
            start = end + 2;
        }
        if (headers["host"] != "127.0.0.1:" + std::to_string(port_) || headers.count("origin")) {
            error(socket, 403, "forbidden_origin"); return;
        }
        if (!authenticated(headers["authorization"])) { error(socket, 401, "unauthorized"); return; }
        if (headers.count("transfer-encoding")) { error(socket, 400, "invalid_headers"); return; }
        size_t length = 0;
        if (headers.count("content-length")) {
            const auto& value = headers["content-length"];
            if (value.empty() || value.size() > 4 || value.find_first_not_of("0123456789") != std::string::npos) {
                error(socket, 400, "invalid_length"); return;
            }
            length = std::stoul(value);
            if (length > 1024) { error(socket, 413, "request_too_large"); return; }
        }
        if (verb == "GET" && length == 0) {
            if (path == "/v1/health") respond(socket, 200, "{\"status\":\"ok\"}");
            else if (path == "/v1/capabilities") respond(socket, 200,
                "{\"api_version\":\"0.1.0\",\"mode\":\"" + mode_ + "\",\"compatibility\":\"unverified\","
                "\"target_build\":" + (mode_ == "fl-native" ? "\"" + build_ + "\"" : "null") +
                ",\"runtime_contract\":" + (abi_available_ ? "\"fpsdk-20210311b-v1\"" : "null") +
                ",\"capabilities\":" + available_methods() + "}");
            else if (path == "/v1/compatibility") respond(socket, 200, compatibility());
            else error(socket, 404, "not_found");
            return;
        }
        if (verb != "POST" || path != "/v1/commands") { error(socket, 404, "not_found"); return; }
        if (!headers.count("content-length") || headers["content-type"] != "application/json") {
            error(socket, 400, "invalid_body"); return;
        }
        std::string body = request.substr(boundary + 4);
        while (body.size() < length) {
            const int n = receive(socket, buffer, sizeof(buffer), deadline);
            if (n <= 0) return;
            body.append(buffer, n);
        }
        if (body.size() != length) { error(socket, 400, "invalid_body"); return; }
        // shortcut: closed ASCII command schema; add a full JSON parser when parameters are introduced.
        static const std::regex schema(
            R"json(^[ \t\r\n]*\{[ \t\r\n]*"method"[ \t\r\n]*:[ \t\r\n]*"([a-z_.]+)"[ \t\r\n]*,[ \t\r\n]*"params"[ \t\r\n]*:[ \t\r\n]*\{[ \t\r\n]*\}[ \t\r\n]*\}[ \t\r\n]*$)json");
        static const std::regex reversed(
            R"json(^[ \t\r\n]*\{[ \t\r\n]*"params"[ \t\r\n]*:[ \t\r\n]*\{[ \t\r\n]*\}[ \t\r\n]*,[ \t\r\n]*"method"[ \t\r\n]*:[ \t\r\n]*"([a-z_.]+)"[ \t\r\n]*\}[ \t\r\n]*$)json");
        std::smatch match;
        if (!std::regex_match(body, match, schema) && !std::regex_match(body, match, reversed)) {
            error(socket, 400, "invalid_body"); return;
        }
        const std::string method = match[1];
        if (!abi_available_) { error(socket, 409, "capability_unavailable"); return; }
        unsigned bit = method == "transport.state" ? 1 : method == "transport.play_pause" ? 2 : method == "transport.stop" ? 4 : 0;
        if (bit && !(methods_ & bit)) { error(socket, 409, "capability_unavailable"); return; }
        if (method == "transport.state") {
            const int state = playing_.load();
            respond(socket, 200, std::string("{\"result\":{\"playing\":") +
                (state < 0 ? "null" : state ? "true" : "false") + ",\"source\":\"host_callback\"}}");
            return;
        }
        if (method != "transport.play_pause" && method != "transport.stop") {
            error(socket, 422, "unsupported"); return;
        }
        auto operation = std::make_shared<Pending>();
        operation->method = method;
        std::unique_lock<std::mutex> lock(queue_mutex_);
        if (stopping_ || pending_) { lock.unlock(); error(socket, 503, "busy"); return; }
        pending_ = operation;
        if (!changed_.wait_for(lock, std::chrono::seconds(2), [&] { return operation->done || stopping_; })) {
            operation->cancelled = true;
            if (!operation->started) pending_.reset();
            const bool started = operation->started;
            lock.unlock();
            error(socket, 504, started ? "outcome_unknown" : "not_executed");
        } else if (!operation->done) {
            lock.unlock(); error(socket, 503, "unavailable");
        } else {
            const auto result = operation->result;
            lock.unlock();
            respond(socket, 200, "{\"result\":" + result + "}");
        }
    }
    void serve() noexcept {
        while (!stopping_) {
            fd_set ready; FD_ZERO(&ready); FD_SET(listener_, &ready);
            timeval timeout{0, 100000};
            if (select(0, &ready, nullptr, nullptr, &timeout) <= 0) continue;
            SOCKET client = accept(listener_, nullptr, nullptr);
            if (client == INVALID_SOCKET) continue;
            {
                std::lock_guard<std::mutex> lock(socket_mutex_);
                active_ = client;
                if (stopping_) shutdown(client, SD_BOTH);
            }
            DWORD milliseconds = 2000;
            setsockopt(client, SOL_SOCKET, SO_RCVTIMEO, reinterpret_cast<char*>(&milliseconds), sizeof(milliseconds));
            setsockopt(client, SOL_SOCKET, SO_SNDTIMEO, reinterpret_cast<char*>(&milliseconds), sizeof(milliseconds));
            try { handle(client); } catch (...) { error(client, 500, "internal_error"); }
            {
                std::lock_guard<std::mutex> lock(socket_mutex_);
                closesocket(client); active_ = INVALID_SOCKET;
            }
        }
    }
public:
    LocalApi(std::string token, unsigned short port, std::string mode, int host_version = 0,
             std::string build = "", bool abi_available = true, unsigned methods = 7)
        : token_(std::move(token)), mode_(std::move(mode)), build_(std::move(build)),
          abi_available_(abi_available), methods_(methods), host_version_(host_version) {
        if (mode_ == "fl-native" && !std::regex_match(build_, std::regex("[0-9]{1,5}(\\.[0-9]{1,5}){3}")))
            throw std::runtime_error("Invalid native build metadata");
        if (token_.size() < 32 || token_.size() > 256 ||
            token_.find_first_not_of("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-") != std::string::npos)
            throw std::runtime_error("Token must contain 32..256 ASCII letters, digits, underscore or hyphen");
        unsigned char identifier[16];
        if (BCryptGenRandom(nullptr, identifier, sizeof(identifier), BCRYPT_USE_SYSTEM_PREFERRED_RNG) < 0)
            throw std::runtime_error("Session identifier generation failed");
        const char* digits = "0123456789abcdef";
        for (auto byte : identifier) {
            session_id_ += digits[byte >> 4]; session_id_ += digits[byte & 15];
        }
        WSADATA data;
        if (WSAStartup(MAKEWORD(2, 2), &data)) throw std::runtime_error("Winsock initialization failed");
        try {
            listener_ = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
            if (listener_ == INVALID_SOCKET) throw std::runtime_error("Socket failed");
            BOOL exclusive = TRUE;
            if (setsockopt(listener_, SOL_SOCKET, SO_EXCLUSIVEADDRUSE, reinterpret_cast<char*>(&exclusive), sizeof(exclusive)))
                throw std::runtime_error("Socket ownership failed");
            sockaddr_in address{};
            address.sin_family = AF_INET; address.sin_addr.s_addr = htonl(INADDR_LOOPBACK); address.sin_port = htons(port);
            if (bind(listener_, reinterpret_cast<sockaddr*>(&address), sizeof(address)) || listen(listener_, 4))
                throw std::runtime_error("Loopback port unavailable");
            int size = sizeof(address);
            if (getsockname(listener_, reinterpret_cast<sockaddr*>(&address), &size)) throw std::runtime_error("Port lookup failed");
            port_ = ntohs(address.sin_port);
            worker_ = std::thread([this] { serve(); });
        } catch (...) { if (listener_ != INVALID_SOCKET) closesocket(listener_); WSACleanup(); throw; }
    }
    ~LocalApi() {
        stopping_ = true;
        { std::lock_guard<std::mutex> lock(queue_mutex_); if (pending_) pending_->cancelled = true; }
        changed_.notify_all();
        { std::lock_guard<std::mutex> lock(socket_mutex_); if (active_ != INVALID_SOCKET) shutdown(active_, SD_BOTH); }
        if (worker_.joinable()) worker_.join();
        closesocket(listener_); WSACleanup();
    }
    LocalApi(const LocalApi&) = delete;
    LocalApi& operator=(const LocalApi&) = delete;
    unsigned short port() const { return port_; }
    bool shutdown_requested() const { return stopping_; }
    void set_playing(bool value) { playing_ = value ? 1 : 0; }
    void idle(const std::function<std::string(const std::string&)>& dispatch) {
        if (GetCurrentThreadId() != owner_) throw std::runtime_error("Host dispatch requires owner thread");
        last_idle_ = GetTickCount64();
        std::shared_ptr<Pending> operation;
        {
            std::lock_guard<std::mutex> lock(queue_mutex_);
            if (!pending_ || pending_->cancelled || stopping_) return;
            operation = pending_; operation->started = true;
        }
        std::string result;
        try { result = dispatch(operation->method); }
        catch (...) { result = "{\"host_result\":null,\"disposition\":\"unknown\"}"; }
        {
            std::lock_guard<std::mutex> lock(queue_mutex_);
            operation->result = std::move(result); operation->done = true;
            if (pending_ == operation) pending_.reset();
        }
        changed_.notify_all();
    }
};
}
