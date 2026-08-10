#include <cstdint>
#include <string>

#include <constellation/core/config/Configuration.hpp>
#include <constellation/satellite/ReceiverSatellite.hpp>

class StopControllerSatellite : public constellation::satellite::ReceiverSatellite {
public:
    StopControllerSatellite(std::string_view type, std::string_view name) : ReceiverSatellite(type, name) {}

protected:
    void initializing(constellation::config::Configuration& config) override {
        max_events_ = config.has("max_events") ? config.get<std::uint64_t>("max_events") : 1000;
        event_count_ = 0;
    }

    void receive_bor(std::string_view /*sender*/,
                      const constellation::config::Dictionary& /*user_tags*/,
                      const constellation::config::Dictionary& /*config*/) override {
        event_count_ = 0;
    }

    void receive_data(std::string_view /*sender*/,
                       const constellation::message::CDTP2Message::DataRecord& /*data_record*/) override {
        event_count_++;
        if (event_count_ >= max_events_) {
            getFSM().requestInterrupt("Maksimum olay sayısına ulaşıldı");
        }
    }

    void receive_eor(std::string_view /*sender*/,
                      const constellation::config::Dictionary& /*user_tags*/,
                      const constellation::config::Dictionary& /*run_metadata*/) override {}

private:
    std::uint64_t event_count_{0};
    std::uint64_t max_events_{1000};
};

#include "constellation/build.hpp"
extern "C" {
CNSTLN_DLL_EXPORT
std::shared_ptr<constellation::satellite::Satellite> generator(std::string_view type, std::string_view name) {
    return std::make_shared<StopControllerSatellite>(type, name);
}
}
