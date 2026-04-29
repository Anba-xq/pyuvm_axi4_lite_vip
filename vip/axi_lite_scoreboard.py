from pyuvm import *

class AxiScoreboard(uvm_scoreboard):
    def build_phase(self):
        super().build_phase()
        self.fifo = uvm_tlm_analysis_fifo("scb_fifo", self)
        self.memory_map = ConfigDB().get(self, "", "GLOBAL_REG_MAP")

        if self.memory_map is None:
            self.logger.error("Scoreboard 未能获取到 GLOBAL_REG_MAP！")
            self.memory_map = {}

    async def run_phase(self):
        for addr, val in self.memory_map.items():
            self.logger.debug(f"寄存器加载: 地址 {hex(addr)} -> 复位值 {hex(val)}")
        while True:
            item = await self.fifo.get()
            aligned_addr = item.addr & 0xFFFFFFFC
            if item.is_write:
                self.memory_map[aligned_addr] = item.data
                self.logger.info(f"💾 [SCB] 记录写入 -> 寄存器 {hex(item.addr)}(映射到物理地址 {hex(aligned_addr)}) 更新为 {hex(item.data)}")
            else:
                expected = self.memory_map.get(aligned_addr, 0)
                if item.data == expected:
                    self.logger.info(f"✅ [SCB] 比对成功! 地址 {hex(aligned_addr)}: 期望={hex(expected)}, 实际={hex(item.data)}")
                else:
                    self.logger.error(f"❌ [SCB] 比对失败! 地址 {hex(aligned_addr)}: 期望={hex(expected)}, 实际={hex(item.data)}")
