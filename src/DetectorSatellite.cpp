#include <chrono>
#include <cstdint>
#include <stop_token>
#include <thread>
#include <vector>

#include <zmq.hpp>

#include <constellation/core/config/Configuration.hpp>
#include <constellation/core/message/CDTP2Message.hpp>
#include <constellation/core/message/PayloadBuffer.hpp>
#include <constellation/satellite/TransmitterSatellite.hpp>

class DetectorSatellite : public constellation::satellite::TransmitterSatellite {
public:
    DetectorSatellite(std::string_view type, std::string_view name) : TransmitterSatellite(type, name) {}

protected:
    void initializing(constellation::config::Configuration& config) override {
        detector_id_ = config.has("detector_id") ? config.get<int>("detector_id") : 1;
    }

    void running(const std::stop_token& stop_token) override {
        while (!stop_token.stop_requested()) {
            std::vector<std::uint8_t> dummy_event_data = {0xDE, 0xAD, 0xBE, 0xEF, static_cast<std::uint8_t>(detector_id_)};

            auto record = newDataRecord();
            record.addTag("detector_id", detector_id_);

            zmq::message_t msg(dummy_event_data.data(), dummy_event_data.size());
            record.addBlock(constellation::message::PayloadBuffer(std::move(msg)));

            sendDataRecord(std::move(record));

            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }

private:
    int detector_id_{1};
};

#include "constellation/build.hpp"
extern "C" {
CNSTLN_DLL_EXPORT
std::shared_ptr<constellation::satellite::Satellite> generator(std::string_view type, std::string_view name) {
    return std::make_shared<DetectorSatellite>(type, name);
}
}
