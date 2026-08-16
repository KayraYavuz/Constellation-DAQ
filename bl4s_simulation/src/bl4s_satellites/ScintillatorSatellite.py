import struct
import numpy as np
import time
from Geant4ReplaySatellite import Geant4ReplaySatellite

class ScintillatorSatellite(Geant4ReplaySatellite):
    """
    Simulates Trigger Scintillators (e.g., S1, S2) in a BL4S beamline.
    Uses Poisson distribution for photon counting and Gaussian for TDC timing.
    """
    def do_starting(self, payload: str):
        super().do_starting(payload)
        self.log.info(f"Scintillator array initialized with {self._channels} channels")

    def generate_physics_event(self) -> bytes:
        payload = bytearray()
        for ch in range(self._channels):
            # 80% chance for a particle to hit the scintillator
            hit = 1 if np.random.rand() > 0.2 else 0
            
            # TDC time: tight Gaussian around 10 ns (cable delay + PMT transit)
            time_val = np.random.normal(10.0, 1.5) if hit else 0.0
            
            # Number of photoelectrons (Poisson)
            n_pe = np.random.poisson(30) if hit else 0
            
            # Format: <H (Channel/Status) B (n_pe) x (pad) f (time)
            channel_data = struct.pack('<H B x f', ch, n_pe, time_val)
            payload.extend(channel_data)
            
        return bytes(payload)

    def decode_event_for_kafka(self, raw_bytes: bytes) -> list[dict]:
        """Decode scintillator data into per-channel timing and PE readings."""
        events = []
        ch_size = 8
        num_channels = len(raw_bytes) // ch_size
        for i in range(num_channels):
            chunk = raw_bytes[i * ch_size : (i + 1) * ch_size]
            ch_id, n_pe, time_val = struct.unpack('<H B x f', chunk)
            events.append({
                "sat": "Scintillator",
                "ch": int(ch_id),
                "n_pe": int(n_pe),
                "time": float(time_val)
            })
        return events

def main(args=None):
    from constellation.core.satellite import SatelliteArgumentParser
    from constellation.core.logging import setup_cli_logging
    parser = SatelliteArgumentParser(description="BL4S Scintillator Satellite")
    args = vars(parser.parse_args(args))
    setup_cli_logging(args.pop("level"))
    data_port = args.pop("data_port", 0)
    s = ScintillatorSatellite(data_port, **args)
    s.run_satellite()

if __name__ == "__main__":
    main()
