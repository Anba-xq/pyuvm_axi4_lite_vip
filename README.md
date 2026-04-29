# 🚀 PyUVM AXI4-Lite VIP (Verification IP)

基于 Python (Cocotb & PyUVM) 构建的轻量级、工业标准的 AXI4-Lite 总线验证 IP。

## ✨ 核心特性 (Key Features)

* **纯前门并发监听 (Pure Front-door Monitor)**：抛弃后门探针，采用 5 协程并发死循环，完美解耦 AXI 5 大独立通道，支持高度乱序和时差到达的 Transaction 抓取与组装。
* **极端场景注入 (Chaos & Error Injection)**：
  * **非对齐地址轰炸**：支持跨边界、非对齐的狂野地址寻址测试。
  * **反压测试 (Backpressure)**：Master 接收端支持随机 `READY` 信号撤销与延迟，模拟真实的 SoC 拥堵环境。
  * **乱序并发发送**：AW 与 W 通道支持随机时差（Delay）注入，打破信号完美同步，暴露状态机死角。
* **覆盖率闭环 (Coverage Closure)**：
  * 基于 Synopsys VCS / URGs 收集覆盖率。
  * 针对 AXI 强耦合握手信号及位宽截断导致的物理不可达死区 (Unreachable Bins)，提供标准 `.el` 豁免文件 (Waiver)，**实现 100% 有效覆盖率签核 (Sign-off)**。
* **数据驱动驱动架构**：通过 `ConfigDB` 全局共享 CSV 寄存器配置表，Reference Model 自动根据配置表动态生成期望值。

## 🛠️ 快速启动 (Quick Start)

### 依赖环境
* Python 3.8+
* Cocotb & PyUVM (`pip install cocotb pyuvm`)
* 仿真器：VCS / Questasim / Icarus Verilog (默认配置为 VCS)

### 运行测试与收集覆盖率
```bash
cd tb
make clean_all
make          # 运行 1000 笔随机压力测试
make cov      # 生成覆盖率 HTML 报告
