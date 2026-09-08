import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

MASK32 = 0xFFFF_FFFF


@cocotb.test()
async def test_reset(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.reset.value = 1
    dut.pc_next.value = 0xDEAD_BEEF  # should be ignored while reset is high
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    assert int(dut.pc_out.value) == 0, f"expected pc_out=0 after reset, got {int(dut.pc_out.value):#x}"


@cocotb.test()
async def test_sequential_update(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.reset.value = 1
    dut.pc_next.value = 0
    await RisingEdge(dut.clk)
    dut.reset.value = 0

    pc = 0
    for i in range(20):
        next_pc = (pc + 4) & MASK32
        dut.pc_next.value = next_pc
        await RisingEdge(dut.clk)
        await Timer(1, unit="ns")
        got = int(dut.pc_out.value)
        assert got == next_pc, f"iter {i}: expected pc_out={next_pc:#x}, got {got:#x}"
        pc = next_pc


@cocotb.test()
async def test_reset_mid_stream(dut):
    """Reset asserted after PC has already advanced should still snap back to 0."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.reset.value = 1
    dut.pc_next.value = 0
    await RisingEdge(dut.clk)
    dut.reset.value = 0

    for pc_val in [4, 8, 12]:
        dut.pc_next.value = pc_val
        await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    assert int(dut.pc_out.value) == 12

    dut.reset.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    assert int(dut.pc_out.value) == 0, "reset mid-stream did not snap pc_out back to 0"
