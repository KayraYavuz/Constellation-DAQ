import struct
import numpy as np
from Geant4ReplaySatellite import Geant4ReplaySatellite

class CherenkovSatellite(Geant4ReplaySatellite):
    """
    Simulates a Threshold Cherenkov Counter for PID.
    Outputs a QDC amplitude value. Electrons produce high values, pions produce pedestal noise.
    """
    def do_starting(self, payload: str):
        super().do_starting(payload)
        self.log.info("Cherenkov PID detector initialized")

    def generate_physics_event(self) -> bytes:
        # Assuming a mixed beam of electrons and pions.
        is_electron = np.random.rand() > 0.5
        
        if is_electron:
            qdc_val = int(np.random.normal(3000, 400))
        else:
            qdc_val = int(np.random.normal(150, 30))
            
        hit_data = struct.pack('<H', np.clip(qdc_val, 0, 65535))
        return hit_data

    def decode_event_for_kafka(self, raw_bytes: bytes) -> list:
        """Decode Cherenkov QDC value for live PID spectrum."""
        import bl4s_events_pb2
        event = bl4s_events_pb2.BL4SEvent(sat="Cherenkov")
        if len(raw_bytes) >= 2:
            qdc_val = struct.unpack('<H', raw_bytes[:2])[0]
            event.cherenkov.qdc = float(qdc_val)
        else:
            event.cherenkov.qdc = 0.0
        return [event]

def main(args=None):
    from constellation.core.satellite import SatelliteArgumentParser
    from constellation.core.logging import setup_cli_logging
    parser = SatelliteArgumentParser(description="BL4S Cherenkov Satellite")
    args = vars(parser.parse_args(args))
    setup_cli_logging(args.pop("level"))
    data_port = args.pop("data_port", 0)
    s = CherenkovSatellite(data_port, **args)
    s.run_satellite()

if __name__ == "__main__":
    main()
