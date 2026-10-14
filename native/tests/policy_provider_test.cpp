#include "../compatibility_policy.h"
#include <iostream>
int main(int argc, char** argv) {
    if (argc != 3) return 2;
    SetEnvironmentVariableA("LOCALAPPDATA", argv[1]);
    std::cout << flcommons::native_allowed_methods(std::stoi(argv[2])) << std::endl;
}
