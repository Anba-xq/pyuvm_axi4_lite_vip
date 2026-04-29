import cocotb
from pyuvm import *
from cocotb.triggers import RisingEdge, ReadOnly
from .axi_lite_item import AxiLiteItem  # 导入刚才定义的 Item

class AxiLiteMonitor(uvm_monitor):
    def build_phase(self):
        super().build_phase()
        self.dut = ConfigDB().get(self,"","DUT")
        self.ap = uvm_analysis_port("mon_ap",self)
        self.aw_queue = []
        self.w_queue  = []
        self.ar_queue = []

    async def run_phase(self):
        cocotb.start_soon(self.monitor_aw_channel())
        cocotb.start_soon(self.monitor_w_channel())
        cocotb.start_soon(self.monitor_b_channel())
        cocotb.start_soon(self.monitor_ar_channel())
        cocotb.start_soon(self.monitor_r_channel())

    async def monitor_aw_channel(self):
        while True:
            await ReadOnly()
            if self.dut.S_AXI_AWVALID.value == 1 and self.dut.S_AXI_AWREADY.value == 1:
                addr = int(self.dut.S_AXI_AWADDR.value)
                self.aw_queue.append(addr)
                self.logger.info(f"[MON-AW] 抓取写地址：{hex(addr)}")
            await RisingEdge(self.dut.S_AXI_ACLK)

    async def monitor_w_channel(self):
        while True:
            await ReadOnly()
            if self.dut.S_AXI_WVALID.value == 1 and self.dut.S_AXI_WREADY.value == 1:
                data = int(self.dut.S_AXI_WDATA.value)
                self.w_queue.append(data)
                self.logger.debug(f"[MON-W] 抓取写数据: {hex(data)}")
            await RisingEdge(self.dut.S_AXI_ACLK)

    async def monitor_b_channel(self):
        while True:
            await ReadOnly()
            if self.dut.S_AXI_BVALID.value == 1 and self.dut.S_AXI_BREADY.value == 1:
                if len(self.aw_queue) > 0 and len(self.w_queue) > 0:
                    addr = self.aw_queue.pop(0)
                    data = self.w_queue.pop(0)
                    self.ap.write(AxiLiteItem("mon_wr", addr, data, is_write=True))
                else:
                    self.logger.error("❌ [MON-FATAL] B通道闭环，但地址或数据队列为空！总线时序发生严重错乱！")
            await RisingEdge(self.dut.S_AXI_ACLK)

    async def monitor_ar_channel(self):
        while True:
            await ReadOnly()
            if self.dut.S_AXI_ARVALID.value == 1 and self.dut.S_AXI_ARREADY.value == 1:
                addr = int(self.dut.S_AXI_ARADDR.value)
                self.ar_queue.append(addr)
                self.logger.debug(f"[MON-AR] 抓取读地址: {hex(addr)}")
            await RisingEdge(self.dut.S_AXI_ACLK)

    async def monitor_r_channel(self):
        while True:
            await ReadOnly()
            if self.dut.S_AXI_RVALID.value == 1 and self.dut.S_AXI_RREADY.value == 1:
                data = int(self.dut.S_AXI_RDATA.value)
                if len(self.ar_queue) > 0:
                    addr = self.ar_queue.pop(0)
                    self.ap.write(AxiLiteItem("mon_rd", addr, data, is_write=False))
                else:
                    self.logger.error("❌ [MON-FATAL] R通道收到数据，但读地址队列为空！")
            await RisingEdge(self.dut.S_AXI_ACLK)