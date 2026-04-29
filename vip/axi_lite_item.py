from pyuvm import *

class AxiLiteItem(uvm_sequence_item):
    def __init__(self, name, addr=0, data=0, is_write=True):
        super().__init__(name)
        self.addr = addr
        self.data = data
        self.strb = 0xF
        self.is_write = is_write
        self.resp = 0