import struct
import numpy as np
import time
from Geant4ReplaySatellite import Geant4ReplaySatellite

class DWCSatellite(Geant4ReplaySatellite):
    """
    Simulates a Delay Wire Chamber (DWC) tracking detector.
    Measures beam position (X, Y) via wire delay time differences (t_left, t_right, t_up, t_down).
    """
    def do_starting(self, payload: str):
        super().do_starting(payload)
        self.log.info("DWC Tracking Satellite initialized (100x100mm active area)")

    def generate_physics_event(self) -> bytes:
        # Beam spot Gaussian centered at (0, 0) with 3.5mm spread
        x_mm = float(np.random.normal(0.5, 3.2))
        y_mm = float(np.random.normal(-0.3, 3.0))
        
        # Wire delay times in ns (drift velocity ~ 0.5 mm/ns, base delay ~ 100ns)
        v_drift = 0.5 # mm/ns
        t_left = float(100.0 + (50.0 + x_mm) / v_drift + np.random.normal(0, 0.2))
        t_right = float(100.0 + (50.0 - x_mm) / v_drift + np.random.normal(0, 0.2))
        t_up = float(100.0 + (50.0 + y_mm) / v_drift + np.random.normal(0, 0.2))
        t_down = float(100.0 + (50.0 - y_mm) / v_drift + np.random.normal(0, 0.2))
        
        # Pack as 6 floats: x_mm, y_mm, t_left, t_right, t_up, t_down -> 24 bytes
        return struct.pack('<6f', x_mm, y_mm, t_left, t_right, t_up, t_down)

    def decode_event_for_kafka(self, raw_bytes: bytes) -> list:
        """Decode DWC binary data for Kafka live streaming."""
        import bl4s_events_pb2
        events = []
        if len(raw_bytes) >= 24:
            x_mm, y_mm, t_left, t_right, t_up, t_down = struct.unpack('<6f', raw_bytes[:24])
            
            # Map into Protobuf Timepix/Tracker coordinates for high-precision streaming
            # Map -50..+50mm into 0..255 pixel space for unified tracking
            pixel_x = int(np.clip((x_mm + 50.0) * (255.0 / 100.0), 0, 255))
            pixel_y = int(np.clip((y_mm + 50.0) * (255.0 / 100.0), 0, 255))
            
            event = bl4s_events_pb2.BL4SEvent(sat="DWC")
            event.timepix.x = pixel_x
            event.timepix.y = pixel_y
            event.timepix.tot = float(t_left - t_right) # delta t_X
            event.timepix.toa = float(t_up - t_down)   # delta t_Y
            events.append(event)
            
        return events

def main(args=None):
    from constellation.core.satellite import SatelliteArgumentParser
    from constellation.core.logging import setup_cli_logging
    parser = SatelliteArgumentParser(description="BL4S DWC Tracking Satellite")
    args = vars(parser.parse_args(args))
    setup_cli_logging(args.pop("level"))
    data_port = args.pop("data_port", 0)
    s = DWCSatellite(data_port, **args)
    s.run_satellite()

if __name__ == "__main__":
    main()
