import json
import time
import random
import threading
import numpy as np
from typing import Dict, Any, Optional

from constellation.core.satellite import Satellite
from constellation.core.configuration import Configuration

class TriggerModuleSatellite(Satellite):
    """
    Advanced Hardware Trigger & Control Board Satellite (BL4S Logic Unit).
    Implements:
    1. Multi-Stage Scintillator Coincidence Logic (S1 AND S2 AND [NOT VETO] AND [Cherenkov TAG])
    2. DAQ Readout Busy & Inhibit Gate (Dead-time Veto Management)
    3. Live Real-Time Telemetry: Dead Time %, Live Time %, Accepted vs Vetoed Trigger Rates
    """
    def do_initializing(self, config: Configuration) -> None:
        self._raw_trigger_rate = config.get_float("raw_rate", default_value=120.0) # Raw particle rate (Hz)
        self._coincidence_window_ns = config.get_float("coincidence_window_ns", default_value=10.0)
        self._s1_threshold_pe = config.get_int("s1_threshold_pe", default_value=5)
        self._s2_threshold_pe = config.get_int("s2_threshold_pe", default_value=5)
        self._readout_deadtime_ms = config.get_float("readout_deadtime_ms", default_value=3.5) # Dead-time per event
        self._require_cherenkov_tag = config.get("require_cherenkov_tag", default_value=False)
        
        # Internal State & Counters
        self._trigger_id = 0
        self._raw_events = 0
        self._coincidence_matches = 0
        self._vetoed_busy_triggers = 0
        self._accepted_triggers = 0
        self._vetoed_busy_triggers = 0
        self._is_busy = False
        self._busy_until = 0.0
        self._last_telemetry_time = 0.0

        # Optional Kafka telemetry
        self._kafka_producer = None
        self._kafka_topic = "bl4s_events"
        self._init_kafka()

        self.log.info(f"Trigger Module initialized (Coincidence window: ±{self._coincidence_window_ns}ns, Dead-time: {self._readout_deadtime_ms}ms, Spill mode: {self._spill_mode})")

    def _init_kafka(self):
        try:
            from kafka import KafkaProducer
            self._kafka_producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                request_timeout_ms=500,
                max_block_ms=200
            )
        except Exception:
            self._kafka_producer = None

    def evaluate_trigger_logic(self) -> Dict[str, Any]:
        """
        Simulates hardware discriminator pulses, coincidence AND gate, and BUSY veto inhibit.
        Synchronized with CERN PS T9 beam extraction supercycle (0.4s spill / 9.6s inter-spill).
        """
        now = time.time()
        self._raw_events += 1
        
        # 1. Update BUSY state based on dead-time clock
        if self._is_busy and now >= self._busy_until:
            self._is_busy = False

        # 2. Check Beam Extraction Cycle
        is_in_spill = True
        if self._spill_mode:
            cycle_pos = now % self._spill_period_s
            is_in_spill = cycle_pos <= self._spill_duration_s

        # 3. Simulate Scintillator Pulses (Photo-electrons & TDC timings)
        has_particle = (random.random() < 0.92) if is_in_spill else (random.random() < 0.01)
        if has_particle:
            s1_pe = np.random.poisson(32)
            s2_pe = np.random.poisson(30)
            t_s1 = np.random.normal(10.0, 0.4) # ns
            t_s2 = np.random.normal(10.8, 0.4) # ns
            cherenkov_qdc = np.random.normal(500, 150)
        else:
            s1_pe = np.random.poisson(2)
            s2_pe = np.random.poisson(1)
            t_s1 = np.random.uniform(0, 50)
            t_s2 = np.random.uniform(0, 50)
            cherenkov_qdc = np.random.exponential(20)

        # Coincidence Condition: S1 >= Thresh AND S2 >= Thresh AND |t1 - t2| <= delta_t
        s1_pass = s1_pe >= self._s1_threshold_pe
        s2_pass = s2_pe >= self._s2_threshold_pe
        timing_pass = abs(t_s1 - t_s2) <= self._coincidence_window_ns
        cherenkov_pass = True if not self._require_cherenkov_tag else (cherenkov_qdc > 300.0)

        is_valid_coincidence = s1_pass and s2_pass and timing_pass and cherenkov_pass

        trigger_decision = "NO_COINCIDENCE"
        is_triggered = False

        if is_valid_coincidence:
            self._coincidence_matches += 1
            # 3. Check Control Board BUSY Inhibit Gate
            if self._is_busy:
                # DAQ is reading out previous event -> VETO / INHIBIT
                self._vetoed_busy_triggers += 1
                trigger_decision = "VETOED_BUSY"
            else:
                # DAQ is ready -> ACCEPT TRIGGER
                self._trigger_id += 1
                self._accepted_triggers += 1
                self._is_busy = True
                self._busy_until = now + (self._readout_deadtime_ms / 1000.0)
                trigger_decision = "TRIGGER_ACCEPTED"
                is_triggered = True
                self.stat("SWTRIG", self._trigger_id)

        # Telemetry metrics
        dead_time_pct = round((self._vetoed_busy_triggers / max(self._coincidence_matches, 1)) * 100.0, 1)
        live_time_pct = round(100.0 - dead_time_pct, 1)
        efficiency_pct = round((self._accepted_triggers / max(self._raw_events, 1)) * 100.0, 1)

        return {
            "sat": "TriggerControlBoard",
            "trigger_id": self._trigger_id,
            "decision": trigger_decision,
            "is_triggered": is_triggered,
            "is_busy": self._is_busy,
            "s1_pe": int(s1_pe),
            "s2_pe": int(s2_pe),
            "delta_t_ns": round(float(t_s1 - t_s2), 2),
            "coincidence_passed": is_valid_coincidence,
            "cherenkov_qdc": round(float(cherenkov_qdc), 1),
            "dead_time_pct": dead_time_pct,
            "live_time_pct": live_time_pct,
            "trigger_efficiency_pct": efficiency_pct,
            "total_raw_events": self._raw_events,
            "total_coincidences": self._coincidence_matches,
            "total_vetoed_busy": self._vetoed_busy_triggers,
            "total_accepted": self._accepted_triggers,
            "is_in_spill": is_in_spill,
            "timestamp": now
        }

    def do_run(self) -> str:
        while not self.stop_requested():
            decision_data = self.evaluate_trigger_logic()
            
            # Broadcast to Kafka every 100ms or upon accepted trigger
            now = time.time()
            if self._kafka_producer and (decision_data["is_triggered"] or (now - self._last_telemetry_time) >= 0.1):
                try:
                    self._kafka_producer.send(self._kafka_topic, value=decision_data)
                except Exception:
                    pass
                self._last_telemetry_time = now

            time.sleep(1.0 / self._raw_trigger_rate)

        return "Finished run"

def main(args=None):
    from constellation.core.satellite import SatelliteArgumentParser
    from constellation.core.logging import setup_cli_logging
    parser = SatelliteArgumentParser(description="BL4S Advanced Trigger & Control Board Satellite")
    args = vars(parser.parse_args(args))
    setup_cli_logging(args.pop("level"))
    name = args.pop("name", "TriggerModule")
    s = TriggerModuleSatellite(name, **args)
    s.run_satellite()

if __name__ == "__main__":
    main()
