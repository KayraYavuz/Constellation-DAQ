import time
import random
import struct
from datetime import datetime, UTC

from constellation.core.configuration import Configuration
from constellation.core.transmitter_satellite import TransmitterSatellite
from constellation.core.message.cdtp2 import DataRecord

class MockQDC(TransmitterSatellite):
    def do_initializing(self, config: Configuration) -> None:
        self.rate = config.get_float("rate", default_value=100.0)
        self.channels = config.get_int("channels", default_value=32)
        self._event_number = 0
        self.log.info(f"MockQDC initialized with {self.channels} channels at {self.rate} Hz")

    def do_starting(self, run_identifier: str) -> str:
        self._event_number = 0
        self.log.info("Starting QDC data generation")
        return "Starting"

    def do_run(self) -> str:
        while not self.stop_requested():
            time.sleep(1.0 / self.rate)
            self._event_number += 1
            record = DataRecord(sequence_number=self._event_number, tags={"type": "qdc", "timestamp": str(datetime.now(UTC))})
            
            # Use event_number as seed to ensure all mock detectors agree on the particle type
            random.seed(self._event_number)
            particle_roll = random.random()
            
            # Physics composition (5 GeV)
            # Pion: 65.1%
            # Kaon: 2.1%
            # Electron/Muon: 22.8%
            # Proton: 10.0%
            if particle_roll < 0.651:
                particle = 'Pion'
            elif particle_roll < 0.672:  # 0.651 + 0.021
                particle = 'Kaon'
            elif particle_roll < 0.900:  # + 0.228
                particle = 'Electron'
            else:
                particle = 'Proton'

            qdc_values = [0] * self.channels
            
            # Channel 0: S2 Scintillator (MIP for all)
            qdc_values[0] = int(random.gauss(200, 20))
            
            # Channel 1: S3 Scintillator (MIP for all)
            qdc_values[1] = int(random.gauss(200, 20))
            
            # Channel 2: Calorimeter / Lead Glass
            if particle == 'Electron':
                qdc_values[2] = int(random.gauss(800, 50)) # Electromagnetic shower
            else:
                qdc_values[2] = int(random.gauss(150, 15)) # MIP
                
            # Channel 3: Cherenkov C0
            if particle in ['Electron', 'Pion', 'Kaon']:
                qdc_values[3] = int(random.gauss(300, 30))
            else: # Proton
                qdc_values[3] = int(random.gauss(10, 5)) # Noise
                
            # Channel 4: Cherenkov C1
            if particle in ['Electron', 'Pion']:
                qdc_values[4] = int(random.gauss(300, 30))
            else: # Kaon, Proton
                qdc_values[4] = int(random.gauss(10, 5)) # Noise
                
            # Fill remaining channels with noise
            for ch in range(5, self.channels):
                qdc_values[ch] = int(random.gauss(20, 5))
                
            # Ensure no negative values
            qdc_values = [max(0, val) for val in qdc_values]
                
            # Pack as array of 32 unsigned short integers
            payload_bytes = struct.pack(f"<{self.channels}H", *qdc_values)
            record.add_block(payload_bytes)
            
            self.send_data_record(record)
        return "Finished run"

def main(args=None):
    from constellation.core.satellite import SatelliteArgumentParser
    from constellation.core.logging import setup_cli_logging
    parser = SatelliteArgumentParser(description="Mock QDC Satellite")
    args = vars(parser.parse_args(args))
    setup_cli_logging(args.pop("level"))
    data_port = args.pop("data_port", 0)
    s = MockQDC(data_port, **args)
    s.run_satellite()

if __name__ == "__main__":
    main()
