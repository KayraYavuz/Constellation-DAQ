import json
import time
import math
import random
import numpy as np
from typing import Dict, Any, List, Tuple

from constellation.core.satellite import Satellite
from constellation.core.configuration import Configuration

class PhysicsReconstructionSatellite(Satellite):
    """
    Real-Time Physics Reconstruction Satellite.
    Performs online sub-millisecond physics reconstruction:
    1. Pi0 -> Gamma Gamma Invariant Mass Reconstruction (M_inv = sqrt(2*E1*E2*(1 - cos theta)))
    2. Multi-Plane 3D Tracking (DWC1 -> DWC2 -> Timepix) & Momentum Estimation
    """
    def do_initializing(self, config: Configuration) -> None:
        self._rate = config.get_float("rate", default_value=50.0)
        self._target_to_calo_dist_mm = config.get_float("target_to_calo_dist_mm", default_value=1500.0)
        self._calo_cell_pitch_mm = config.get_float("calo_cell_pitch_mm", default_value=30.0)
        self._magnetic_field_tesla = config.get_float("magnetic_field_tesla", default_value=0.5)
        self._magnet_length_m = config.get_float("magnet_length_m", default_value=0.4)
        
        self._total_reconstructed_events = 0
        self._pi0_candidates_found = 0
        
        self.log.info(f"PhysicsReconstructionSatellite initialized (L_calo={self._target_to_calo_dist_mm}mm, B={self._magnetic_field_tesla}T)")

        # Kafka Streaming
        self._kafka_producer = None
        self._kafka_topic = "bl4s_events"
        self._init_kafka()

    def _init_kafka(self):
        try:
            from kafka import KafkaProducer
            self._kafka_producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                request_timeout_ms=500,
                max_block_ms=200
            )
            self.log.info("Physics Reconstruction Kafka streaming ENABLED on localhost:9092")
        except Exception:
            self._kafka_producer = None

    def reconstruct_pi0_mass(self, matrix_4x4: np.ndarray) -> Dict[str, Any]:
        """
        Identifies two localized photon clusters in the 4x4 Lead Glass matrix
        and calculates the two-photon invariant mass M_gamma_gamma.
        """
        # Find 2 highest local maxima
        flat_indices = np.argsort(matrix_4x4.flatten())[::-1]
        c1_idx = flat_indices[0]
        c2_idx = flat_indices[1]
        
        r1, col1 = divmod(c1_idx, 4)
        r2, col2 = divmod(c2_idx, 4)
        
        # Convert matrix row/col to centered mm coordinates [-45, -15, +15, +45]
        x1_mm = (col1 - 1.5) * self._calo_cell_pitch_mm
        y1_mm = (r1 - 1.5) * self._calo_cell_pitch_mm
        e1_mev = float(matrix_4x4[r1, col1])
        
        x2_mm = (col2 - 1.5) * self._calo_cell_pitch_mm
        y2_mm = (r2 - 1.5) * self._calo_cell_pitch_mm
        e2_mev = float(matrix_4x4[r2, col2])
        
        L = self._target_to_calo_dist_mm
        
        # Vector lengths
        d1 = math.sqrt(x1_mm**2 + y1_mm**2 + L**2)
        d2 = math.sqrt(x2_mm**2 + y2_mm**2 + L**2)
        
        # Dot product for opening angle cos(theta)
        cos_theta = (x1_mm * x2_mm + y1_mm * y2_mm + L**2) / (d1 * d2)
        cos_theta = max(-1.0, min(1.0, cos_theta))
        opening_angle_deg = math.degrees(math.acos(cos_theta))
        
        # Invariant mass: M = sqrt(2 * E1 * E2 * (1 - cos(theta)))
        if e1_mev > 100.0 and e2_mev > 100.0 and (1.0 - cos_theta) > 0.0001:
            inv_mass_mev = math.sqrt(2.0 * e1_mev * e2_mev * (1.0 - cos_theta))
            is_valid_pi0 = 110.0 <= inv_mass_mev <= 160.0
        else:
            inv_mass_mev = 0.0
            is_valid_pi0 = False

        return {
            "cluster1": {"x_mm": round(x1_mm, 1), "y_mm": round(y1_mm, 1), "energy_mev": round(e1_mev, 1)},
            "cluster2": {"x_mm": round(x2_mm, 1), "y_mm": round(y2_mm, 1), "energy_mev": round(e2_mev, 1)},
            "opening_angle_deg": round(opening_angle_deg, 2),
            "invariant_mass_mev": round(inv_mass_mev, 1),
            "is_valid_pi0": is_valid_pi0
        }

    def reconstruct_3d_track(self, dwc1_pos: Tuple[float, float], dwc2_pos: Tuple[float, float], tpx_pos: Tuple[float, float]) -> Dict[str, Any]:
        """
        Fits 3D linear trajectory across tracking stations (z coordinates: DWC1=0mm, DWC2=1000mm, Timepix=2200mm).
        Calculates chi2, tracking residuals, and momentum deflection.
        """
        z_coords = np.array([0.0, 1000.0, 2200.0]) # mm
        x_coords = np.array([dwc1_pos[0], dwc2_pos[0], tpx_pos[0]])
        y_coords = np.array([dwc1_pos[1], dwc2_pos[1], tpx_pos[1]])
        
        # 1D Linear regression for X and Y
        slope_x, intercept_x = np.polyfit(z_coords, x_coords, 1)
        slope_y, intercept_y = np.polyfit(z_coords, y_coords, 1)
        
        # Residuals
        fit_x = slope_x * z_coords + intercept_x
        fit_y = slope_y * z_coords + intercept_y
        res_x = x_coords - fit_x
        res_y = y_coords - fit_y
        
        chi2_x = float(np.sum(res_x**2))
        chi2_y = float(np.sum(res_y**2))
        chi2_ndf = round((chi2_x + chi2_y) / 2.0, 3)
        
        # Deflection in magnet
        deflection_rad = math.atan(slope_x)
        # Momentum estimation p = (0.3 * B * L) / sin(theta) (GeV/c)
        if abs(deflection_rad) > 0.005 and self._magnetic_field_tesla > 0:
            momentum_gev = (0.3 * self._magnetic_field_tesla * self._magnet_length_m) / abs(math.sin(deflection_rad))
            momentum_gev = round(min(10.0, momentum_gev), 2)
        else:
            momentum_gev = 2.0 # Default nominal beam momentum

        return {
            "slope_x_mrad": round(slope_x * 1000.0, 2),
            "slope_y_mrad": round(slope_y * 1000.0, 2),
            "intercept_x_mm": round(intercept_x, 2),
            "intercept_y_mm": round(intercept_y, 2),
            "residual_timepix_x_um": round(float(res_x[2]) * 1000.0, 1),
            "residual_timepix_y_um": round(float(res_y[2]) * 1000.0, 1),
            "chi2_ndf": chi2_ndf,
            "estimated_momentum_gev": momentum_gev,
            "track_points": [
                {"station": "DWC1", "z_mm": 0, "x_mm": round(float(x_coords[0]), 2), "y_mm": round(float(y_coords[0]), 2)},
                {"station": "DWC2", "z_mm": 1000, "x_mm": round(float(x_coords[1]), 2), "y_mm": round(float(y_coords[1]), 2)},
                {"station": "Timepix", "z_mm": 2200, "x_mm": round(float(x_coords[2]), 2), "y_mm": round(float(y_coords[2]), 2)},
            ]
        }

    def do_run(self) -> str:
        event_id = 0
        
        while not self.stop_requested():
            event_id += 1
            self._total_reconstructed_events += 1
            
            # Simulate realistic calorimeter matrix (4x4)
            matrix = np.zeros((4, 4))
            is_pi0 = random.random() < 0.40
            
            if is_pi0:
                self._pi0_candidates_found += 1
                # Dual photon shower: pi0 invariant mass ~ 135.0 MeV
                # E1 ~ 1200 MeV, E2 ~ 1150 MeV, separation ~ 60 mm at L=1500 mm => theta ~ 40 mrad
                # M = sqrt(2 * 1200 * 1150 * (1 - cos(0.040))) ~= 135 MeV
                r1, c1 = random.randint(0, 1), random.randint(0, 1)
                r2, c2 = random.randint(2, 3), random.randint(2, 3)
                matrix[r1, c1] = np.random.normal(1200, 70)
                matrix[r2, c2] = np.random.normal(1150, 65)
                # Shower tails
                matrix += np.random.exponential(25, size=(4, 4))
            else:
                # Single charged particle (electron/muon/pion)
                r, c = random.randint(1, 2), random.randint(1, 2)
                matrix[r, c] = np.random.normal(1800, 200)
                matrix += np.random.exponential(15, size=(4, 4))

            # Simulate tracking station hits
            beam_x = np.random.normal(0.0, 3.5)
            beam_y = np.random.normal(0.0, 3.0)
            angle_x = np.random.normal(0.002, 0.001)
            angle_y = np.random.normal(0.001, 0.001)
            
            dwc1 = (beam_x + np.random.normal(0, 0.15), beam_y + np.random.normal(0, 0.15))
            dwc2 = (beam_x + 1000.0 * angle_x + np.random.normal(0, 0.15), beam_y + 1000.0 * angle_y + np.random.normal(0, 0.15))
            tpx  = (beam_x + 2200.0 * angle_x + np.random.normal(0, 0.05), beam_y + 2200.0 * angle_y + np.random.normal(0, 0.05))

            pi0_recon = self.reconstruct_pi0_mass(matrix)
            track_recon = self.reconstruct_3d_track(dwc1, dwc2, tpx)

            recon_payload = {
                "sat": "PhysicsReconstruction",
                "event_id": event_id,
                "timestamp": time.time(),
                "pi0_reconstruction": pi0_recon,
                "track_reconstruction": track_recon,
                "total_events_processed": self._total_reconstructed_events,
                "pi0_candidates_found": self._pi0_candidates_found
            }

            if self._kafka_producer:
                try:
                    self._kafka_producer.send(self._kafka_topic, value=recon_payload)
                except Exception:
                    pass

            time.sleep(1.0 / self._rate)

        return "Finished run"

def main(args=None):
    from constellation.core.satellite import SatelliteArgumentParser
    from constellation.core.logging import setup_cli_logging
    parser = SatelliteArgumentParser(description="Physics Reconstruction Satellite")
    args = vars(parser.parse_args(args))
    setup_cli_logging(args.pop("level"))
    name = args.pop("name", "PhysicsReconstruction")
    s = PhysicsReconstructionSatellite(name, **args)
    s.run_satellite()

if __name__ == "__main__":
    main()
