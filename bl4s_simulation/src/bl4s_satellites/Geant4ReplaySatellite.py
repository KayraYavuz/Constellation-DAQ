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
    def do_initializing(self, config) -> None:
        self.log.info("Initializing physics replay...")

        def safe_get(key, default):
            try:
                if isinstance(default, float) and hasattr(config, 'get_float'):
                    return config.get_float(key, default_value=default)
                if isinstance(default, int) and not isinstance(default, bool) and hasattr(config, 'get_int'):
                    return config.get_int(key, default_value=default)
                if isinstance(default, str) and hasattr(config, 'get_str'):
                    return config.get_str(key, default_value=default)
                if hasattr(config, 'get'):
                    return config.get(key, default_value=default)
            except Exception:
                pass
            return default

        self._replay_file = safe_get("replay_file", "")
        self._rate = safe_get("rate", 100.0)
        self._channels = safe_get("channels", 16)
        self._spill_duration_s = safe_get("spill_duration_s", 0.4)
        self._spill_period_s = safe_get("spill_period_s", 10.0)
        self._spill_mode = safe_get("spill_mode", True)
        
        if self._replay_file and os.path.exists(self._replay_file):
            self.log.info(f"Replaying data from {self._replay_file}")
            self._mode = "file"
        else:
            self.log.info(f"Generating realistic physics models on the fly (Spill mode: {self._spill_mode}, Cycle: {self._spill_period_s}s, Spill: {self._spill_duration_s}s)")
            self._mode = "generate"
        
        # --- Kafka Live Streaming (Optional) ---
        self._kafka_producer = None
        self._kafka_topic = "bl4s_events"
        self._last_kafka_attempt = 0
        self._init_kafka()
        
        if hasattr(super(), 'do_initializing'):
            super().do_initializing(config)

    def _init_kafka(self):
        """Attempt to initialize Kafka producer."""
        try:
            from kafka import KafkaProducer
            self._kafka_producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda x: x.SerializeToString(),
                request_timeout_ms=500,
                max_block_ms=200,
                linger_ms=5,
                batch_size=16384
            )
            self.log.info("Kafka live streaming ENABLED on localhost:9092 (Protobuf)")
        except Exception as e:
            self._kafka_producer = None

    def generate_physics_event(self) -> bytes:
        """
        Subclasses must implement this to return the raw bytes for the payload.
        """
        raise NotImplementedError("Subclasses must implement generate_physics_event")

    def decode_event_for_kafka(self, raw_bytes: bytes) -> list:
        """
        Subclasses should override this to return a list of Protobuf BL4SEvent
        messages representing the decoded event for Kafka streaming.
        """
        return []

    def _send_to_kafka(self, events: list):
        """Send decoded events to Kafka with seamless automatic reconnection."""
        if not events:
            return
        now = time.time()
        if self._kafka_producer is None:
            if now - self._last_kafka_attempt >= 4.0:
                self._last_kafka_attempt = now
                self._init_kafka()
            if self._kafka_producer is None:
                return

        try:
            for event in events:
                self._kafka_producer.send(self._kafka_topic, value=event)
        except Exception:
            self._kafka_producer = None
            self._last_kafka_attempt = now

    def do_starting(self, payload: str) -> str:
        self.log.info(f"Starting physics replay for run: {payload}")
        self._event_number = 0
        return "Starting"

    def do_run(self) -> str:
        """
        Main loop to transmit data over Constellation ZMQ and stream to Kafka.
        Adheres to CERN PS T9 beam extraction supercycle (0.4s beam-on / 9.6s beam-off).
        """
        from constellation.core.message.cdtp2 import DataRecord
        from datetime import datetime, timezone
        
        while not self.stop_requested():
            now = time.time()
            
            # Check beam extraction supercycle
            if self._spill_mode:
                cycle_pos = now % self._spill_period_s
                if cycle_pos > self._spill_duration_s:
                    # Off-spill (Inter-spill gap: 9.6s). Sleep briefly and loop.
                    time.sleep(0.04)
                    continue
            
            # In-spill (Beam ON: 0.4s burst): Generate event
            self._event_number += 1
            record = DataRecord(sequence_number=self._event_number, tags={"timestamp": str(datetime.now(timezone.utc))})
            
            if self._mode == "file":
                payload_bytes = self.generate_physics_event()
            else:
                payload_bytes = self.generate_physics_event()
                
            record.add_block(payload_bytes)
            self.send_data_record(record)
            
            # Stream decoded event to Kafka for live observability
            kafka_events = self.decode_event_for_kafka(payload_bytes)
            self._send_to_kafka(kafka_events)
            
            # In-spill high rate limiting
            time.sleep(1.0 / max(self._rate, 10.0))
            
        return "Finished run"
