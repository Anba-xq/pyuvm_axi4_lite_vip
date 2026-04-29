import cocotb
import random
from pyuvm import *
from cocotb.triggers import RisingEdge, ReadOnly, Combine, ClockCycles

class AxiLiteMasterDriver(uvm_driver):
    def build_phase(self):
        super().build_phase()
        self.dut = ConfigDB().get(self, "", "DUT")

    async def axi_send(self, valid_sig, ready_sig, data_sig_dict):
        for sig, val in data_sig_dict.items():
            sig.value = val
        valid_sig.value = 1

        while True:
            await ReadOnly()
            if ready_sig.value == 1:
                await RisingEdge(self.dut.S_AXI_ACLK)
                break
            await RisingEdge(self.dut.S_AXI_ACLK)
        valid_sig.value = 0

    async def axi_recv(self, valid_sig, ready_sig, extract_func=None):
        delay = random.randint(0, 5)
        if delay > 0:
            ready_sig.value = 0
            await ClockCycles(self.dut.S_AXI_ACLK, delay)
        ready_sig.value = 1

        while True:
            await ReadOnly()
            if valid_sig.value == 1:
                if extract_func:
                    extract_func()
                await RisingEdge(self.dut.S_AXI_ACLK)
                break
            await RisingEdge(self.dut.S_AXI_ACLK)
        ready_sig.value = 0

    async def write_transaction(self, item):
        self.logger.debug(f"📤 发起写请求 -> 地址: {hex(item.addr)}")
        delay_aw = random.randint(0, 3)
        delay_w = random.randint(0, 3)

        async def delayed_aw_send():
            if delay_aw > 0:
                await ClockCycles(self.dut.S_AXI_ACLK, delay_aw)
            await self.axi_send(self.dut.S_AXI_AWVALID, self.dut.S_AXI_AWREADY, {self.dut.S_AXI_AWADDR: item.addr})

        async def delayed_w_send():
            if delay_w > 0:
                await ClockCycles(self.dut.S_AXI_ACLK, delay_w)
            await self.axi_send(self.dut.S_AXI_WVALID, self.dut.S_AXI_WREADY,
                                {self.dut.S_AXI_WDATA: item.data, self.dut.S_AXI_WSTRB: item.strb})

        aw_task = cocotb.start_soon(delayed_aw_send())
        w_task = cocotb.start_soon(delayed_w_send())
        await Combine(aw_task, w_task)

        def extract_b():
            item.resp = int(self.dut.S_AXI_BRESP.value)
        await self.axi_recv(self.dut.S_AXI_BVALID, self.dut.S_AXI_BREADY, extract_b)

    async def read_transaction(self, item):
        self.logger.debug(f"📥 发起读请求 -> 地址: {hex(item.addr)}")
        await self.axi_send(self.dut.S_AXI_ARVALID, self.dut.S_AXI_ARREADY, {self.dut.S_AXI_ARADDR: item.addr})

        def extract_r():
            item.data = int(self.dut.S_AXI_RDATA.value)
            item.resp = int(self.dut.S_AXI_RRESP.value)
        await self.axi_recv(self.dut.S_AXI_RVALID, self.dut.S_AXI_RREADY, extract_r)

    async def run_phase(self):
        self.dut.S_AXI_AWVALID.value = 0
        self.dut.S_AXI_WVALID.value = 0
        self.dut.S_AXI_BREADY.value = 1
        self.dut.S_AXI_ARVALID.value = 0
        self.dut.S_AXI_RREADY.value = 1

        while True:
            item = await self.seq_item_port.get_next_item()
            if item.is_write:
                await self.write_transaction(item)
            else:
                await self.read_transaction(item)
            self.seq_item_port.item_done()