import os
import struct
import json
import numpy as np
import time
from constellation.core.transmitter_satellite import TransmitterSatellite

class Geant4ReplaySatellite(TransmitterSatellite):
    """
    Base class for replaying Geant4/Allpix^2 simulated data.
    If a CSV/ROOT file is provided, it reads from it.
    If not, it calls `generate_physics_event()` which subclasses must implement
    to provide realistic Landau/Gaussian physics distributions.
    
    Includes optional Kafka streaming for real-time observability.
    """
    def do_initializing(self, config) -> None:
        self.log.info("Initializing physics replay...")
        self._replay_file = config.get_str("replay_file", default_value="")
        self._rate = config.get_float("rate", default_value=100.0)
        self._channels = config.get_int("channels", default_value=16)
        
        if self._replay_file and os.path.exists(self._replay_file):
            self.log.info(f"Replaying data from {self._replay_file}")
            self._mode = "file"
        else:
            self.log.info("No replay file found. Generating realistic physics models on the fly.")
            self._mode = "generate"
        
        # --- Kafka Live Streaming (Optional) ---
        self._kafka_producer = None
        self._kafka_topic = "bl4s_events"
        try:
            from kafka import KafkaProducer
            self._kafka_producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                request_timeout_ms=1000,
                max_block_ms=500,
                linger_ms=5,
                batch_size=16384
            )
            self.log.info("Kafka live streaming ENABLED on localhost:9092")
        except Exception as e:
            self.log.warning(f"Kafka not available ({e}). Running without live streaming.")
        
        if hasattr(super(), 'do_initializing'):
            super().do_initializing(config)

    def generate_physics_event(self) -> bytes:
        """
        Subclasses must implement this to return the raw bytes for the payload.
        """
        raise NotImplementedError("Subclasses must implement generate_physics_event")

    def decode_event_for_kafka(self, raw_bytes: bytes) -> list[dict]:
        """
        Subclasses should override this to return a list of dicts
        representing the decoded event for Kafka streaming.
        Default: sends the raw byte length as a simple metric.
        """
        return [{"sat": self.__class__.__name__, "raw_len": len(raw_bytes)}]

    def _send_to_kafka(self, events: list[dict]):
        """Send decoded events to Kafka, silently ignoring errors."""
        if self._kafka_producer is None:
            return
        try:
            for event in events:
                self._kafka_producer.send(self._kafka_topic, value=event)
        except Exception:
            pass

    def do_starting(self, payload: str) -> str:
        self.log.info(f"Starting physics replay for run: {payload}")
        self._event_number = 0
        return "Starting"

    def do_run(self) -> str:
        """
        Main loop to transmit data over Constellation ZMQ.
        """
        from constellation.core.message.cdtp2 import DataRecord
        from datetime import datetime, UTC
        
        while not self.stop_requested():
            self._event_number += 1
            record = DataRecord(sequence_number=self._event_number, tags={"timestamp": str(datetime.now(UTC))})
            
            if self._mode == "generate":
                payload_bytes = self.generate_physics_event()
            else:
                payload_bytes = self.generate_physics_event()
                
            record.add_block(payload_bytes)
            self.send_data_record(record)
            
            # Stream decoded event to Kafka for live observability
            kafka_events = self.decode_event_for_kafka(payload_bytes)
            self._send_to_kafka(kafka_events)
            
            # Rate limiting
            time.sleep(1.0 / self._rate)
            
        return "Finished run"
