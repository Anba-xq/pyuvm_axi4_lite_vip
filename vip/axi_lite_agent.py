from pyuvm import *
from .axi_lite_driver import AxiLiteMasterDriver
from .axi_lite_monitor import AxiLiteMonitor

class AxiLiteAgent(uvm_agent):
    def build_phase(self):
        super().build_phase()
        self.seqr = uvm_sequencer("seqr", self)
        self.drv = AxiLiteMasterDriver("drv", self)
        self.mon = AxiLiteMonitor("mon", self)

    def connect_phase(self):
        super().connect_phase()
        self.drv.seq_item_port.connect(self.seqr.seq_item_export)