#include <chrono>
#include <cstdint>
#include <stop_token>
#include <thread>

#include <constellation/core/config/Configuration.hpp>
#include <constellation/core/message/CDTP2Message.hpp>
#include <constellation/satellite/TransmitterSatellite.hpp>

class PollingTriggerSatellite : public constellation::satellite::TransmitterSatellite {
public:
    PollingTriggerSatellite(std::string_view type, std::string_view name) : TransmitterSatellite(type, name) {}

protected:
    void initializing(constellation::config::Configuration& config) override {
        polling_interval_us_ = config.has("polling_interval_us") ? config.get<std::uint64_t>("polling_interval_us") : 1000;
    }

    void running(const std::stop_token& stop_token) override {
        auto interval = std::chrono::microseconds(polling_interval_us_);
        while (!stop_token.stop_requested()) {
            if (check_coincidence()) {
                auto record = newDataRecord();
                record.addTag("event_id", current_event_id_++);
                sendDataRecord(std::move(record));
            }
            std::this_thread::sleep_for(interval);
        }
    }

private:
    bool check_coincidence() {
        // TODO: gerçek çakışma (coincidence) mantığını buraya ekleyin
        return true;
    }

    std::uint64_t polling_interval_us_{1000};
    std::uint64_t current_event_id_{0};
};

#include "constellation/build.hpp"
extern "C" {
CNSTLN_DLL_EXPORT
std::shared_ptr<constellation::satellite::Satellite> generator(std::string_view type, std::string_view name) {
    return std::make_shared<PollingTriggerSatellite>(type, name);
}
}
