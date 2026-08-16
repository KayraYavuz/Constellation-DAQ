import json
import random
import time
from typing import Any

from constellation.core.satellite import Satellite
from constellation.core.configuration import Configuration

class TriggerModuleSatellite(Satellite):
    """
    Python implementation of TriggerModuleSatellite
    It uses telemetry (STAT) to send software trigger IDs.
    Includes optional Kafka streaming for live observability.
    """
    def do_initializing(self, config: Configuration) -> None:
        self.trigger_id = 0
        if hasattr(self, "_mnt") and self._mnt:
            self._mnt.register_metric("SWTRIG", "", "Software trigger signal, carries the trigger ID")
        self.log.info("TriggerModuleSatellite initialized")

        # --- Kafka Live Streaming (Optional) ---
        self._kafka_producer = None
        self._kafka_topic = "bl4s_events"
        self._last_kafka_time = time.time()
        try:
            from kafka import KafkaProducer
            self._kafka_producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                request_timeout_ms=1000,
                max_block_ms=500
            )
            self.log.info("Trigger Kafka live streaming ENABLED on localhost:9092")
        except Exception as e:
            self.log.warning(f"Kafka not available ({e}). Running without live streaming.")

    def do_starting(self, run_identifier: str) -> str:
        self.trigger_id = 0
        self._last_kafka_time = time.time()
        self.log.info("TriggerModuleSatellite starting")
        return "Starting"

    def poll_register(self) -> bool:
        return random.random() < 0.000001

    def do_run(self) -> str:
        while not self.stop_requested():
            if self.poll_register():
                self.trigger_id += 1
                self.stat("SWTRIG", self.trigger_id)
                self.log.debug(f"Sent software trigger with ID {self.trigger_id}")

            # Send trigger rate to Kafka every 500ms
            now = time.time()
            if self._kafka_producer and (now - self._last_kafka_time) >= 0.5:
                try:
                    self._kafka_producer.send(self._kafka_topic, value={
                        "sat": "Trigger",
                        "id": self.trigger_id,
                        "timestamp": now
                    })
                except Exception:
                    pass
                self._last_kafka_time = now

            time.sleep(0.0001)
        return "Finished run"

def main(args=None):
    from constellation.core.satellite import SatelliteArgumentParser
    from constellation.core.logging import setup_cli_logging
    parser = SatelliteArgumentParser(description="Trigger Module Satellite")
    args = vars(parser.parse_args(args))
    setup_cli_logging(args.pop("level"))
    name = args.pop("name", "TriggerModule")
    s = TriggerModuleSatellite(name, **args)
    s.run_satellite()

if __name__ == "__main__":
    main()
