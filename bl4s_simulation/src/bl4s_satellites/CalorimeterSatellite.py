import struct
import numpy as np
import time
from Geant4ReplaySatellite import Geant4ReplaySatellite

class CalorimeterSatellite(Geant4ReplaySatellite):
    """
    Simulates a Lead Glass Calorimeter.
    Generates realistic energy depositions (dE/dx) following a Landau distribution.
    """
    def do_starting(self, payload: str):
        super().do_starting(payload)
        self.log.info(f"Calorimeter initialized with {self._channels} channels")

    def generate_physics_event(self) -> bytes:
        payload = bytearray()
        
        # Determine if it's an electron (high shower) or pion (MIP)
        is_electron = np.random.rand() > 0.5
        
        for ch in range(self._channels):
            # If electron, deposits lots of energy (Electromagnetic Shower)
            if is_electron:
                amp = int(np.clip(np.random.normal(3000, 500), 0, 65535))
            else:
                # If pion, deposits Minimum Ionizing Particle (MIP) energy (Landau peak)
                amp = int(np.clip(np.random.gamma(shape=2.0, scale=100.0), 0, 65535))
                
            n_hits = np.random.poisson(2)
            time_val = float(np.random.normal(15.0, 2.0))
            
            # Format: <H B x f -> 8 bytes per channel
            channel_data = struct.pack('<H B x f', amp, n_hits, time_val)
            payload.extend(channel_data)
            
        return bytes(payload)

    def decode_event_for_kafka(self, raw_bytes: bytes) -> list:
        """Decode calorimeter data into per-channel energy readings."""
        import bl4s_events_pb2
        events = []
        ch_size = 8
        num_channels = len(raw_bytes) // ch_size
        for ch in range(num_channels):
            chunk = raw_bytes[ch * ch_size : (ch + 1) * ch_size]
            amp, n_hits, time_val = struct.unpack('<H B x f', chunk)
            
            event = bl4s_events_pb2.BL4SEvent(sat="Calorimeter")
            event.calorimeter.ch = ch
            event.calorimeter.energy = float(amp)
            event.calorimeter.n_hits = int(n_hits)
            event.calorimeter.time = float(time_val)
            events.append(event)
            
        return events

def main(args=None):
    from constellation.core.satellite import SatelliteArgumentParser
    from constellation.core.logging import setup_cli_logging
    parser = SatelliteArgumentParser(description="BL4S Calorimeter Satellite")
    args = vars(parser.parse_args(args))
    setup_cli_logging(args.pop("level"))
    data_port = args.pop("data_port", 0)
    s = CalorimeterSatellite(data_port, **args)
    s.run_satellite()

if __name__ == "__main__":
    main()
