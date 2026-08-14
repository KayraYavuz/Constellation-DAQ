# BL4S Constellation DAQ: Comprehensive Setup and Operations Guide

Welcome to the Beamline for Schools (BL4S) Constellation tutorial. In this guide, we will implement a fully functional Data Acquisition (DAQ) system using the **Constellation** framework. 

This tutorial is designed to provide a comprehensive understanding of how to set up, configure, and operate a distributed DAQ system for test beam experiments. Instead of relying on specific beam energies or physical targets, this guide uses a generalized suite of **Mock Satellites** that simulate common high-energy physics detectors (like Cherenkov detectors, QDCs, Calorimeters, and pixel trackers).

---

## 1. Core Concepts of Constellation

Before diving into the installation, it is crucial to understand the terminology and architecture of Constellation:

- **Satellites**: In Constellation, every participant in the DAQ—whether it is a physical piece of hardware, a Python simulation script, or a data-writing service—is called a *satellite*. Satellites run as independent processes and communicate over the network.
- **Group**: Satellites are organized into groups (e.g., `bl4s`). Only satellites within the same group can communicate with each other.
- **ZeroMQ (ØMQ)**: The underlying messaging protocol. It allows for lightning-fast, decentralized communication without a central broker.
- **FSM (Finite State Machine)**: Every satellite follows a strict set of states to ensure the DAQ operates safely:
  - `NEW`: The satellite has just started and has no configuration.
  - `INIT`: The satellite has received its configuration (via TOML) and initialized its hardware/software.
  - `ORBIT`: The satellite is fully ready to take data.
  - `RUN`: The satellite is actively acquiring data and transmitting payloads.

---

## 2. Installation

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

> **Firewall Warning:** It might be needed to disable your firewall temporarily in case Constellation does not detect any satellites in your local network.

---

## 3. Preparing the BL4S Mock Workspace

In a real experiment, satellites connect to physical NIM crates, VME modules, or USB boards. For this tutorial, we use **Python Mock Satellites** that generate realistic physics data.

### Environment Setup
1. Clone this repository to your local machine.
2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the Constellation Python bindings:
   ```bash
   pip install "ConstellationDAQ[cli]"
   ```

### Understanding the Mock Detectors
Our simulation includes the following detector satellites, which independently generate correlated physics events using synchronized random seeds:
- **MockQDC**: Simulates a 32-channel Charge-to-Digital Converter. Useful for simulating Scintillators (MIP Signals) and Cherenkov threshold detectors.
- **MockCalorimeter**: Simulates electromagnetic and hadronic showers.
- **MockTimePix**: Generates 2D hit maps representing particle tracks.
- **MockScintillator**: Acts as a cumulative scaler (e.g., simulating neutron detectors or trigger counters).

---

## 4. Configuration (TOML)

Before any satellite can transition from `NEW` to `INIT`, it requires a configuration. Constellation uses `.toml` files for this purpose.

Create a file called `bl4s_config.toml` in your working directory. This file dictates how many channels each detector has and how fast it should operate:

```toml
[MockQDC._default]
channels = 32
rate = 100.0 # Operates at 100 Hz

[MockCalorimeter._default]
channels = 16
rate = 100.0

[MockTimePix._default]
matrix_size = 256
rate = 100.0

[H5DataWriter._default]
# This satellite listens to the data streams and records them to disk
output_dir = "~/bl4s_data"
```

---

## 5. Controlling the DAQ (MissionControl)

MissionControl is the central graphical interface used to orchestrate all satellites.

### Step 5.1: Starting the Satellite Processes
Open multiple terminal windows, activate your `venv`, and start your satellites under the `bl4s` group:
```bash
python3 bl4s_simulation/src/bl4s_satellites/MockQDC.py -g bl4s
python3 bl4s_simulation/src/bl4s_satellites/MockCalorimeter.py -g bl4s
SatelliteH5DataWriter -g bl4s
```

### Step 5.2: Orchestrating via MissionControl
1. Start **MissionControl** from your application menu or terminal.
2. Enter the group name `bl4s` to connect.
3. In the main window, all your active satellites (`MockQDC`, `MockCalorimeter`, `H5DataWriter`) will appear. They will initially be in the `NEW` state.
4. Click **Load Config** and select your `bl4s_config.toml` file.
5. Click **Initialize**. The FSM will transition the satellites to the `INIT` state. The hardware/software is now configured.
6. Click **Launch**. The satellites transition to `ORBIT`, standing by for the run.
7. Click **Start**. The satellites enter the `RUN` state and begin acquiring and transmitting data.
8. Wait for your desired duration, then click **Stop** to safely halt data acquisition and flush the files to disk.

---

## 6. Observation and Telemetry

Constellation provides dedicated tools for real-time monitoring while the system is in the `RUN` state.

### Observatory (Logging)
Observatory is the graphical logging interface. It aggregates logs from all distributed satellites into a single view.
1. Start **Observatory**.
2. Connect to the `bl4s` group.
3. Under *Individual Subscriptions*, select the `INFO` or `DEBUG` log level for your satellites.
4. You will see real-time log messages indicating exactly what each satellite is doing (e.g., "MockQDC initialized with 32 channels").

### TelemetryConsole (Metrics)
TelemetryConsole allows you to monitor live metrics, such as trigger rates, temperatures, or CPU usage.
1. Start **TelemetryConsole**.
2. Connect to the `bl4s` group.
3. Select your Trigger satellite (if active) as the sender.
4. Select the `SWTRIG` metric (Software Trigger rate).
5. Click **Create** to plot a live, real-time graph of how many events per second your DAQ is processing.

---

## 7. Offline Data Analysis (HDF5)

Unlike older DAQ systems that write `.root` files natively, Constellation writes data in the modern, highly parallelizable **HDF5 (`.h5`)** format.

When you clicked **Stop** in MissionControl, the `H5DataWriter` saved a file (e.g., `data_run_1.h5`) in your specified `output_dir` (e.g., `~/bl4s_data/`).

### Analyzing the Data with Python
To extract the physical payloads from the HDF5 file, you can use Python with `h5py` and `matplotlib`. The `analysis_scripts/` folder in this repository contains ready-to-use scripts for unpacking the binary data.

For example, to analyze the QDC data:
```bash
python3 analysis_scripts/analyze_h5_qdc.py
```

**How it works under the hood:**
```python
import h5py
import struct

with h5py.File("data_run_1.h5", "r") as f:
    def process_node(name, node):
        # Locate the specific dataset block inside the HDF5 tree
        if "mockqdc" in name.lower() and "block" in name.lower():
            raw_bytes = node[:].tobytes()
            
            # The QDC payload is packed as 32 unsigned short integers (2 bytes each).
            # We use struct.unpack to convert the raw C++ bytes back into Python integers.
            channels = struct.unpack("<32H", raw_bytes)
            
            # Access Channel 0 (e.g., Scintillator 2)
            scintillator_value = channels[0]
            
    f.visititems(process_node)
```

By adapting these Python scripts (or migrating them into Jupyter Notebooks), you can perform advanced Particle Identification (PID), generate hit maps, and evaluate detector performance with ease.
