# Constellation DAQ: Complete Operator Guide & Tutorial

Welcome to the comprehensive guide for operating the Constellation Data Acquisition (DAQ) framework using the simulated mock satellites provided in this repository. This guide mirrors the official Constellation Operator Guide, providing you with a deep dive into setting up, configuring, running, and analyzing a decentralized DAQ system.

---

## Table of Contents
1. [What is Constellation?](#1-what-is-constellation)
2. [Installation](#2-installation)
3. [The Mock Detector Suite](#3-the-mock-detector-suite)
4. [Configuration (TOML)](#4-configuration-toml)
5. [Step-by-Step Operating Tutorial](#5-step-by-step-operating-tutorial)
6. [Live Monitoring (Observatory & Telemetry)](#6-live-monitoring-observatory--telemetry)
7. [Offline Data Analysis (HDF5)](#7-offline-data-analysis-hdf5)

---

## 1. What is Constellation?

Constellation is a decentralized, network-based Data Acquisition (DAQ) framework primarily designed for High Energy Physics (HEP) test beam experiments. Unlike traditional DAQ systems that rely on a central event builder or master node, Constellation delegates autonomy to individual participants called **Satellites**.

### Core Architecture Concepts:
* **Satellites**: The fundamental building blocks of Constellation. A satellite can be a hardware interface (reading out a sensor), a software service (writing data to disk), or a mock simulation.
* **Groups**: Satellites are segmented into isolated network groups (e.g., `bl4s`). Only satellites within the same group can communicate with each other.
* **ZeroMQ (ØMQ)**: Constellation utilizes ZeroMQ for all underlying network communication, providing robust, broker-less messaging.
* **Finite State Machine (FSM)**: Every satellite adheres to a strict FSM. Understanding these states is critical for operation:
  * `NEW`: The satellite is running but has no configuration.
  * `INIT`: The satellite has received its `.toml` configuration and initialized its internal components.
  * `ORBIT`: The satellite is fully ready and waiting for the global start signal.
  * `RUN`: The satellite is actively acquiring data, generating triggers, and transmitting payloads.
  * `SAFE`: A safe fallback state.
  * `ERROR`: A state entered if a hardware or software fault occurs.

---

## 2. Installation

Constellation consists of core C++ applications (like MissionControl and Observatory) and Python bindings for custom satellite development.

### 2.1 Core Framework Installation

**Linux**
1. Install Flatpak as described in [flathub.org/setup](https://flathub.org/setup).
2. Install Constellation via: `flatpak install flathub de.desy.constellation`

**MacOS**
1. Update your MacOS installation via `sudo softwareupdate -i -a -R` (important).
2. Clone the repository: `git clone https://gitlab.desy.de/constellation/constellation`
3. Follow the build instructions on the [Constellation Documentation](https://constellation.pages.desy.de/application_development/intro/install_from_source.html#c-version) to compile using CMake.

**Windows**
1. Install WSL as described in the [Microsoft Docs](https://learn.microsoft.com/windows/wsl/install).
2. Set the WSL networking mode to **Mirrored** in the `.wslconfig` file.
3. Follow the Linux installation instructions inside the WSL terminal.

> **Network Note:** Ensure your firewall is not blocking ZeroMQ UDP discovery packets. If satellites cannot see each other, try temporarily disabling your local firewall.

### 2.2 Python Environment Setup
To run the mock detector satellites in this repository, you must set up the Python environment:

```bash
# Clone this repository
git clone https://github.com/KayraYavuz/Constellation-DAQ.git
cd Constellation-DAQ

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Constellation Python bindings and dependencies
pip install "ConstellationDAQ[cli]" h5py matplotlib numpy
```

---

## 3. The Mock Detector Suite

This repository provides a highly configurable suite of Python-based Mock Satellites. These satellites simulate realistic physics data acquisition without requiring physical hardware. 

> **Note:** These detectors are designed to be entirely generic. The specific beam conditions, incident particle energies, and target materials are left entirely to the operator to define via subsequent analysis. 

Available Mock Satellites:
* **TriggerModuleSatellite**: Acts as the master clock, generating synchronous trigger events for all other satellites.
* **MockQDC**: Simulates a multi-channel Charge-to-Digital Converter.
* **MockCalorimeter**: Simulates energy deposition in a grid-based calorimeter structure.
* **MockTimePix**: Simulates pixel-detector hit matrices for particle tracking.
* **MockDWC**: Simulates Delay Wire Chambers for beam profiling.
* **MockScintillator**: Simulates a basic scintillation counter for rate monitoring.

---

## 4. Configuration (TOML)

Before transitioning from `NEW` to `INIT`, the DAQ requires a configuration file written in TOML. This file assigns parameters to each satellite based on its class name.

Create a file named `daq_config.toml` in your working directory. Below is a comprehensive example:

```toml
# Trigger Module Configuration
[TriggerModuleSatellite._default]
trigger_rate = 100.0  # The global trigger rate in Hz

# QDC Configuration
[MockQDC._default]
channels = 32
rate = 100.0

# Calorimeter Configuration
[MockCalorimeter._default]
channels = 16
rate = 100.0

# Data Storage Configuration
[H5DataWriter._default]
output_dir = "./data_output"  # Directory where .h5 files will be saved
```
*The `_default` suffix applies the configuration to any satellite of that class. You can also target specific satellites by their given name.*

---

## 5. Step-by-Step Operating Tutorial

We will now orchestrate a full DAQ run using **MissionControl**, the central graphical interface for Constellation.

### Step 5.1: Start the Data Writer
First, ensure you have a directory for your data, and start the `H5DataWriter` satellite to listen for incoming network payloads.
```bash
mkdir -p ./data_output
SatelliteH5DataWriter -g bl4s
```

### Step 5.2: Launch the Mock Satellites
Open new terminal tabs, activate your `venv`, and start your detectors:
```bash
python3 bl4s_simulation/src/bl4s_satellites/TriggerModuleSatellite.py -g bl4s
python3 bl4s_simulation/src/bl4s_satellites/MockQDC.py -g bl4s
python3 bl4s_simulation/src/bl4s_satellites/MockCalorimeter.py -g bl4s
```
*Notice we pass `-g bl4s` to assign them all to the `bl4s` network group.*

### Step 5.3: Orchestrating with MissionControl
1. Open **MissionControl** from your system.
2. In the connection dialog, enter `bl4s` as the group name and connect.
3. You will see your satellites listed. Their status will be **NEW**.
4. **Load Config**: Click the "Load Config" button and select your `daq_config.toml` file.
5. **INIT**: Click the "Initialize" button. The satellites read their TOML parameters, allocate memory, and transition to **INIT**.
6. **ORBIT**: Click "Launch". Satellites prepare their network sockets for data transmission and enter **ORBIT**.
7. **RUN**: Click "Start". The Trigger Module begins emitting triggers. The QDC and Calorimeter generate simulated data, and the H5DataWriter records it to disk. You are now actively taking data!
8. **STOP**: After acquiring sufficient data, click "Stop". The H5 file is safely closed and flushed to disk.

---

## 6. Live Monitoring (Observatory & Telemetry)

Operating a DAQ blindly is dangerous. Constellation provides powerful introspection tools.

### 6.1 Logging via Observatory
Observatory aggregates logs from all distributed satellites.
1. Launch **Observatory** and connect to the `bl4s` group.
2. In the "Individual Subscriptions" tab, subscribe to the `INFO` and `WARNING` levels.
3. You will see a live feed of initialization messages, network state changes, and any potential warnings across your entire DAQ cluster.

### 6.2 Metrics via TelemetryConsole
1. Launch **TelemetryConsole** and connect to `bl4s`.
2. Select your `TriggerModule` or `MockQDC` as the Sender.
3. Select `SWTRIG` (Software Triggers) or `RATE` from the metrics dropdown.
4. Click **Create** to spawn a live, scrolling graph showing your real-time data throughput.

---

## 7. Offline Data Analysis (HDF5)

Constellation abandons legacy formats in favor of **HDF5**, a high-performance, parallel data format widely used in modern scientific computing.

Once your run is complete, an `.h5` file will reside in your `data_output` directory. 

### Extracting Data with Python
The `analysis_scripts/` directory contains Python scripts to unpack the binary blobs written by the Constellation C++ core.

To analyze your QDC data:
```bash
python3 analysis_scripts/analyze_h5_qdc.py path/to/your/data.h5
```

### Understanding the HDF5 Structure
Constellation writes data in structured blocks. Inside the HDF5 file, datasets are named according to the emitting satellite and the block index.

```python
import h5py
import struct

filename = "data_output/Constellation_bl4s_..._000000.h5"

with h5py.File(filename, "r") as f:
    def process_node(name, node):
        # Look for QDC data payloads
        if "mockqdc" in name.lower() and "block" in name.lower():
            raw_bytes = node[:].tobytes()
            
            # Unpack the raw bytes into unsigned 16-bit integers (channels)
            # The exact format string ("<32H") depends on your MockQDC channel count configuration
            unpacked_channels = struct.unpack("<32H", raw_bytes)
            
            print(f"Event Data: {unpacked_channels}")
            
    # Iterate through the entire HDF5 hierarchical tree
    f.visititems(process_node)
```

From here, the data is just standard NumPy arrays or Python lists, allowing you to easily generate histograms, heatmaps, and perform advanced particle identification (PID) logic.
