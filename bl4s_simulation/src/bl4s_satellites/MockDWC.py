import threading
import time
import random
import struct
from typing import Any
from datetime import datetime, UTC

from constellation.core.configuration import Configuration
from constellation.core.transmitter_satellite import TransmitterSatellite
from constellation.core.message.cdtp2 import DataRecord

class MockDWC(TransmitterSatellite):
    def do_initializing(self, config: Configuration) -> None:
        self.rate = config.get_float("rate", default_value=10.0) # Data rate in Hz
        self._event_number = 0
        self.log.info(f"MockDWC initialized at {self.rate} Hz")

    def do_starting(self, run_identifier: str) -> str:
        self._event_number = 0
        self.log.info("Starting DWC tracking data generation")
        return "Starting"

    def do_run(self) -> str:
        while not self.stop_requested():
            time.sleep(1.0 / self.rate)
            self._event_number += 1
            record = DataRecord(sequence_number=self._event_number, tags={"type": "dwc", "timestamp": str(datetime.now(UTC))})
            
            # Generate fake (X, Y) hit coordinates (simulating DWC / Silicon pixel data)
            num_hits = random.randint(1, 3) # 1 to 3 particle hits per trigger
            hits_data = []
            for _ in range(num_hits):
                x = random.uniform(-10.0, 10.0)
                y = random.uniform(-10.0, 10.0)
                hits_data.extend([x, y])
            
            # Pack as binary (array of floats)
            payload_bytes = struct.pack(f"<{2 * num_hits}f", *hits_data)
            record.add_block(payload_bytes)
            
            self.send_data_record(record)
        return "Finished run"

def main(args=None):
    from constellation.core.satellite import SatelliteArgumentParser
    from constellation.core.logging import setup_cli_logging
    parser = SatelliteArgumentParser(description="Mock DWC Satellite")
    args = vars(parser.parse_args(args))
    setup_cli_logging(args.pop("level"))
    data_port = args.pop("data_port", 0)
    s = MockDWC(data_port, **args)
    s.run_satellite()

if __name__ == "__main__":
    main()
