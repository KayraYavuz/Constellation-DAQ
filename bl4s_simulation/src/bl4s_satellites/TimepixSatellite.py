import struct
import numpy as np
import time
from Geant4ReplaySatellite import Geant4ReplaySatellite

class TimepixSatellite(Geant4ReplaySatellite):
    """
    Simulates a Timepix Silicon Pixel Detector (256x256 pixels).
    Generates sparse data (only pixels that were hit).
    Each hit is 16 bytes: X (1B), Y (1B), fToA (1B), pad (1B), ToT (2B), pad (2B), ToA_low (4B), ToA_high (4B).
    """
    def do_starting(self, payload: str):
        super().do_starting(payload)
        self.log.info("Timepix3 array initialized (256x256)")

    def generate_physics_event(self) -> bytes:
        payload = bytearray()
        
        # 30% chance for a particle track
        if np.random.rand() > 0.7:
            # Generate a "beam spot" near the center
            center_x = np.random.normal(128, 20)
            center_y = np.random.normal(128, 20)
            
            # A track usually hits a cluster of 1-4 pixels
            cluster_size = np.random.poisson(2) + 1
            for _ in range(cluster_size):
                x = int(np.clip(np.random.normal(center_x, 1.0), 0, 255))
                y = int(np.clip(np.random.normal(center_y, 1.0), 0, 255))
                
                # ToT (energy proxy) follows a Landau-like shape
                tot = int(np.clip(np.random.gamma(shape=2.0, scale=50.0), 0, 65535))
                
                ftoa = np.random.randint(0, 16)
                toa_low = np.random.randint(0, 10000)
                toa_high = 0
                
                # Format: <B B B x H x x I I -> Total 16 bytes
                hit_data = struct.pack('<B B B x H x x I I', x, y, ftoa, tot, toa_low, toa_high)
                payload.extend(hit_data)
                
        return bytes(payload)

    def decode_event_for_kafka(self, raw_bytes: bytes) -> list[dict]:
        """Decode Timepix data into per-hit pixel readings."""
        events = []
        hit_size = 16
        num_hits = len(raw_bytes) // hit_size
        for i in range(num_hits):
            chunk = raw_bytes[i * hit_size : (i + 1) * hit_size]
            x, y, ftoa, tot, toa_low, toa_high = struct.unpack('<B B B x H x x I I', chunk)
            events.append({
                "sat": "Timepix",
                "x": int(x),
                "y": int(y),
                "tot": int(tot),
                "toa": int(toa_low)
            })
        # If no hits, send an empty marker so the UI knows it's alive
        if not events:
            events.append({"sat": "Timepix", "x": -1, "y": -1, "tot": 0, "toa": 0})
        return events

def main(args=None):
    from constellation.core.satellite import SatelliteArgumentParser
    from constellation.core.logging import setup_cli_logging
    parser = SatelliteArgumentParser(description="BL4S Timepix Satellite")
    args = vars(parser.parse_args(args))
    setup_cli_logging(args.pop("level"))
    data_port = args.pop("data_port", 0)
    s = TimepixSatellite(data_port, **args)
    s.run_satellite()

if __name__ == "__main__":
    main()
