#!/bin/bash

# 1. Clean up old processes (to avoid conflicts)
echo "[0/5] Cleaning up old satellites and DAQ processes..."
pkill -9 -f "bl4s_satellites" 2>/dev/null || true
pkill -9 -f "SatelliteH5DataWriter" 2>/dev/null || true
pkill -9 -f "bl4s_event_explorer_server" 2>/dev/null || true

# 1.5. Ensure CERNBox EOS directory exists & clear python cache
echo "[1/5] Ensuring CERNBox EOS storage directory and clearing cache..."
mkdir -p /eos/user/k/kayra/bl4s_data 2>/dev/null || true
mkdir -p /home/kayra/bl4s_simulation/old_data
mv /home/kayra/bl4s_simulation/*.h5 /home/kayra/bl4s_simulation/old_data/ 2>/dev/null || true
find /home/kayra/bl4s_simulation -name "*.pyc" -delete 2>/dev/null || true
find /home/kayra/bl4s_simulation -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 2. Reset environment variables (to clean CVMFS pollution)
unset PYTHONPATH
unset LD_LIBRARY_PATH

echo "[2/5] Switching to Python Virtual Environment..."
cd /home/kayra/bl4s_simulation
source venv/bin/activate

echo "[3/5] Starting all Detector, Reconstruction and ML Satellites..."
# Basic Detector Satellites & Data Writer
nohup /home/kayra/bl4s_simulation/venv/bin/SatelliteH5DataWriter -g bl4s > datawriter.log 2>&1 &
nohup python3 src/bl4s_satellites/TriggerModuleSatellite.py -g bl4s > trigger.log 2>&1 &
nohup python3 src/bl4s_satellites/ScintillatorSatellite.py -g bl4s > scintillator.log 2>&1 &
nohup python3 src/bl4s_satellites/DWCSatellite.py -g bl4s > dwc.log 2>&1 &
nohup python3 src/bl4s_satellites/TimepixSatellite.py -g bl4s > timepix.log 2>&1 &
nohup python3 src/bl4s_satellites/CherenkovSatellite.py -g bl4s > cherenkov.log 2>&1 &
nohup python3 src/bl4s_satellites/CalorimeterSatellite.py -g bl4s > calorimeter.log 2>&1 &

# Advanced Event Builder, Physics Reconstruction, ML & Telemetry Satellites
nohup python3 src/bl4s_satellites/CoincidenceEventBuilder.py -g bl4s > coincidence.log 2>&1 &
nohup python3 src/bl4s_satellites/PhysicsReconstructionSatellite.py -g bl4s > physics_recon.log 2>&1 &
nohup python3 src/bl4s_satellites/MachineLearningSatellite.py -g bl4s > ml_pid.log 2>&1 &
nohup python3 src/bl4s_satellites/SlowControlSatellite.py -g bl4s > slow_control.log 2>&1 &
nohup python3 src/bl4s_satellites/PrometheusExporter.py -g bl4s > prometheus.log 2>&1 &

# Live Event Explorer Web Backend & Kafka Auto-Start
if [ -f "docker-compose-kafka.yml" ]; then
    docker compose -f docker-compose-kafka.yml up -d 2>/dev/null || docker-compose -f docker-compose-kafka.yml up -d 2>/dev/null || true
fi
if [ -f "bl4s_event_explorer_server.py" ]; then
    nohup python3 bl4s_event_explorer_server.py > event_explorer.log 2>&1 &
    echo "  -> Live Event Explorer Backend started at http://localhost:5050 !"
fi

# Exit Python environment
deactivate

echo "[4/5] Loading CVMFS Environment..."
source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-el9-gcc13-opt/setup.sh

echo "[5/5] Starting MissionControl..."
export DISPLAY=localhost:10.0
/home/kayra/constellation/build/cxx/controllers/MissionControl/MissionControl
