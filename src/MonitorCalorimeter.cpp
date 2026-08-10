#include "MonitorCalorimeter.h"
#include <cstdlib>

MonitorCalorimeter::MonitorCalorimeter(std::string name, TFile* tfile) {
    m_time.push_back(new TH1D((name + "_time").c_str(), "Time;t [ns];Events", 500, 0, 1000));
    m_numHits.push_back(new TH1D((name + "_nHits").c_str(), "Hits;# Hits;Events", 6, -0.5, 5.5));
    m_amplitude.push_back(new TH1D((name + "_amplitude").c_str(), "Amplitude;QDC Counts;Events", 500, 0, 5000));
}

MonitorCalorimeter::~MonitorCalorimeter() {}

bool MonitorCalorimeter::Process() {
    if (!m_amplitude.empty() && m_amplitude[0]) {
        m_amplitude[0]->Fill(rand() % 4000);
    }
    return true;
}
