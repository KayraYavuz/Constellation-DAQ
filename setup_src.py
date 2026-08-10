import os

src_dir = os.path.expanduser("~/bl4s_daq_sim/src")
os.makedirs(src_dir, exist_ok=True)

f_detector = """#include 
#include 
#include 
#include 
#include 
#include 

#include 
#include 

class DetectorSatellite : public constellation::satellite::Satellite {
public:
    using Satellite::Satellite;

protected:
    void initializing(constellation::config::Configuration& config) override {
        detector_id_ = config.has("detector_id") ? config.get("detector_id") : 1;
    }

    void running(const std::stop_token& stop_token) override {
        while (!stop_token.stop_requested()) {
            std::vector dummy_event_data = {0xDE, 0xAD, 0xBE, 0xEF, static_cast(detector_id_)};

            auto msg = constellation::message::CDTP2Message();
            msg.add_header("detector_id", detector_id_);
            msg.add_data(dummy_event_data.data(), dummy_event_data.size());

            send_payload(std::move(msg));
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }

private:
    int detector_id_{1};
};

CONSTELLATION_SATELLITE_MAIN(DetectorSatellite)
"""

f_trigger = """#include 
#include 
#include 
#include 
#include 
#include 

#include 
#include 

class PollingTriggerSatellite : public constellation::satellite::Satellite {
public:
    using Satellite::Satellite;

protected:
    void initializing(constellation::config::Configuration& config) override {
        polling_interval_us_ = config.has("polling_interval_us") ? config.get("polling_interval_us") : 100;
    }

    void running(const std::stop_token& stop_token) override {
        auto interval = std::chrono::microseconds(polling_interval_us_);

        while (!stop_token.stop_requested()) {
            if (check_coincidence()) {
                auto trigger_msg = constellation::message::CDTP2Message();
                trigger_msg.add_header("event_id", current_event_id_++);
                trigger_msg.add_header("trigger_type", "COINCIDENCE");

                send_payload(std::move(trigger_msg));
            }
            std::this_thread::sleep_for(interval);
        }
    }

private:
    bool check_coincidence() {
        return (rand() % 10 == 0);
    }

    int polling_interval_us_{100};
    std::uint64_t current_event_id_{0};
};

CONSTELLATION_SATELLITE_MAIN(PollingTriggerSatellite)
"""

f_stop = """#include 
#include 

#include 
#include 

class StopControllerSatellite : public constellation::satellite::Satellite {
public:
    using Satellite::Satellite;

protected:
    void initializing(constellation::config::Configuration& config) override {
        max_events_ = config.has("max_events") ? config.get("max_events") : 1000;
        event_count_ = 0;
    }

    void running(const std::stop_token& stop_token) override {
        while (!stop_token.stop_requested()) {
            auto msg = receive_payload();
            if (msg) {
                event_count_++;
                if (event_count_ >= max_events_) {
                    break;
                }
            }
        }
    }

private:
    std::uint64_t max_events_{1000};
    std::uint64_t event_count_{0};
};

CONSTELLATION_SATELLITE_MAIN(StopControllerSatellite)
"""

f_calorimeter = """#include 
#include 
#include 

#include 

#include 
#include 

#include "MonitorCalorimeter.h"

class CalorimeterMonitorSatellite : public constellation::satellite::Satellite {
public:
    using Satellite::Satellite;

protected:
    void initializing(constellation::config::Configuration& config) override {
        std::string root_file_path = config.has("output_root_file") ? config.get("output_root_file") : "calorimeter_mon.root";
        tfile_ = new TFile(root_file_path.c_str(), "RECREATE");
        monitor_ = std::make_unique("CalorimeterMonitor", tfile_);
    }

    void running(const std::stop_token& stop_token) override {
        while (!stop_token.stop_requested()) {
            auto msg = receive_payload();
            if (!msg) continue;
            monitor_->Process();
        }
    }

    void stopping() override {
        if (tfile_ && tfile_->IsOpen()) {
            tfile_->cd();
            tfile_->Write();
        }
    }

    void deconstructing() override {
        if (tfile_) {
            tfile_->Close();
            delete tfile_;
            tfile_ = nullptr;
        }
    }

private:
    TFile* tfile_{nullptr};
    std::unique_ptr monitor_{nullptr};
};

CONSTELLATION_SATELLITE_MAIN(CalorimeterMonitorSatellite)
"""

with open(os.path.join(src_dir, "DetectorSatellite.cpp"), "w") as f:
    f.write(f_detector)

with open(os.path.join(src_dir, "PollingTriggerSatellite.cpp"), "w") as f:
    f.write(f_trigger)

with open(os.path.join(src_dir, "StopControllerSatellite.cpp"), "w") as f:
    f.write(f_stop)

with open(os.path.join(src_dir, "CalorimeterMonitorSatellite.cpp"), "w") as f:
    f.write(f_calorimeter)

print("Tum C++ kaynak dosyalari basariyla olusturuldu.")
