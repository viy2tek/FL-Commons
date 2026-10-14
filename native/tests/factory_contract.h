// Official SDK ABI fact: Host pointer first, intptr_t Tag second.
#include <type_traits>
using OfficialFactory = TFruityPlug* (__stdcall *)(TFruityPlugHost*, TPluginTag);
static_assert(std::is_same_v<decltype(&CreatePlugInstance), OfficialFactory>,
              "CreatePlugInstance must receive (Host, Tag) in official SDK order");
