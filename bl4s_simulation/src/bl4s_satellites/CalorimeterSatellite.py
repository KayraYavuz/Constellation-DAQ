import struct
import numpy as np
import time
from Geant4ReplaySatellite import Geant4ReplaySatellite

class CalorimeterSatellite(Geant4ReplaySatellite):
    """
    Simulates the 16-channel (4x4) Lead Glass Electromagnetic Calorimeter
    for the BL4S 2026 Team PionIST 3 Experiment: Neutral Pion (pi0 -> gamma gamma) Decay.
    """
    def do_starting(self, payload: str):
        super().do_starting(payload)
        self.log.info(f"PionIST 3 Lead Glass Calorimeter initialized with {self._channels} channels")

    def generate_physics_event(self) -> bytes:
        payload = bytearray()
        
        # 70% Neutral Pion decay (pi0 -> gamma + gamma), 30% background/charged MIP
        is_pi0 = np.random.rand() > 0.30
        
        # 16-channel energy distribution array
        energies = np.zeros(16, dtype=np.float64)
        
        if is_pi0:
            # pi0 kinematics in lab frame (E_pi0 ~ 1.5 - 4.0 GeV)
            e_pi0 = np.random.uniform(1800, 3800) # MeV
            # Energy sharing asymmetry z = E1 / (E1 + E2)
            z = np.random.uniform(0.35, 0.65)
            e1 = e_pi0 * z
            e2 = e_pi0 * (1.0 - z)
            
            # Photon 1 cluster center in 4x4 matrix
            r1, c1 = np.random.choice([0, 1]), np.random.choice([0, 1, 2, 3])
            # Photon 2 cluster center (separated by opening angle)
            r2, c2 = np.random.choice([2, 3]), np.random.choice([0, 1, 2, 3])
            
            # Deposit Photon 1 energy with lateral shower spread
            for r in range(4):
                for c in range(4):
                    dist_sq = (r - r1)**2 + (c - c1)**2
                    frac = np.exp(-dist_sq / 0.8)
                    energies[r * 4 + c] += (e1 / 0.085) * frac * np.random.normal(1.0, 0.05)
                    
            # Deposit Photon 2 energy with lateral shower spread
            for r in range(4):
                for c in range(4):
                    dist_sq = (r - r2)**2 + (c - c2)**2
                    frac = np.exp(-dist_sq / 0.8)
                    energies[r * 4 + c] += (e2 / 0.085) * frac * np.random.normal(1.0, 0.05)
        else:
            # Charged Pion (MIP) passing through a single crystal
            ch_hit = np.random.randint(0, 16)
            energies[ch_hit] = np.random.gamma(shape=2.5, scale=120.0)
            
        # Add baseline pedestal noise
        for ch in range(self._channels):
            amp = int(np.clip(energies[ch] + np.random.normal(100, 8), 0, 65535))
            n_hits = np.random.poisson(3 if amp > 500 else 1)
            time_val = float(np.random.normal(15.2, 0.8))
            
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
    parser = SatelliteArgumentParser(description="BL4S PionIST 3 Calorimeter Satellite")
    args = vars(parser.parse_args(args))
    setup_cli_logging(args.pop("level"))
    data_port = args.pop("data_port", 0)
    s = CalorimeterSatellite(data_port, **args)
    s.run_satellite()

if __name__ == "__main__":
    main()
