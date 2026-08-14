import time
import random
import struct
from datetime import datetime, UTC

from constellation.core.configuration import Configuration
from constellation.core.transmitter_satellite import TransmitterSatellite
from constellation.core.message.cdtp2 import DataRecord

class MockTimePix(TransmitterSatellite):
    def do_initializing(self, config: Configuration) -> None:
        self.rate = config.get_float("rate", default_value=100.0)
        self._event_number = 0
        
        # Simülasyon parametreleri (TimePix çözünürlüğü 256x256)
        self.beam_x = 128.0
        self.beam_y = 128.0
        self.beam_spread = 20.0
        
        # Basit bir sayaç (toa)
        self.global_time = 0
        
        self.log.info(f"MockTimePix initialized at {self.rate} Hz")

    def do_starting(self, run_identifier: str) -> str:
        self._event_number = 0
        self.log.info("Starting TimePix data generation")
        return "Starting"

    def do_run(self) -> str:
        while not self.stop_requested():
            time.sleep(1.0 / self.rate)
            self._event_number += 1
            self.global_time += int(1e6) # her event arası 1 ms artış simülasyonu
            
            record = DataRecord(sequence_number=self._event_number, tags={"type": "timepix", "timestamp": str(datetime.now(UTC))})
            
            # Bu event'teki hit sayısı (0 ile 50 arası rastgele)
            num_hits = random.randint(0, 50)
            
            payload_bytes = bytearray()
            for _ in range(num_hits):
                # x, y piksel koordinatları (0-255)
                x = int(random.gauss(self.beam_x, self.beam_spread))
                y = int(random.gauss(self.beam_y, self.beam_spread))
                # Sınırların içine çek (0-255)
                x = max(0, min(255, x))
                y = max(0, min(255, y))
                
                # ftoa (0-15)
                ftoa = random.randint(0, 15)
                
                # ToT (0-4095)
                tot = max(0, min(4095, int(random.gauss(1000, 300))))
                
                # ToA (Time of Arrival)
                # Küçük rastgelelik ekle
                hit_time = self.global_time + random.randint(0, 10000)
                toa_low = hit_time & 0xFFFFFFFF
                toa_high = (hit_time >> 32) & 0xFFFFFFFF
                
                # Paketleme formatı: <B B B x H x x I I (16 byte)
                # B(x), B(y), B(ftoa), x(pad)
                # H(tot), x(pad), x(pad)
                # I(toa_low), I(toa_high)
                payload_bytes += struct.pack("<B B B x H x x I I", x, y, ftoa, tot, toa_low, toa_high)
                
            record.add_block(bytes(payload_bytes))
            self.send_data_record(record)
            
        return "Finished run"

def main(args=None):
    from constellation.core.satellite import SatelliteArgumentParser
    from constellation.core.logging import setup_cli_logging
    parser = SatelliteArgumentParser(description="Mock TimePix Satellite")
    args = vars(parser.parse_args(args))
    setup_cli_logging(args.pop("level"))
    data_port = args.pop("data_port", 0)
    s = MockTimePix(data_port, **args)
    s.run_satellite()

if __name__ == "__main__":
    main()
