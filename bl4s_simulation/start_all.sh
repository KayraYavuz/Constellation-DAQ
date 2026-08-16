#!/bin/bash

# 1. Eski süreçleri temizleyelim (çakışma olmaması için)
pkill -f "bl4s_satellites"
pkill -f "SatelliteH5DataWriter"

# 1.5. Eski verileri arşive taşıyalım (Aynı run ID ile çakışma olmaması için)
echo "[0/4] Eski veriler arşive (eski_veriler) taşınıyor..."
mkdir -p /eos/user/k/kyavuz/bl4s_data/eski_veriler
mv /eos/user/k/kyavuz/bl4s_data/*.h5 /eos/user/k/kyavuz/bl4s_data/eski_veriler/ 2>/dev/null || true

# 2. Çevre değişkenlerini sıfırlayalım (CVMFS kirliliğini temizlemek için)
unset PYTHONPATH
unset LD_LIBRARY_PATH

echo "[1/4] Python Sanal Ortamına Geçiliyor..."
cd /home/kayra/bl4s_simulation
source venv/bin/activate

echo "[2/4] Simülasyon Uyduları Başlatılıyor..."
# nohup ve alt kabuk kullanarak çevre kirlenmesini tamamen engelliyoruz
nohup /home/kayra/bl4s_simulation/venv/bin/SatelliteH5DataWriter -g bl4s > datawriter.log 2>&1 &
nohup python3 src/bl4s_satellites/TriggerModuleSatellite.py -g bl4s > trigger.log 2>&1 &
nohup python3 src/bl4s_satellites/ScintillatorSatellite.py -g bl4s > scintillator.log 2>&1 &
nohup python3 src/bl4s_satellites/TimepixSatellite.py -g bl4s > timepix.log 2>&1 &
nohup python3 src/bl4s_satellites/CherenkovSatellite.py -g bl4s > cherenkov.log 2>&1 &
nohup python3 src/bl4s_satellites/CalorimeterSatellite.py -g bl4s > calorimeter.log 2>&1 &
nohup python3 src/bl4s_satellites/PrometheusExporter.py -g bl4s > prometheus.log 2>&1 &

# Python ortamından çıkıyoruz
deactivate

echo "[3/4] CVMFS Ortamı Yükleniyor..."
source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-el9-gcc13-opt/setup.sh

echo "[4/4] MissionControl Başlatılıyor..."
export DISPLAY=localhost:10.0
/home/kayra/constellation/build/cxx/controllers/MissionControl/MissionControl
