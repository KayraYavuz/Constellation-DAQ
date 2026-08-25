#!/bin/bash

# 1. Clean up old processes (to avoid conflicts)
echo "[0/5] Cleaning up old satellites and DAQ processes..."
pkill -9 -f "bl4s_satellites" 2>/dev/null || true
pkill -9 -f "SatelliteH5DataWriter" 2>/dev/null || true
pkill -9 -f "bl4s_event_explorer_server" 2>/dev/null || true

# 1.5. Ensure local data directory exists, clear python cache & sync to CERNBox
echo "[1/5] Ensuring storage directories, archiving old data and syncing to CERNBox..."
mkdir -p /home/kayra/bl4s_simulation/data
mkdir -p /home/kayra/bl4s_simulation/old_data
mkdir -p /eos/user/k/kyavuz/bl4s_data 2>/dev/null || true

# Copy any unsynced runs to CERNBox old_data/ subfolder (startup sync)
mkdir -p /eos/user/k/kyavuz/bl4s_data/old_data 2>/dev/null || true
xrdfs eosuser.cern.ch mkdir -p /eos/user/k/kyavuz/bl4s_data/old_data 2>/dev/null || true
for f in /home/kayra/bl4s_simulation/data/*.h5 /home/kayra/bl4s_simulation/old_data/*.h5; do
    [ -f "$f" ] || continue
    fname=$(basename "$f")
    xrdcp --silent "$f" "root://eosuser.cern.ch//eos/user/k/kyavuz/bl4s_data/old_data/$fname" 2>/dev/null || \
      cp -f "$f" "/eos/user/k/kyavuz/bl4s_data/old_data/$fname" 2>/dev/null || true
done

# Archive old data locally (move to old_data/ before new run)
mv /home/kayra/bl4s_simulation/data/*.h5 /home/kayra/bl4s_simulation/old_data/ 2>/dev/null || true
mv /home/kayra/bl4s_simulation/*.h5 /home/kayra/bl4s_simulation/old_data/ 2>/dev/null || true

# Persistent Run Counter: count all existing H5 files to get next run number
RUN_COUNTER_FILE="/home/kayra/bl4s_simulation/run_counter.txt"
if [ -f "$RUN_COUNTER_FILE" ]; then
    NEXT_RUN=$(cat "$RUN_COUNTER_FILE")
else
    # First time: count existing files across all directories
    EXISTING=$(ls /home/kayra/bl4s_simulation/old_data/*.h5 2>/dev/null | wc -l)
    NEXT_RUN=$((EXISTING + 1))
fi
echo "$((NEXT_RUN + 1))" > "$RUN_COUNTER_FILE"
echo "  -> Next Run Number: $NEXT_RUN (persisted in run_counter.txt)"

# H5DataWriter increments run_number by 1 internally on each START,
# so write NEXT_RUN-1 to TOML so the actual file becomes data_run_<NEXT_RUN>.h5
TOML_RUN=$((NEXT_RUN - 1))
sed -i "s/^run_number = .*/run_number = $TOML_RUN/" /home/kayra/bl4s_simulation/bl4s_config.toml 2>/dev/null || true
# Add run_number line if not already present
grep -q "^run_number" /home/kayra/bl4s_simulation/bl4s_config.toml 2>/dev/null || \
  sed -i "/^\[H5DataWriter/a run_number = $TOML_RUN" /home/kayra/bl4s_simulation/bl4s_config.toml

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
nohup python3 src/bl4s_satellites/caen_hv_satellite.py -g bl4s > caen_hv.log 2>&1 &
nohup python3 src/bl4s_satellites/PrometheusExporter.py -g bl4s > prometheus.log 2>&1 &

# Real-Time Automatic CERNBox Sync Daemon
if [ -f "auto_cernbox_sync.py" ]; then
    nohup python3 auto_cernbox_sync.py > cernbox_sync.log 2>&1 &
    echo "  -> CERNBox Real-Time Auto-Sync Daemon active!"
fi


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
