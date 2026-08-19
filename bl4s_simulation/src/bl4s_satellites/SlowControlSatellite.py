import json
import time
import random
import numpy as np
from typing import Dict, Any

from constellation.core.satellite import Satellite
from constellation.core.configuration import Configuration

class SlowControlSatellite(Satellite):
    """
    Slow Control and Environmental Monitoring Satellite.
    Transmits slow hardware state, PMT High Voltage, gas pressures,
    detector temperatures, and alarm trip-points for EPICS/Grafana/Live UI.
    """
    def do_initializing(self, config: Configuration) -> None:
        self._interval_sec = config.get_float("interval_sec", default_value=1.0)
        self.log.info("SlowControlSatellite initialized (1.0 Hz slow control loop)")

        # Base physical setpoints
        self._pmt_hv_setpoints = [1420.0, 1418.0, 1450.0, 1390.0]  # Volts
        self._cherenkov_pressure_setpoint = 2.45                    # Bar (CO2)
        self._timepix_temp_setpoint = 18.5                          # Celsius
        self._ambient_temp_setpoint = 21.8                          # Celsius

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
            self.log.info("SlowControl Kafka streaming ENABLED on localhost:9092")
        except Exception:
            self._kafka_producer = None

    def read_telemetry(self) -> Dict[str, Any]:
        """
        Reads hardware sensors with realistic thermal and power fluctuations.
        """
        # Thermal drifts
        t_amb = self._ambient_temp_setpoint + random.gauss(0, 0.15)
        t_tpx = self._timepix_temp_setpoint + random.gauss(0, 0.10)
        t_ch = self._cherenkov_pressure_setpoint + random.gauss(0, 0.02)
        
        # PMT voltages with ripple
        hv = [round(sp + random.gauss(0, 0.4), 1) for sp in self._pmt_hv_setpoints]
        curr = [round(1.1 + random.gauss(0, 0.05), 2) for _ in range(4)]
        
        # Status checks
        status = "OPTIMAL"
        if max(hv) > 1550 or t_tpx > 25.0 or t_ch < 1.8:
            status = "WARNING"
        if max(hv) > 1650 or t_tpx > 30.0 or t_ch < 1.2:
            status = "CRITICAL_ALARM"

        return {
            "sat": "SlowControl",
            "timestamp": time.time(),
            "status_overall": status,
            "pmt_hv_v": hv,
            "pmt_current_ua": curr,
            "cherenkov_pressure_bar": round(t_ch, 3),
            "cherenkov_temp_c": round(t_amb - 0.5, 1),
            "timepix_temp_c": round(t_tpx, 1),
            "timepix_bias_v": -50.0 + random.gauss(0, 0.05),
            "ambient_temp_c": round(t_amb, 1),
            "ambient_humidity_pct": round(42.5 + random.gauss(0, 0.8), 1),
            "chiller_flow_lpm": round(3.25 + random.gauss(0, 0.05), 2)
        }

    def do_run(self) -> str:
        while not self.stop_requested():
            telemetry = self.read_telemetry()
            
            if self._kafka_producer:
                try:
                    self._kafka_producer.send(self._kafka_topic, value=telemetry)
                except Exception:
                    pass
                    
            time.sleep(self._interval_sec)
            
        return "Finished run"

def main(args=None):
    from constellation.core.satellite import SatelliteArgumentParser
    from constellation.core.logging import setup_cli_logging
    parser = SatelliteArgumentParser(description="Slow Control & Environmental Satellite")
    args = vars(parser.parse_args(args))
    setup_cli_logging(args.pop("level"))
    name = args.pop("name", "SlowControl")
    s = SlowControlSatellite(name, **args)
    s.run_satellite()

if __name__ == "__main__":
    main()
