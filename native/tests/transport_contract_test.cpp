// Original FL Commons code, MIT. SDK headers are provided separately by the user.
#include <windows.h>
#include <stdint.h>
#include <cassert>
#include "../transport_commands.h"

static int calls = 0;
static intptr_t last_id, last_index, last_value;
static intptr_t answer = 8;
static intptr_t call_host(intptr_t id, intptr_t index, intptr_t value) {
    ++calls;
    last_id = id;
    last_index = index;
    last_value = value;
    return answer;
}

int main() {
    using namespace flcommons;
    const DWORD gui = GetCurrentThreadId();
    auto reply = request_transport(TransportCommand::PlayPause, call_host, gui);
    assert(calls == 1 && last_id == 79 && last_index == 10 && last_value == 1);
    assert(reply.host_result == 8 && reply.disposition == Disposition::Handled);
    answer = 5;
    reply = request_transport(TransportCommand::Stop, call_host, gui);
    assert(calls == 2 && last_id == 79 && last_index == 11 && last_value == 1);
    assert(reply.disposition == Disposition::Delayed);
    answer = 0;
    assert(request_transport(TransportCommand::Stop, call_host, gui).disposition == Disposition::NotHandled);
    answer = -1;
    assert(request_transport(TransportCommand::Stop, call_host, gui).disposition == Disposition::Unavailable);
    answer = 1234;
    assert(request_transport(TransportCommand::Stop, call_host, gui).disposition == Disposition::Unknown);
    const int before = calls;
    reply = request_transport(static_cast<TransportCommand>(100), call_host, gui);
    assert(reply.disposition == Disposition::InvalidCommand && calls == before);
    reply = request_transport(TransportCommand::Stop, call_host, 0);
    assert(reply.disposition == Disposition::WrongThread && calls == before);
    assert(sizeof(TPluginTag) == sizeof(void*));
    return 0;
}
