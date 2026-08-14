import time
import random
import struct
from datetime import datetime, UTC

from constellation.core.configuration import Configuration
from constellation.core.transmitter_satellite import TransmitterSatellite
from constellation.core.message.cdtp2 import DataRecord

class MockCalorimeter(TransmitterSatellite):
    def do_initializing(self, config: Configuration) -> None:
        self.rate = config.get_float("rate", default_value=100.0)
        self.channels = config.get_int("channels", default_value=16)
        self._event_number = 0
        self.log.info(f"MockCalorimeter initialized with {self.channels} channels at {self.rate} Hz")

    def do_starting(self, run_identifier: str) -> str:
        self._event_number = 0
        self.log.info("Starting Calorimeter data generation")
        return "Starting"

    def do_run(self) -> str:
        while not self.stop_requested():
            time.sleep(1.0 / self.rate)
            self._event_number += 1
            record = DataRecord(sequence_number=self._event_number, tags={"type": "calorimeter", "timestamp": str(datetime.now(UTC))})
            
            # Use event_number as seed
            random.seed(self._event_number)
            particle_roll = random.random()
            
            if particle_roll < 0.651:
                particle = 'Pion'
            elif particle_roll < 0.672:
                particle = 'Kaon'
            elif particle_roll < 0.900:
                particle = 'Electron'
            else:
                particle = 'Proton'

            payload_bytes = bytearray()
            
            # The Calorimeter has 16 segments/channels.
            for ch in range(self.channels):
                # Only a few central channels see the shower
                is_central = (ch in [6, 7, 9, 10])
                
                if is_central and particle == 'Electron':
                    amplitude = max(0, int(random.gauss(3000, 200)))
                    num_hits = max(1, int(random.gauss(10, 2)))
                elif is_central and particle in ['Pion', 'Kaon', 'Proton']:
                    amplitude = max(0, int(random.gauss(400, 50)))
                    num_hits = max(1, int(random.gauss(2, 1)))
                else:
                    # Noise for outer channels
                    amplitude = max(0, int(random.gauss(20, 5)))
                    num_hits = max(0, int(random.gauss(0.5, 0.5)))
                
                time_val = random.uniform(10.0, 50.0)
                
                # <H B x f = 8 bytes
                channel_bytes = struct.pack("<H B x f", amplitude, num_hits, time_val)
                payload_bytes.extend(channel_bytes)
                
            record.add_block(payload_bytes)
            self.send_data_record(record)
            
        return "Finished run"

def main(args=None):
    from constellation.core.satellite import SatelliteArgumentParser
    from constellation.core.logging import setup_cli_logging
    parser = SatelliteArgumentParser(description="Mock Calorimeter Satellite")
    args = vars(parser.parse_args(args))
    setup_cli_logging(args.pop("level"))
    data_port = args.pop("data_port", 0)
    s = MockCalorimeter(data_port, **args)
    s.run_satellite()

if __name__ == "__main__":
    main()
