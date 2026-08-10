#include <filesystem>
#include "constellation/exec/cli.hpp"
#include "constellation/exec/satellite.hpp"
using namespace constellation::exec;
int main(int argc, char** argv) {
    SatelliteType type("Detector", std::filesystem::path(BUILD_LIBDIR));
    return satellite_main(to_span(argc, argv), "SatelliteDetector", type);
}
