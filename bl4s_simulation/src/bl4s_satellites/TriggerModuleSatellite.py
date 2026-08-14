import random
import time
from typing import Any

from constellation.core.satellite import Satellite
from constellation.core.configuration import Configuration

class TriggerModuleSatellite(Satellite):
    """
    Python implementation of TriggerModuleSatellite
    It uses telemetry (STAT) to send software trigger IDs.
    """
    def do_initializing(self, config: Configuration) -> None:
        self.trigger_id = 0
        # register_metric is not natively available via self in Satellite base class, 
        # but we can use self._mnt if we need to register it.
        # Actually in Python constellation, calling self.stat() dynamically registers if needed,
        # but to be explicit we can register via monitoring manager:
        if hasattr(self, "_mnt") and self._mnt:
            self._mnt.register_metric("SWTRIG", "", "Software trigger signal, carries the trigger ID")
        self.log.info("TriggerModuleSatellite initialized")

    def do_starting(self, run_identifier: str) -> str:
        self.trigger_id = 0
        self.log.info("TriggerModuleSatellite starting")
        return "Starting"

    def poll_register(self) -> bool:
        # Bernoulli distribution with 0.000001 probability roughly
        return random.random() < 0.000001

    def do_run(self) -> str:
        while not self.stop_requested():
            if self.poll_register():
                self.trigger_id += 1
                self.stat("SWTRIG", self.trigger_id)
                self.log.debug(f"Sent software trigger with ID {self.trigger_id}")
            time.sleep(0.0001)  # tiny sleep to prevent burning 100% CPU on this while loop
        return "Finished run"

def main(args=None):
    from constellation.core.satellite import SatelliteArgumentParser
    from constellation.core.logging import setup_cli_logging
    parser = SatelliteArgumentParser(description="Trigger Module Satellite")
    args = vars(parser.parse_args(args))
    setup_cli_logging(args.pop("level"))
    # Satellite takes name and other kwargs
    name = args.pop("name", "TriggerModule")
    s = TriggerModuleSatellite(name, **args)
    s.run_satellite()

if __name__ == "__main__":
    main()
