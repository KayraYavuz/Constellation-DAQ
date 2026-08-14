import threading
import time
from typing import Any
from datetime import datetime, UTC

from constellation.core.configuration import Configuration
from constellation.core.transmitter_satellite import TransmitterSatellite
from constellation.core.message.cdtp2 import DataRecord

class MockTrigger(TransmitterSatellite):
    def do_initializing(self, config: Configuration) -> None:
        self.rate = config.get_float("rate", default_value=10.0) # Trigger rate in Hz
        self._thread = None
        self._stop_event = threading.Event()
        self._event_number = 0
        self.log.info(f"MockTrigger initialized with rate {self.rate} Hz")

    def do_starting(self, payload: Any) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._daq_loop, daemon=True)
        self._thread.start()
        self.log.info("Started generating triggers")

    def do_stopping(self, payload: Any) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        self.log.info("Stopped generating triggers")

    def _daq_loop(self):
        while not self._stop_event.is_set():
            time.sleep(1.0 / self.rate)
            self._event_number += 1
            record = DataRecord(sequence_number=self._event_number, tags={"type": "trigger", "timestamp": str(datetime.now(UTC))})
            record.add_block(f"TRIGGER_ID_{self._event_number}".encode())
            self.send_data_record(record)

def main(args=None):
    from constellation.core.satellite import SatelliteArgumentParser
    from constellation.core.logging import setup_cli_logging
    parser = SatelliteArgumentParser(description="Mock Trigger Satellite")
    args = vars(parser.parse_args(args))
    setup_cli_logging(args.pop("level"))
    data_port = args.pop("data_port", 0)
    s = MockTrigger(data_port, **args)
    s.run_satellite()

if __name__ == "__main__":
    main()
