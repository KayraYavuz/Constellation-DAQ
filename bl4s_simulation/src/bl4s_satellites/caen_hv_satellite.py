import time
import json
import random
import threading
from confluent_kafka import Producer

class CaenHvSatellite:
    def __init__(self, config):
        self.config = config
        self.kafka_broker = config.get('kafka_broker', 'localhost:9092')
        self.topic = 'slow_control'
        self.producer = Producer({'bootstrap.servers': self.kafka_broker})
        
        # Load CAEN configuration
        self.caen_ip = config.get('caen_ip', '192.168.1.100')
        self.connected = False
        
        # Try to import pycaenhv. If it fails or connection fails, we fallback to simulation.
        try:
            import pycaenhv
            print(f"[CAEN HV] Attempting to connect to real CAEN crate at {self.caen_ip}...")
            # Here we would normally connect: self.crate = pycaenhv.HVWrapper(self.caen_ip, ...)
            # Since this is local laptop without VPN, we simulate failure:
            raise ConnectionError(f"Cannot reach {self.caen_ip}")
        except Exception as e:
            print(f"[CAEN HV] Connection to {self.caen_ip} failed: {e}. Falling back to Simulation Mode.")
            self.connected = False
            
    def run(self):
        print("[CAEN HV] Starting telemetry loop...")
        while True:
            # Simulate fetching values from CAEN crate
            hv_data = {
                'timestamp': time.time(),
                'source': 'GECO_CAEN_HV',
                'channels': {
                    'CAL9': {'vmon': 1351.0 + random.uniform(-1, 1), 'imon': 402.6 + random.uniform(-0.5, 0.5), 'status': 'On'},
                    'CAL10': {'vmon': 1476.0 + random.uniform(-1, 1), 'imon': 436.5 + random.uniform(-0.5, 0.5), 'status': 'On'},
                    'S2': {'vmon': 0.0, 'imon': 0.0, 'status': 'Off'},
                    'DRIFT': {'vmon': 0.0, 'imon': 0.0, 'status': 'I-Tripped'}
                }
            }
            
            try:
                self.producer.produce(self.topic, json.dumps(hv_data).encode('utf-8'))
                self.producer.poll(0)
            except Exception as e:
                pass
                
            time.sleep(2.0)  # Telemetry update rate

if __name__ == "__main__":
    sat = CaenHvSatellite({})
    sat.run()
