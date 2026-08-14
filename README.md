# BL4S Constellation DAQ Tutorial

Welcome to the Beamline for Schools (BL4S) Constellation tutorial. In this guide, we will implement a fully functional Data Acquisition (DAQ) system using **Constellation**, simulating a 5 GeV particle beam hitting a 60 cm Tungsten target. 

We will cover the installation, adding mock physical detectors (QDC, Calorimeter, TimePix), controlling the DAQ via MissionControl, and extracting meaningful physics data (Kaons, Pions, Electrons) using Python and HDF5.

---

## 1. Installation

Constellation is highly portable and supports multiple operating systems.

### Linux
- Install Flatpak as described in [flathub.org/setup](https://flathub.org/setup)
- Install Constellation via: `flatpak install flathub de.desy.constellation`
- Ensure that Python 3.11 or newer is available.

### MacOS
- Update your MacOS installation via `sudo softwareupdate -i -a -R` (important).
- Clone the repository: `git clone https://gitlab.desy.de/constellation/constellation`
- Follow the build instructions on the [Constellation Documentation](https://constellation.pages.desy.de/application_development/intro/install_from_source.html#c-version).

### Windows
- Install WSL as described in the [Microsoft Docs](https://learn.microsoft.com/windows/wsl/install).
- Set the WSL networking mode to **Mirrored** in the WSL Settings.
- Install Constellation inside WSL following the Linux instructions.

> [!WARNING]
> **Firewall:** It might be needed to disable your firewall temporarily in case Constellation does not detect any satellites in your local network.

---

## 2. Preparing the BL4S Workspace

Instead of real hardware, we will use **Mock Satellites** that generate realistic physics data. These Python-based satellites pretend to be hardware modules (like the V792 QDC or a TimePix tracker).

1. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install the Constellation Python bindings:
   ```bash
   pip install "ConstellationDAQ[cli]"
   ```

### Understanding the Mock Detectors
Our simulation includes the following detectors, all tied to the same random seed per event to guarantee synchronized physics interactions:
- **MockQDC**: Simulates a 32-channel Charge-to-Digital Converter.
  - *Ch0 & Ch1*: Scintillators S2 & S3 (MIP Signals)
  - *Ch2*: Calorimeter (Electromagnetic shower for $e^-$, MIP for hadrons)
  - *Ch3 & Ch4*: Cherenkov C0 & C1 for Particle Identification (PID).
- **MockTimePix**: Generates 2D hit maps of the particle tracks.
- **MockScintillator (WENDI)**: A cumulative scaler that detects secondary neutrons.

---

## 3. Configuration (TOML)

Before the satellites can be initialized, a configuration file is needed. Create a file called `bl4s_config.toml` in your working directory.

```toml
[MockQDC._default]
channels = 32
rate = 100.0

[MockCalorimeter._default]
channels = 16
rate = 100.0

[MockTimePix._default]
matrix_size = 256
rate = 100.0

[H5DataWriter._default]
# This satellite records all the data to the disk
output_dir = "~/bl4s_data"
```

---

## 4. Controlling the DAQ (MissionControl)

In Constellation, each participant in the data acquisition is called a **satellite**. Each satellite has a Finite State Machine (FSM): `NEW -> INIT -> ORBIT -> RUN`.

### Starting the Satellites
Open multiple terminal windows, activate your `venv`, and start your satellites under the `bl4s` group:
```bash
python3 src/bl4s_satellites/MockQDC.py -g bl4s
python3 src/bl4s_satellites/MockCalorimeter.py -g bl4s
SatelliteH5DataWriter -g bl4s
```

### Using MissionControl
1. Start **MissionControl** from your application menu or terminal.
2. Enter the group name `bl4s` to connect.
3. In the main window, all your satellites (QDC, Calorimeter, H5DataWriter) will appear in the list.
4. Click **Load Config** and select your `bl4s_config.toml` file.
5. Click **Initialize** to send configurations to the satellites (State: `INIT`).
6. Click **Launch** to prepare them for data taking (State: `ORBIT`).
7. Click **Start** to begin taking data (State: `RUN`).
   - The system is now simulating a 5 GeV beam!
8. Wait for ~10 seconds, then click **Stop**.

---

## 5. Observation and Telemetry

While the experiment is running in the `RUN` state, you can monitor the health and logs of your DAQ.

### Observatory
Start **Observatory**, the graphical logging interface. Under *Individual Subscriptions*, you can select the `DEBUG` or `INFO` log level for the `MockQDC` satellite. Every time a transition happens, you will see exactly what the satellite is doing.

### TelemetryConsole
If you want to view the Trigger Rate or Hardware Status:
1. Start **TelemetryConsole**.
2. Select your `TriggerModuleSatellite` as the sender.
3. Select the `SWTRIG` metric (Software Trigger rate).
4. Click **Create** to plot a live, real-time graph of how many particles per second your DAQ is processing.

---

## 6. Offline Data Analysis (HDF5)

Unlike the old TDAQ which wrote `.root` files, Constellation uses the modern, lightning-fast **HDF5 (`.h5`)** format.

When you clicked **Stop** in MissionControl, the `H5DataWriter` saved a file like `data_run_1.h5` in your `~/bl4s_data/` folder.

To extract the physical PID (Particle Identification) data—for example, separating Kaons from Pions—you can use Python and `h5py`. 

Create an analysis script `analyze_data.py`:
```python
import h5py
import struct
import matplotlib.pyplot as plt

# Open the Constellation data file
with h5py.File("data_run_1.h5", "r") as f:
    calorimeter_qdc = []
    cherenkov_qdc = []
    
    # Traverse the HDF5 tree looking for MockQDC blocks
    def process_node(name, node):
        if "mockqdc" in name.lower() and "block" in name.lower():
            raw_bytes = node[:].tobytes()
            # Unpack 32 unsigned short integers (2 bytes each)
            channels = struct.unpack("<32H", raw_bytes)
            
            calorimeter_qdc.append(channels[2])
            cherenkov_qdc.append(channels[3])
            
    f.visititems(process_node)

# Plot the physics data
plt.hist2d(calorimeter_qdc, cherenkov_qdc, bins=50, cmap='viridis')
plt.xlabel("Calorimeter QDC (Energy)")
plt.ylabel("Cherenkov C0 QDC")
plt.title("Particle Identification (e- vs Hadrons)")
plt.show()
```

Run this script to visualize how the simulated $e^-$ shower creates a massive peak at ~800 QDC, while Pions and Kaons cluster at the ~150 MIP peak.

**Congratulations! You have successfully deployed, monitored, and analyzed a Constellation DAQ system for BL4S.**
