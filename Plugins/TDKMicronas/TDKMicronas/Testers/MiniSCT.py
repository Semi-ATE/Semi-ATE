
from TDKMicronas.Testers.InterfaceSCT import InterfaceSCT


class MiniSCT(InterfaceSCT):
    def pulse_trigger_out(self, pulse_width_ms):
        # ToDo: Implement with actual hardware.
        print(f"MiniSCT: Pulse Trigger Out")

    def get_sites_count(self):
        return 1
