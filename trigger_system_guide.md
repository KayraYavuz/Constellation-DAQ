# ⚡ BL4S 2026: Trigger & Polling Architecture and Satellite Implementation Guide

This guide provides a comprehensive technical breakdown of the **Polling-Based Trigger & Event Building Architecture**, its underlying physics principles, and the C++ / Python satellite implementations used in the **Constellation DAQ** framework for the **CERN PS East Area T9 Beamline**.

---

## 📑 Table of Contents
1. [What is TDAQ and Polling in Particle Physics?](#1-what-is-tdaq-and-polling-in-particle-physics)
2. [Why Do We Use 2 Dedicated Trigger Satellites?](#2-why-do-we-use-2-dedicated-trigger-satellites)
3. [Satellite 1: TriggerModuleSatellite (C++ & Python Implementation)](#3-satellite-1-triggermodulesatellite)
4. [Satellite 2: CoincidenceEventBuilder (Event Building & Noise Rejection)](#4-satellite-2-coincidenceeventbuilder)
5. [Transitioning to Real Hardware (CAEN VME): Implementing poll_register()](#5-transitioning-to-real-hardware-caen-vme-implementing-poll_register)
6. [Key Jury Presentation Points & Q&A Defense](#6-key-jury-presentation-points--qa-defense)

---

## 1. What is TDAQ and Polling in Particle Physics?

In High-Energy Physics (HEP) test beam experiments, detectors generate millions of raw electrical pulses per second from background noise, cosmic rays, and secondary particles. Digitizing and storing all signals unconditionally would instantly saturate bus bandwidth and disk storage.

* **Trigger (TDAQ):** A rapid hardware/software decision system that identifies physically meaningful interactions (e.g., simultaneous signals in beamline scintillators $S_1 \land S_2$) and issues an acquisition gate (*Level-1 Accept* / L1A).
* **Polling:** The continuous, high-frequency querying of a hardware readout register (e.g., VME / QDC status word) by the DAQ software to check whether `DATA_READY` is asserted, eliminating interrupt-driven context-switch latency.

---

## 2. Why Do We Use 2 Dedicated Trigger Satellites?

Following modern HEP DAQ standards (such as ATLAS/CMS Level-1 Trigger and Event Filter architectures), our framework decouples trigger arbitration from multi-detector event assembly:

```
[ Physical Hardware / NIM Logic / VME Register ]
                       │
                       ▼ (Fast Register Polling)
┌─────────────────────────────────────────────────────────────┐
│ 1. TriggerModuleSatellite                                   │ ──▶ Broadcasts SWTRIG Telemetry
│    - Fast Hardware Register Polling                         │     ("Trigger ID #104 Accepted!")
│    - Multi-Stage Coincidence Logic                          │
│    - DAQ Readout Busy & Inhibit Gate (3.5 ms Dead-time)     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. CoincidenceEventBuilder                                  │ ──▶ Correlates Sub-Detectors (Calo, Timepix, Cherenkov)
│    - Sub-nanosecond Time-Window Matching (±10 ns)           │ ──▶ Builds unified global HDF5 event
│    - Out-of-Time Background & Jitter Rejection              │
└─────────────────────────────────────────────────────────────┘
```

1. **`TriggerModuleSatellite` (The Gatekeeper):** Runs at maximum clock frequency to poll registers, stamp `Trigger IDs`, enforce dead-time vetos, and synchronize with the 0.4s CERN PS spill extraction.
2. **`CoincidenceEventBuilder` (The Correlator):** Collects asynchronous payload blocks pushed by sub-detector satellites, aligns them within the coincidence gate ($\pm \Delta t$), and outputs unified physics events.

---

## 3. Satellite 1: TriggerModuleSatellite

### 🔹 Official C++ Implementation (DESY / Constellation Reference Standard)

This reference C++ implementation demonstrates the standardized `SWTRIG` telemetry mechanism provided by Constellation:

```cpp
#include "TriggerModuleSatellite.hpp"
#include <random>
#include <stop_token>
#include <string_view>
#include "constellation/core/log/log.hpp"
#include "constellation/core/metrics/stat.hpp"
#include "constellation/satellite/Satellite.hpp"

using namespace constellation::satellite;

// 1. Constructor: Register the standardized SWTRIG metric across the Constellation group
TriggerModuleSatellite::TriggerModuleSatellite(std::string_view type, std::string_view name) 
    : Satellite(type, name) {
    register_metric("SWTRIG", "", "Software trigger signal, carries the trigger ID");
}

// 2. Run Initialization: Reset trigger sequence counter on Start
void TriggerModuleSatellite::starting(std::string_view /*run_identifier*/) {
    trigger_id_ = 0;
}

// 3. Hardware Polling Hook (Mock distribution in simulation, VME register read in beamline)
bool TriggerModuleSatellite::poll_register() const {
    static thread_local std::mt19937 rng(std::random_device {}());
    static thread_local std::bernoulli_distribution dist(0.000001);
    return dist(rng);
}

// 4. Main Execution Loop: Ultra-fast non-blocking polling
void TriggerModuleSatellite::running(const std::stop_token& stop_token) {
    while(!stop_token.stop_requested()) {
        // Continuous register poll:
        if(poll_register()) {
            trigger_id_++;
            
            // Broadcast software trigger telemetry to all participating satellites:
            STAT("SWTRIG", trigger_id_.load());
            LOG(DEBUG) << "Sent software trigger with ID " << trigger_id_.load();
        }
    }
}
```

---

### 🔹 Python Implementation (`TriggerModuleSatellite.py`)

Our Python satellite implements full multi-stage NIM coincidence logic, CERN PS spill synchronization, and a realistic dead-time veto gate:

```python
def evaluate_trigger_logic(self) -> Dict[str, Any]:
    now = time.time()
    self._raw_events += 1
    
    # 1. Update BUSY state based on dead-time clock
    if self._is_busy and now >= self._busy_until:
        self._is_busy = False

    # 2. Check CERN PS T9 Spill Cycle (0.4s beam-on / 9.6s inter-spill)
    cycle_pos = now % self._spill_period_s
    is_in_spill = cycle_pos <= self._spill_duration_s

    # 3. Multi-Stage Scintillator Coincidence Condition:
    # S1 >= Thresh AND S2 >= Thresh AND |t1 - t2| <= coincidence_window (10 ns)
    s1_pass = s1_pe >= self._s1_threshold_pe
    s2_pass = s2_pe >= self._s2_threshold_pe
    timing_pass = abs(t_s1 - t_s2) <= self._coincidence_window_ns
    is_valid_coincidence = s1_pass and s2_pass and timing_pass

    trigger_decision = "NO_COINCIDENCE"
    is_triggered = False

    if is_valid_coincidence:
        self._coincidence_matches += 1
        # 4. Check DAQ Inhibit / BUSY Gate
        if self._is_busy:
            # Previous event is being digitized -> VETO / INHIBIT
            self._vetoed_busy_triggers += 1
            trigger_decision = "VETOED_BUSY"
        else:
            # DAQ Ready -> ACCEPT TRIGGER
            self._trigger_id += 1
            self._accepted_triggers += 1
            self._is_busy = True
            self._busy_until = now + (self._readout_deadtime_ms / 1000.0) # 3.5 ms dead-time
            
            # Emit official SWTRIG metric:
            self.stat("SWTRIG", self._trigger_id)
            trigger_decision = "TRIGGER_ACCEPTED"
            is_triggered = True

    return {
        "trigger_id": self._trigger_id,
        "decision": trigger_decision,
        "is_triggered": is_triggered,
        "dead_time_pct": round((self._vetoed_busy_triggers / max(self._coincidence_matches, 1)) * 100.0, 1),
        "live_time_pct": round(100.0 - dead_time_pct, 1)
    }
```

---

## 4. Satellite 2: CoincidenceEventBuilder

The `CoincidenceEventBuilder` aligns multi-detector payload streams against the reference trigger timestamp:

```python
class CoincidenceEventBuilder(Satellite):
    def process_event_candidate(self) -> Dict[str, Any]:
        t_trigger = 0.0 # Reference trigger timestamp (ns)
        
        # Sub-detector timestamps arriving from asynchronous satellite channels:
        # t_s1, t_s2, t_dwc, t_timepix, t_calo
        
        # Verify coincidence window condition (|t_hit - t_trig| <= 10 ns):
        in_window = all(abs(t) <= self._window_ns for t in [t_s1, t_s2, t_dwc, t_tpx, t_calo])
        
        if in_window:
            self._matched_events += 1
            status = "COINCIDENCE_MATCHED"
            # Package sub-detector data into unified HDF5 container
        else:
            self._rejected_noise_hits += 1
            status = "BACKGROUND_REJECTED" # Drop out-of-time background
            
        return {"status": status, "built_events": self._matched_events}
```

---

## 5. Transitioning to Real Hardware (CAEN VME): Implementing `poll_register()`

When deployed on the physical VME crate at CERN T9, the simulation function is replaced with direct register reads via `libCAENVME.so`:

```cpp
bool TriggerModuleSatellite::poll_register() const {
    uint32_t status_reg = 0;
    
    // Read Status Register via CAEN V1718 USB-VME Bridge:
    CVErrorCodes err = CAENVME_ReadRegister(vme_handle_, VME_STATUS_REGISTER_ADDR, &status_reg);
    
    if (err != cvSuccess) {
        return false;
    }
    
    // Bit 0: DATA_READY (NIM coincidence strobe asserted)
    // Bit 2: BUSY (Readout FIFO in progress)
    bool data_ready = (status_reg & 0x01) != 0;
    bool busy = (status_reg & 0x04) != 0;
    
    return data_ready && !busy;
}
```

---

## 6. Key Jury Presentation Points & Q&A Defense

> **Q: "Why did you implement a polling trigger rather than an interrupt-driven approach?"**
> 
> **Defense:** *"In high-rate particle beamlines such as CERN T9, interrupt-driven readout introduces significant operating system context-switching overhead (IRQ latency). By utilizing high-frequency register polling in our dedicated `TriggerModuleSatellite`, we achieve deterministic sub-microsecond response times while managing dead-time vetos and `SWTRIG` telemetry in strict accordance with Constellation core guidelines."*
