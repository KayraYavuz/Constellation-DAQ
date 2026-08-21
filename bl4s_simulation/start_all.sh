#!/bin/bash

# 1. Eski süreçleri temizleyelim (çakışma olmaması için)
echo "[0/5] Eski uydular ve DAQ süreçleri temizleniyor..."
pkill -9 -f "bl4s_satellites" 2>/dev/null || true
pkill -9 -f "SatelliteH5DataWriter" 2>/dev/null || true
pkill -9 -f "bl4s_event_explorer_server" 2>/dev/null || true

# 1.5. Eski verileri arşive taşıyalım ve Python bytecode önbelleğini temizleyelim
echo "[1/5] Eski veriler arşive taşınıyor ve önbellek temizleniyor..."
mkdir -p /home/kayra/bl4s_simulation/eski_veriler
mv /home/kayra/bl4s_simulation/*.h5 /home/kayra/bl4s_simulation/eski_veriler/ 2>/dev/null || true
find /home/kayra/bl4s_simulation -name "*.pyc" -delete 2>/dev/null || true
find /home/kayra/bl4s_simulation -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 2. Çevre değişkenlerini sıfırlayalım (CVMFS kirliliğini temizlemek için)
unset PYTHONPATH
unset LD_LIBRARY_PATH

echo "[2/5] Python Sanal Ortamına Geçiliyor..."
cd /home/kayra/bl4s_simulation
source venv/bin/activate

echo "[3/5] Tüm Dedektör, Rekonstrüksiyon ve ML Uyduları Başlatılıyor..."
# Temel Dedektör Uyduları & Veri Kaydedici
nohup /home/kayra/bl4s_simulation/venv/bin/SatelliteH5DataWriter -g bl4s > datawriter.log 2>&1 &
nohup python3 src/bl4s_satellites/TriggerModuleSatellite.py -g bl4s > trigger.log 2>&1 &
nohup python3 src/bl4s_satellites/ScintillatorSatellite.py -g bl4s > scintillator.log 2>&1 &
nohup python3 src/bl4s_satellites/DWCSatellite.py -g bl4s > dwc.log 2>&1 &
nohup python3 src/bl4s_satellites/TimepixSatellite.py -g bl4s > timepix.log 2>&1 &
nohup python3 src/bl4s_satellites/CherenkovSatellite.py -g bl4s > cherenkov.log 2>&1 &
nohup python3 src/bl4s_satellites/CalorimeterSatellite.py -g bl4s > calorimeter.log 2>&1 &

# İleri Düzey Event Builder, Fizik Rekonstrüksiyon, ML & Telemetri Uyduları
nohup python3 src/bl4s_satellites/CoincidenceEventBuilder.py -g bl4s > coincidence.log 2>&1 &
nohup python3 src/bl4s_satellites/PhysicsReconstructionSatellite.py -g bl4s > physics_recon.log 2>&1 &
nohup python3 src/bl4s_satellites/MachineLearningSatellite.py -g bl4s > ml_pid.log 2>&1 &
nohup python3 src/bl4s_satellites/SlowControlSatellite.py -g bl4s > slow_control.log 2>&1 &
nohup python3 src/bl4s_satellites/PrometheusExporter.py -g bl4s > prometheus.log 2>&1 &

# Live Event Explorer Web Backend & Kafka Otomatik Başlatma
if [ -f "docker-compose-kafka.yml" ]; then
    docker compose -f docker-compose-kafka.yml up -d 2>/dev/null || docker-compose -f docker-compose-kafka.yml up -d 2>/dev/null || true
fi
if [ -f "bl4s_event_explorer_server.py" ]; then
    nohup python3 bl4s_event_explorer_server.py > event_explorer.log 2>&1 &
    echo "  -> Live Event Explorer Backend http://localhost:5050 adresinde başlatıldı!"
fi

# Python ortamından çıkıyoruz
deactivate

echo "[4/5] CVMFS Ortamı Yükleniyor..."
source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-el9-gcc13-opt/setup.sh

echo "[5/5] MissionControl Başlatılıyor..."
export DISPLAY=localhost:10.0
/home/kayra/constellation/build/cxx/controllers/MissionControl/MissionControl
