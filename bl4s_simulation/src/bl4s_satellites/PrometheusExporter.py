import time
import random
from prometheus_client import start_http_server, Counter, Gauge, Histogram

from constellation.core.configuration import Configuration
from constellation.core.satellite import Satellite

class PrometheusExporter(Satellite):
    def do_initializing(self, config: Configuration) -> None:
        self.metrics_port = config.get_int("metrics_port", default_value=9100)
        
        # --- MORE DETAILED METRICS ---
        self.event_counter = Counter('constellation_events_total', 'Total number of events processed')
        self.data_volume = Counter('constellation_data_bytes_total', 'Total bytes of data generated')
        
        self.temperature_gauge = Gauge('constellation_detector_temperature_celsius', 'Detector temperature')
        self.hv_gauge = Gauge('constellation_detector_high_voltage', 'Detector High Voltage (V)')
        self.cpu_load = Gauge('constellation_system_cpu_load_percent', 'Simulated CPU Load (%)')
        self.active_channels = Gauge('constellation_active_channels', 'Number of active detector channels')
        
        self.event_size_hist = Histogram('constellation_event_size_bytes', 'Size of events in bytes', buckets=(64, 128, 256, 512, 1024, 2048))
        
        start_http_server(self.metrics_port)
        self.log.info(f"Prometheus Exporter initialized. Metrics available at http://localhost:{self.metrics_port}/metrics")

    def do_starting(self, run_identifier: str) -> str:
        self.log.info(f"Prometheus Exporter starting for run: {run_identifier}")
        return "Starting"

    def do_run(self) -> str:
        self.temperature_gauge.set(22.5)
        self.hv_gauge.set(1200.0) # Nominal HV for PMT/SiPM
        self.active_channels.set(34) # 16 Calo + 16 Cherenkov + 2 Scint
        
        while not self.stop_requested():
            time.sleep(1.0)
            
            events_in_second = random.randint(85, 115)
            self.event_counter.inc(events_in_second)
            
            # Simulate data volume (approx 128 bytes per event)
            bytes_in_second = events_in_second * random.randint(110, 140)
            self.data_volume.inc(bytes_in_second)
            
            # Observe some event sizes
            for _ in range(10):
                self.event_size_hist.observe(random.gauss(128, 20))
            
            # Fluctuate environment metrics slightly
            current_temp = self.temperature_gauge._value.get()
            self.temperature_gauge.set(current_temp + random.uniform(-0.05, 0.05))
            
            current_hv = self.hv_gauge._value.get()
            self.hv_gauge.set(current_hv + random.uniform(-0.5, 0.5))
            
            self.cpu_load.set(random.uniform(15.0, 35.0))
            
        return "Finished run"

def main(args=None):
    from constellation.core.satellite import SatelliteArgumentParser
    from constellation.core.logging import setup_cli_logging
    parser = SatelliteArgumentParser(description="Prometheus Exporter Satellite")
    args = vars(parser.parse_args(args))
    setup_cli_logging(args.pop("level"))
    s = PrometheusExporter(**args)
    s.run_satellite()

if __name__ == "__main__":
    main()
