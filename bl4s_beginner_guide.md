# 🚀 BL4S DAQ & Live Monitoring System: Comprehensive Beginner's Guide

This guide is designed from scratch for someone who has never used **Constellation**, **Kafka**, **Grafana**, or **Particle Physics Simulation (Geant4)** in their life.

The system might look complex, but when broken down into pieces, you'll see that it's a very logical data pipeline.

---

## 🧩 Part 1: "The Big Picture" (What Have We Built?)

When conducting an experiment in a particle accelerator (e.g., at CERN), thousands of data points arrive from detectors every second. The system that **collects**, **transports**, and **visualizes** this data is called **DAQ (Data Acquisition)**.

Our system consists of 3 main parts:

1. **Simulation (On the CERN Server):** We don't have the real physical detectors running right now. Therefore, we use the **Geant4** physics engine to generate *fake but physically accurate* data (ADC/TDC signals) as if electrons and pions were passing through them. A framework called **Constellation** manages this job.
2. **Data Transporters (Infrastructure):** Since the generated data flows very fast, we need to transport it without losing it. We have two couriers for this:
   * **Kafka:** Transports event-based raw physics data (e.g., "3000 MeV energy hit the Calorimeter!").
   * **Prometheus:** Transports slowly changing "health" data (e.g., "Detector temperature is 24°C, Voltage is 1500V").
3. **Visualization (Control Room - On Your Computer):** We turn the data brought by the couriers into graphs on the screen:
   * **Live Event Explorer (Web Interface):** Converts the raw physics data coming from Kafka into live histograms and heatmaps.
   * **Grafana:** Displays health data coming from Prometheus with panels like speedometers and thermometers.

---

## 🛠️ Part 2: Installation and Prerequisites (First Time Only)

To spin up the system on your computer (Mac/Linux), we need a few tools.

### 1. Install and Run Docker
Docker allows you to run programs (Kafka, Grafana, etc.) in isolated boxes called "containers" without installing them directly on your system. Open Docker Desktop and make sure it is running in the background.

### 2. Prepare the Python Environment
We need to set up a virtual environment to download the necessary libraries. Open your terminal:
```bash
cd ~/Desktop/DATA
./setup_venv.sh
```

---

## 🚀 Part 3: Step-by-Step Operating Guide

You will follow these steps in order every time you want to use the system.

### Step 1: Start Background Services (Docker)
Open a terminal and start Kafka, Prometheus, and Grafana:
```bash
cd ~/Desktop/DATA
# Start Kafka
docker-compose -f docker-compose-kafka.yml up -d

# Start Prometheus and Grafana (If not already started)
docker run -d -p 9090:9090 -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
docker run -d -p 3000:3000 grafana/grafana
```

### Step 2: Establish a Data Tunnel (Bridge) with the CERN Server
We need to set up an invisible bridge so that the server at CERN can send data to your Mac. Open a new terminal tab and enter the following commands (leave this tab open in the background):
```bash
# Reverse tunnel for Kafka (CERN -> Mac)
ssh -N -R 9092:localhost:9092 kayra@128.141.131.221

# Forward tunnel for Prometheus (Mac -> CERN)
ssh -N -L 9100:localhost:9100 kayra@128.141.131.221
```

### Step 3: Start the Simulation on the CERN Server
Now we can connect to CERN and start generating fake data. Open a new terminal and connect to CERN:
```bash
ssh kayra@128.141.131.221
cd /home/kayra/bl4s_simulation
./start_all.sh
```
> **Note:** The `start_all.sh` script wakes up all Constellation satellites (Calorimeter, Timepix, Trigger, etc.). However, they are all currently in the **NEW** state and waiting.

### Step 4: Orchestration with MissionControl
To give the "Get Ready and Start" command to all satellites, open the **MissionControl** application on the CERN server (or via your X11-supported connection):
1. Select the group as `bl4s` and connect. You will see the satellites on the screen.
2. Click the **Load Config** button and select the settings file (`bl4s_config.toml`).
3. Click the **Initialize** button. (Satellites read their settings and turn green - `INIT`).
4. Click the **Launch** button. (Satellites connect to the network and turn light blue - `ORBIT`).
5. Click the **Start** button. (Dark blue - `RUN`). 
🎉 **Congratulations! Right now, hundreds of particle collisions are being simulated every second, and the data is flowing to your Mac!**

### Step 5: Automated & Timed Runs via ConstellationCommander (CLI)
If you want to run a timed data taking session automatically (e.g. leaving the DAQ running for 1 hour overnight without needing a GUI screen):

After `./start_all.sh` is started, run in your terminal:
```bash
# 1. Initialize satellites with configuration
ConstellationCommander -g bl4s initialize bl4s_config.toml

# 2. Launch satellites into ORBIT state
ConstellationCommander -g bl4s launch

# 3. Start a timed acquisition run (e.g., 3600 seconds = 1 hour)
ConstellationCommander -g bl4s start --duration 3600
```
When the timer expires, `ConstellationCommander` automatically sends the `STOP` signal, flushes the data buffer to disk, and securely seals the `.h5` file ready for archiving.

---

## 📊 Part 4: Live Data Monitoring (The Fun Part!)

While the simulation is running, let's head over to the control room (your browser).

### 1. Grafana (System Health and Telemetry)
Go to **[http://localhost:3000](http://localhost:3000)** in your browser. (Login: admin/admin).
* Click on *Dashboards* from the left menu and import the `bl4s_grafana_dashboard.json` file.
* **What Will You See?** You will watch live on car-dashboard-like screens the temperatures of the detectors, high voltage (HV) values, and how many events they generate per second (Event/s).

### 2. Live Event Explorer (Physics Data Interface)
Run the following command in your Mac terminal:
```bash
cd ~/Desktop/DATA
source kafka_env/bin/activate
python bl4s_event_explorer_server.py
```
Then go to **[http://localhost:5050](http://localhost:5050)** in your browser.
* **What Will You See?** On the left side, there is a folder tree of detectors.
  * 🎯 **Click Timepix > Hit Map**: A 256x256 pixel heatmap showing exactly how particles hit the beam spot center will appear on your screen.
  * 🔥 **Click Calorimeter > Energy Histogram**: You will see the massive energies (electromagnetic shower) accumulated in the lead glass blocks.
  * 🌈 **Click Cherenkov > QDC Spectrum**: You will see with your own eyes two distinct peaks (PID) where light electrons and heavy pions separate!

---

## 💾 Part 5: The Experiment is Over, Now What? (Data Analysis)

When you click the **Stop** button from MissionControl, the data flow stops. 
Constellation has compressed and saved all those millions of events into a single **`.h5` (HDF5)** file. 

Now, like a real physicist, you can open this file and perform scientific analysis after the simulation is over:
```bash
# Running an example analysis script:
python analyze_h5_calorimeter.py /path/to/data/folder/data_file.h5
```
These scripts will give you static, high-resolution graphs (Matplotlib) just like the ones used in scientific papers.

---

## ➕ Bonus: How to Add a New Satellite to the System?

Adding a new satellite is quite simple! If you look at the content of the `start_all.sh` file, **Step 2 (Simülasyon Uyduları Başlatılıyor)** is dedicated entirely to this.

Let's say users want to add a new detector to the system, for example, a **"MuonChamberSatellite"**. Here are the steps they should follow:

### 1. Prepare the Satellite Python File
First, they must place the Python file of the new satellite (`MuonChamberSatellite.py`) inside the `src/bl4s_satellites/` folder on the CERN server.

### 2. Edit the `start_all.sh` File
Using a text editor on the server (e.g., typing `nano start_all.sh`), they open the file and add a **single line** to the satellite list after line 20.

The existing file looks like this:
```bash
echo "[2/4] Simülasyon Uyduları Başlatılıyor..."
nohup /home/kayra/bl4s_simulation/venv/bin/SatelliteH5DataWriter -g bl4s > datawriter.log 2>&1 &
nohup python3 src/bl4s_satellites/TriggerModuleSatellite.py -g bl4s > trigger.log 2>&1 &
# ... other satellites ...
nohup python3 src/bl4s_satellites/CalorimeterSatellite.py -g bl4s > calorimeter.log 2>&1 &
```

**Right below this, they add their own satellite:**
```bash
nohup python3 src/bl4s_satellites/MuonChamberSatellite.py -g bl4s > muonchamber.log 2>&1 &
```

* **`nohup` and `&`**: These commands ensure the satellite runs continuously in the background (even if the terminal is closed).
* **`-g bl4s`**: Ensures the satellite joins the `bl4s` network (group).
* **`> muonchamber.log 2>&1`**: If a Python error (crash) occurs in the satellite, it writes it directly to the `muonchamber.log` file instead of printing it to the screen. This makes debugging very easy.

### 3. Add to the Configuration (TOML) File
Finally, for MissionControl to apply settings to the satellite, they need to add their new satellite to the `bl4s_config.toml` file like this:

```toml
[MuonChamberSatellite._default]
channels = 32
rate = 100.0
```

That's it! The next time they run the `./start_all.sh` command, their new satellite will automatically join the network and appear on the MissionControl screen.

---

## 🔌 Part 6: Transitioning from Simulation to Real Experiment (Connecting C++ Detectors)

When deploying at the CERN T9 beamline, mock/simulation satellites are replaced with actual hardware readout drivers (VME, CAEN, Timepix C++ libraries).

There are **two straightforward approaches** to interface your C++ drivers:

### Method 1: Native C++ Constellation Satellite (Recommended)
Constellation core is natively written in modern C++. You can link vendor libraries (`libCAENVME.so`) directly inside a C++ satellite for zero-copy latency:
```cpp
#include "constellation/core/satellite/Satellite.hpp"
#include "caen_vme_driver.h"

class CalorimeterSatellite : public constellation::satellite::Satellite {
    void running(const std::stop_token& stop_token) override {
        while (!stop_token.stop_requested()) {
            std::vector<uint32_t> data = read_vme_fifo();
            auto record = create_data_record();
            record.add_block(data.data(), data.size() * sizeof(uint32_t));
            send_data_record(std::move(record));
        }
    }
};
```

### Method 2: Python Satellite with C++ Wrapper (`ctypes`)
Without modifying existing Python satellites, compile your C++ driver into a `.so` shared library and invoke it directly from Python:
```python
import ctypes
c_lib = ctypes.CDLL("./libcaen_reader.so")

class CalorimeterSatellite(Geant4ReplaySatellite):
    def generate_physics_event(self) -> bytes:
        buf = (ctypes.c_uint16 * 16)()
        c_lib.read_vme_calorimeter(buf) # Direct hardware readout
        return bytes(buf)
```

> 🎯 **Key Advantage:** Because the architecture is completely decoupled and modular, not a single line of code needs to change in Kafka, Protobuf, the Web Event Explorer UI (`localhost:5050`), or Grafana!

---

## ⚡ Part 7: High Voltage (HV) Control: CAEN SY5527 and Web GECO

The detector chain (16-channel Calorimeter crystals, Cherenkov, Scintillators) requires stable high voltage (**-1500V to +2500V**) provided by the **CAEN SY5527 High Voltage Mainframe** located in the control room.

Instead of requiring physicists to install standalone desktop software (GECO 2020), our system integrates slow control directly into the web platform:

```
[ CAEN SY5527 High Voltage Mainframe (Hardware) ]
                     │ (Direct Local Ethernet Network)
                     ▼
[ SlowControlSatellite.py (CERN Server) ]
  - Communicates via official CAENHVWrapper Library
  - Handles SetVoltage(ch, 1500), GetStatus() commands
  - Enforces Ramp-Up / Ramp-Down (50 V/s) and Overcurrent TRIP safety
                     │ (WebSocket + Prometheus)
                     ▼
[ Unified Control Room ]
  👉 http://localhost:5050 (Web-Based GECO Panel)
  👉 http://localhost:3000 (Grafana Slow Control Dashboard)
```

### How It Works:
1. **Direct Hardware Connection:** The `CAEN SY5527` mainframe is connected to the local control room Ethernet network.
2. **Library Interface:** `SlowControlSatellite` communicates via the official `CAENHVWrapper` (C/Python) library.
3. **Zero Software Installation:** Shifters and collaborators can toggle channels (`ON/OFF`), set target voltages, and monitor real-time current/voltage curves directly from any browser at `localhost:5050`.

---
*You did it! You now know how a professional DAQ system is set up, orchestrated, and monitored live!* 🚀



