// Original FL Commons code, MIT. Include the separately supplied official SDK.
#pragma once
#include <windows.h>
#include <stdint.h>
#include "fp_plugclass.h"
#include "generictransport.h"

namespace flcommons {
enum class TransportCommand { PlayPause, Stop };
enum class Disposition { Handled, Delayed, NotHandled, Unavailable, Unknown,
                         InvalidCommand, WrongThread };
struct TransportReply {
    intptr_t host_result;
    Disposition disposition;
};

template <typename Dispatch>
TransportReply request_transport(TransportCommand command, Dispatch dispatch, DWORD gui_thread_id) {
    if (GetCurrentThreadId() != gui_thread_id)
        return {0, Disposition::WrongThread};
    intptr_t message;
    switch (command) {
    case TransportCommand::PlayPause: message = FPT_Play; break;
    case TransportCommand::Stop: message = FPT_Stop; break;
    default: return {0, Disposition::InvalidCommand};
    }
    const intptr_t result = dispatch(FHD_Transport, message, 1);
    switch (result) {
    case -1: return {result, Disposition::Unavailable};
    case 0: return {result, Disposition::NotHandled};
    case 5: return {result, Disposition::Delayed};
    case 1: case 2: case 4: case 8: return {result, Disposition::Handled};
    default: return {result, Disposition::Unknown};
    }
}

// The owner thread ID must be captured in the FL GUI callback creating the instance.
inline TransportReply request_transport(TFruityPlugHost& host, TPluginTag tag,
                                        TransportCommand command, DWORD gui_thread_id) {
    return request_transport(command, [&host, tag](intptr_t id, intptr_t index, intptr_t value) {
        return host.Dispatcher(tag, id, index, value);
    }, gui_thread_id);
}
} // namespace flcommons
