// Original controlled host, MIT. Does not emulate or prove FL compatibility.
#include "../local_api.h"
#include <iostream>
#include <cassert>
int main(int argc, char** argv) {
    if (argc != 4) return 2;
    flcommons::LocalApi api(argv[1], 0, "controlled-host");
    bool blocked = false;
    std::thread wrong_thread([&] {
        try { api.idle([](const std::string&) { return "{}"; }); }
        catch (const std::runtime_error&) { blocked = true; }
    });
    wrong_thread.join();
    assert(blocked);
    bool exclusive = false;
    try { flcommons::LocalApi second(argv[1], api.port(), "controlled-host"); }
    catch (const std::runtime_error&) { exclusive = true; }
    assert(exclusive);
    std::cout << api.port() << std::endl;
    const auto end = GetTickCount64() + std::stoul(argv[2]);
    int calls = 0;
    while (GetTickCount64() < end && !api.shutdown_requested()) {
        if (std::string(argv[3]) != "stalled" &&
            (std::string(argv[3]) != "paused" || GetTickCount64() >= end - 1000))
            api.idle([&](const std::string& method) -> std::string {
                ++calls;
                if (std::string(argv[3]) == "paused") assert(false && "Timed-out command executed");
                if (std::string(argv[3]) == "slow") Sleep(2500);
                if (std::string(argv[3]) == "large")
                    return std::string("{\"payload\":\"") + std::string(2000000, 'x') + "\"}";
                api.set_playing(method == "transport.play_pause");
                return "{\"host_result\":8,\"disposition\":\"handled\"}";
            });
        Sleep(5);
    }
    std::cout << "calls=" << calls << std::endl;
}
