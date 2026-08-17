# Constellation DAQ: Complete Operator Guide & Real-Time Observability Suite

Welcome to the comprehensive guide for operating the Constellation Data Acquisition (DAQ) framework and the **Extended Real-Time Observability & Monitoring Suite** developed for the Beamline for Schools (BL4S) experiment.

This repository provides:
1. **Core Constellation DAQ & Mock Detector Suite**: Complete framework setup, FSM orchestration, and Geant4/Allpix² physics replays.
2. **Prometheus & Grafana Telemetry**: Slow-control telemetry dashboard for real-time detector health, high voltage, temperatures, and throughput.
3. **Kafka Real-Time Streaming Pipeline (Google Protocol Buffers)**: Zero-latency, highly compressed binary event streaming (`.proto`) directly from detector frontends.
4. **BL4S Live Event Explorer (Observability UI)**: Web-based control room interface featuring a hierarchical tree explorer and high-performance **Apache ECharts** histograms, 2D heatmaps, and PID spectra (similar to ATLAS/CMS TDAQ OHP).

---

### 🟢 New to the Project?
If you have never used Constellation, Kafka, Grafana, or Particle Physics simulations before, please start with our **[Beginner's Step-by-Step Guide](bl4s_beginner_guide.md)**!

---

## Table of Contents
1. [What is Constellation?](#1-what-is-constellation)
2. [Observability vs. Telemetry: Architecture Comparison](#2-observability-vs-telemetry-architecture-comparison)
3. [Technology Stack & System Architecture](#3-technology-stack--system-architecture)
4. [Installation & Prerequisites](#4-installation--prerequisites)
5. [The Detector Suite (Hardware & Simulation)](#5-the-detector-suite-hardware--simulation)
6. [Configuration (TOML)](#6-configuration-toml)
7. [Step-by-Step Operating Tutorial](#7-step-by-step-operating-tutorial)
8. [Real-Time Monitoring & Observability Stack](#8-real-time-monitoring--observability-stack)
   - [8.1 BL4S Live Event Explorer (Web UI)](#81-bl4s-live-event-explorer-web-ui)
   - [8.2 Grafana Control Room Dashboard](#82-grafana-control-room-dashboard)
   - [8.3 Live Kafka Calorimeter Viewer](#83-live-kafka-calorimeter-viewer)
9. [Offline Data Analysis (HDF5)](#9-offline-data-analysis-hdf5)

---

## 1. What is Constellation?

Constellation is a decentralized, network-based Data Acquisition (DAQ) framework primarily designed for High Energy Physics (HEP) test beam experiments at DESY and CERN. Unlike traditional DAQ systems that rely on a central event builder or master node, Constellation delegates autonomy to individual participants called **Satellites**.

### Core Architecture Concepts:
* **Satellites**: Independent processes interfacing with hardware (readout electronics) or software services (event writer).
* **Groups**: Logical network segmentation (e.g., `bl4s`). Only satellites in the same group discover and communicate with each other.
* **ZeroMQ (ØMQ)**: Underlying asynchronous messaging protocol using CDTP (Constellation Data Transport Protocol), CSCP (Control Protocol), and CMDP (Monitoring Protocol).
* **Finite State Machine (FSM)**:
  * `NEW`: Satellite process running, waiting for configuration.
  * `INIT`: Loaded TOML configuration and allocated hardware buffers.
  * `ORBIT`: Connected to network, discovered peers, ready to start.
  * `RUN`: Actively taking data, generating triggers, and pushing events.
  * `SAFE`: Safe fallback state upon error or interrupt.

---

## 2. Observability vs. Telemetry: Architecture Comparison

Constellation comes out of the box with standard tools (**MissionControl**, **Observatory**, and **TelemetryConsole**). However, for real-time physics inspection and online quality control (DQM), a full observability stack was built on top of it.

| Feature / Dimension | Built-in Constellation (Observatory & TelemetryConsole) | **Our Extended Real-Time DAQ Observability Stack** |
| :--- | :--- | :--- |
| **Data Scope** | Single scalar numbers (`stat("temp", 24.5)`) | **Full physics event payloads** (16-channel ADC array, 256×256 hit matrices, TDC timings, QDC spectra) |
| **Visual Capabilities** | ❌ Text/Number tables only | ✅ **Interactive 1D Histograms, 2D Heatmaps (4×4 & 256×256), Scatter Plots, and Real-Time Gauges** |
| **Explorability** | Static flat list of registered metrics | ✅ **Interactive Tree Hierarchy (`Satellite ➔ Channel ➔ Visualizer`)** |
| **Physics Diagnostics** | ❌ None (only "is process alive?") | ✅ **Online Particle ID (e/π separation in Cherenkov), EM shower profiling (Calorimeter), beam spot centering (Timepix)** |
| **Transport Layer** | ZeroMQ CMDP (local network only) | **Apache Kafka + WebSockets + Prometheus** |
| **Access & Portability** | Requires X11 Forwarding from CERN server | ✅ **Modern Web Browser UI (Accessible on Mac/PC/Tablet at `localhost:5050` and `localhost:3000`)** |
| **Equivalent in LHC** | Basic hardware status monitors | **ATLAS / CMS Online Histogram Presenter (OHP) & DQM Display** |

---

## 3. Technology Stack & System Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   CERN Server (pc-bl4s-07 / Linux)                       │
│                                                                          │
│  ┌──────────────────────┐   Constellation CDTP (ZMQ)   ┌──────────────┐  │
│  │ Geant4ReplaySatellite│ ───────────────────────────▶ │H5DataWriter  │  │
│  │ ├─ Calorimeter       │                              │  └─ .h5 (EOS)│  │
│  │ ├─ Scintillator      │                              └──────────────┘  │
│  │ ├─ Timepix (256x256) │                                                │
│  │ ├─ Cherenkov (PID)   │   Prometheus Exporter (HTTP) ┌──────────────┐  │
│  │ └─ TriggerModule     │ ───────────────────────────▶ │ Port :9100   │  │
│  └──────────┬───────────┘                              └──────┬───────┘  │
└─────────────┼─────────────────────────────────────────────────┼──────────┘
              │                                                 │
              │ Reverse SSH Tunnel (Port 9092)                  │ Forward Tunnel (:9090)
              ▼                                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     Local Machine (macOS / Linux)                        │
│                                                                          │
│  ┌─────────────────────────┐          ┌───────────────────────────────┐  │
│  │ Apache Kafka (Docker)   │          │ Prometheus & Grafana (Docker) │  │
│  │ Topic: bl4s_events      │          │ http://localhost:3000         │  │
│  └──────────┬──────────────┘          └───────────────────────────────┘  │
│             │                                                            │
│             ▼                                                            │
│  ┌─────────────────────────┐                                             │
│  │ Flask-SocketIO Server   │                                             │
│  │ (Python Backend)        │                                             │
│  └──────────┬──────────────┘                                             │
│             │ WebSocket Push                                             │
│             ▼                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │ BL4S Live Event Explorer (HTML5 / Apache ECharts / Dark UI)           │  │
│  │ http://localhost:5050                                              │  │
│  │ ├── 📂 Calorimeter: 16-ch Energy Histogram & 4x4 Heatmap           │  │
│  │ ├── 📂 Scintillator: Timing & Photoelectron Distribution           │  │
│  │ ├── 📂 Timepix: 256x256 Hit Map & ToT Spectrum                     │  │
│  │ ├── 📂 Cherenkov: QDC Spectrum (Electron / Pion separation)        │  │
│  │ └── 📂 Trigger: Live Rate Time Series                              │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Installation & Prerequisites

### 4.1 Local Machine Setup (Mac / Linux)

1. **Docker Containers (Kafka & Monitoring):**
   ```bash
   # Start Kafka & Zookeeper
   docker-compose -f docker-compose-kafka.yml up -d
   
   # Start Prometheus & Grafana (if not already running)
   docker run -d -p 9090:9090 -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
   docker run -d -p 3000:3000 grafana/grafana
   ```

2. **Python Virtual Environment:**
   ```bash
   ./setup_venv.sh
   source kafka_env/bin/activate
   pip install flask flask-socketio kafka-python matplotlib numpy
   ```

3. **Establish Secure SSH Tunnels:**
   ```bash
   # Reverse tunnel for Kafka (Sends CERN data -> Local Mac)
   ssh -N -R 9092:localhost:9092 kayra@128.141.131.221
   
   # Forward tunnel for Prometheus (Fetches CERN metrics -> Local Grafana)
   ssh -N -L 9100:localhost:9100 kayra@128.141.131.221
   ```

---

## 5. The Detector Suite (Hardware & Simulation)

The simulation reproduces the complete BL4S beamline geometry:
* **TriggerModuleSatellite**: Software and hardware coincidences generator.
* **CalorimeterSatellite**: 16-channel Lead Glass Calorimeter measuring electromagnetic showers ($e^-$) vs. MIPs ($\pi$).
* **ScintillatorSatellite**: Dual-scintillator paddle array ($S_1, S_2$) measuring sub-nanosecond TDC timing and Poisson photoelectron yields.
* **TimepixSatellite**: $256 \times 256$ pixel matrix outputting sparse clustered hits with Time-over-Threshold (ToT) and Time-of-Arrival (ToA).
* **CherenkovSatellite**: Threshold gas detector for Particle Identification (PID), distinguishing relativistic electrons from heavier pions.

---

## 6. Configuration (TOML)

Save the following as `bl4s_config.toml`:

```toml
[TriggerModuleSatellite._default]
trigger_rate = 100.0

[CalorimeterSatellite._default]
channels = 16
rate = 100.0

[ScintillatorSatellite._default]
channels = 2
rate = 100.0

[TimepixSatellite._default]
channels = 16
rate = 100.0

[CherenkovSatellite._default]
channels = 16
rate = 100.0

[H5DataWriter._default]
output_path = "/eos/user/k/kyavuz/bl4s_data"
```

---

## 7. Step-by-Step Operating Tutorial

1. **Deploy and Start the DAQ Cluster on CERN Server:**
   ```bash
   cd /home/kayra/bl4s_simulation
   ./start_all.sh
   ```
2. **Orchestrating in MissionControl:**
   * Connect to group `bl4s`.
   * Click **Load Config** (`bl4s_config.toml`).
   * Click **Initialize** (All satellites turn Green / `INIT`).
   * Click **Launch** (All satellites turn Light Blue / `ORBIT`).
   * Click **Start** (All satellites turn Dark Blue / `RUN`).

---

## 8. Real-Time Monitoring & Observability Stack

### 8.1 BL4S Live Event Explorer (Web UI)
Launch the local web server:
```bash
source kafka_env/bin/activate
python bl4s_event_explorer_server.py
```
Open **[http://localhost:5050](http://localhost:5050)** in any browser.

**Key Features:**
* **Folder Tree Explorer**: Expand any satellite to reveal available visualizers.
* **Interactive Grid Cards**: Click to open/close live histogram panels.
* **4x4 Calorimeter Heatmap**: Displays spatial energy distribution across crystals.
* **256x256 Timepix Tracker**: Real-time beam spot and pixel cluster visualization.
* **Cherenkov PID Spectrum**: Visual electron vs. pion identification peaks.

### 8.2 Grafana Control Room Dashboard
Import `bl4s_grafana_dashboard.json` into Grafana at **[http://localhost:3000](http://localhost:3000)**.
* **Slow Controls**: High Voltage (HV), Cryogenic & PMT temperatures.
* **Data Rates**: Events per second, cumulative recorded data, server CPU load.

### 8.3 Live Kafka Calorimeter Viewer
For dedicated terminal-based Matplotlib animations:
```bash
source kafka_env/bin/activate
python live_kafka_viewer.py
```

---

## 9. Offline Data Analysis (HDF5)

When a run is stopped, Constellation flushes all events into high-performance HDF5 containers (`.h5`).

Analyze run files locally:
```bash
python analyze_h5_calorimeter.py path/to/run.h5
python analyze_h5_timepix.py path/to/run.h5
python analyze_h5_qdc.py path/to/run.h5
```
