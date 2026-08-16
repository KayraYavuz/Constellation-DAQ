import time
from prometheus_client import start_http_server, Counter, Gauge

from constellation.core.configuration import Configuration
from constellation.core.satellite import Satellite

class PrometheusExporter(Satellite):
    def do_initializing(self, config: Configuration) -> None:
        # Konfigürasyondan port adresini okuyoruz (Varsayılan 9100)
        self.metrics_port = config.get_int("metrics_port", default_value=9100)
        
        # Prometheus Metriklerini Tanımlıyoruz
        self.event_counter = Counter('constellation_events_total', 'Total number of events processed')
        self.temperature_gauge = Gauge('constellation_detector_temperature_celsius', 'Mock detector temperature')
        
        # Web sunucusunu (Prometheus'un kazıyacağı endpoint) başlatıyoruz
        start_http_server(self.metrics_port)
        self.log.info(f"Prometheus Exporter initialized. Metrics available at http://localhost:{self.metrics_port}/metrics")

    def do_starting(self, run_identifier: str) -> str:
        self.log.info(f"Prometheus Exporter starting for run: {run_identifier}")
        return "Starting"

    def do_run(self) -> str:
        # Gerçek bir sistemde bu döngü, ZeroMQ üzerinden gelen 'STAT' telemetri 
        # mesajlarını dinler ve Prometheus sayaçlarını günceller.
        # Bu mock versiyonda canlı sistem gibi sayaçları artırıyoruz:
        self.temperature_gauge.set(22.5)
        
        while not self.stop_requested():
            time.sleep(1.0)
            # Saniyede rastgele 80-120 arası event geliyormuş gibi sayacı artır
            import random
            events_in_second = random.randint(80, 120)
            self.event_counter.inc(events_in_second)
            
            # Sıcaklığı hafifçe oynat
            current_temp = self.temperature_gauge._value.get()
            self.temperature_gauge.set(current_temp + random.uniform(-0.1, 0.1))
            
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
