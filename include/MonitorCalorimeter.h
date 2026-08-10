#ifndef MONITOR_CALORIMETER_H
#define MONITOR_CALORIMETER_H

#include <string>
#include <vector>
#include <TH1D.h>
#include <TFile.h>

class MonitorCalorimeter {
public:
    MonitorCalorimeter(std::string name, TFile* tfile);
    ~MonitorCalorimeter();
    bool Process();

private:
    std::vector<TH1D*> m_time;
    std::vector<TH1D*> m_numHits;
    std::vector<TH1D*> m_amplitude;
};

#endif
