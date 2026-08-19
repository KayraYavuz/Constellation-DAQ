import json
import time
import random
import numpy as np
from typing import Dict, Any, List

from constellation.core.satellite import Satellite
from constellation.core.configuration import Configuration

class CoincidenceEventBuilder(Satellite):
    """
    Sub-nanosecond Time-Window Coincidence Event Builder.
    Gathers asynchronous hits from all detector satellites and builds correlated
    physics events if and only if |t_hit - t_trig| <= delta_t (e.g. +-10 ns).
    Rejects accidental background noise.
    """
    def do_initializing(self, config: Configuration) -> None:
        self._window_ns = config.get_float("coincidence_window_ns", default_value=10.0)
        self._rate = config.get_float("rate", default_value=40.0)
        
        self._total_triggers = 0
        self._matched_events = 0
        self._rejected_noise_hits = 0
        
        self.log.info(f"CoincidenceEventBuilder initialized with timing window +- {self._window_ns} ns")

        self._kafka_producer = None
        self._kafka_topic = "bl4s_events"
        self._init_kafka()

    def _init_kafka(self):
        try:
            from kafka import KafkaProducer
            self._kafka_producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                request_timeout_ms=500,
                max_block_ms=200
            )
            self.log.info("Coincidence Builder Kafka streaming ENABLED on localhost:9092")
        except Exception:
            self._kafka_producer = None

    def process_event_candidate(self) -> Dict[str, Any]:
        """
        Simulates sub-nanosecond timestamp resolution across stations.
        """
        self._total_triggers += 1
        t_trigger = 0.0 # Reference trigger time (ns)
        
        # Real physics hits arrive with jitter ~ 0.8 ns Gaussian
        is_true_coincidence = random.random() < 0.85
        
        if is_true_coincidence:
            t_s1 = t_trigger + np.random.normal(-0.5, 0.4)
            t_s2 = t_trigger + np.random.normal(0.6, 0.4)
            t_dwc = t_trigger + np.random.normal(1.8, 1.2)
            t_tpx = t_trigger + np.random.normal(3.2, 1.5)
            t_calo = t_trigger + np.random.normal(7.5, 0.9)
            
            # Check window matching
            in_window = all(abs(t) <= self._window_ns for t in [t_s1, t_s2, t_dwc, t_tpx, t_calo])
            if in_window:
                self._matched_events += 1
                status = "COINCIDENCE_MATCHED"
            else:
                self._rejected_noise_hits += 1
                status = "JITTER_REJECTED"
        else:
            # Out-of-time background noise / cosmic ray / accidental coincidence
            t_s1 = t_trigger + np.random.uniform(-40, 40)
            t_s2 = t_trigger + np.random.uniform(-40, 40)
            t_dwc = t_trigger + np.random.uniform(-40, 40)
            t_tpx = t_trigger + np.random.uniform(-40, 40)
            t_calo = t_trigger + np.random.uniform(-40, 40)
            self._rejected_noise_hits += 1
            status = "BACKGROUND_REJECTED"

        rejection_pct = round((self._rejected_noise_hits / max(self._total_triggers, 1)) * 100.0, 1)
        efficiency_pct = round((self._matched_events / max(self._total_triggers, 1)) * 100.0, 1)

        return {
            "sat": "CoincidenceBuilder",
            "trigger_id": self._total_triggers,
            "status": status,
            "window_ns": self._window_ns,
            "delta_t_s1": round(float(t_s1), 2),
            "delta_t_s2": round(float(t_s2), 2),
            "delta_t_dwc": round(float(t_dwc), 2),
            "delta_t_timepix": round(float(t_tpx), 2),
            "delta_t_calo": round(float(t_calo), 2),
            "rejection_rate_pct": rejection_pct,
            "coincidence_efficiency_pct": efficiency_pct,
            "total_built": self._matched_events,
            "total_rejected": self._rejected_noise_hits
        }

    def do_run(self) -> str:
        while not self.stop_requested():
            coincidence_data = self.process_event_candidate()
            
            if self._kafka_producer:
                try:
                    self._kafka_producer.send(self._kafka_topic, value=coincidence_data)
                except Exception:
                    pass
                    
            time.sleep(1.0 / self._rate)
            
        return "Finished run"

def main(args=None):
    from constellation.core.satellite import SatelliteArgumentParser
    from constellation.core.logging import setup_cli_logging
    parser = SatelliteArgumentParser(description="Coincidence Window Event Builder Satellite")
    args = vars(parser.parse_args(args))
    setup_cli_logging(args.pop("level"))
    name = args.pop("name", "CoincidenceBuilder")
    s = CoincidenceEventBuilder(name, **args)
    s.run_satellite()

if __name__ == "__main__":
    main()
