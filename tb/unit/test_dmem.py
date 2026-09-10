import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

MASK32 = 0xFFFF_FFFF


async def start_clock(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.addr.value = 0
    dut.write_data.value = 0
    dut.mem_read.value = 0
    dut.mem_write.value = 0
    await RisingEdge(dut.clk)


@cocotb.test()
async def test_write_then_read(dut):
    await start_clock(dut)

    dut.addr.value = 0
    dut.write_data.value = 0xCAFEBABE
    dut.mem_write.value = 1
    await RisingEdge(dut.clk)
    dut.mem_write.value = 0

    dut.mem_read.value = 1
    await Timer(1, unit="ns")
    got = int(dut.read_data.value)
    assert got == 0xCAFEBABE, f"expected 0xCAFEBABE, got {got:#010x}"


@cocotb.test()
async def test_read_gated_by_mem_read(dut):
    """read_data should be 0 when mem_read is low, even at a written address."""
    await start_clock(dut)

    dut.addr.value = 4
    dut.write_data.value = 0x11112222
    dut.mem_write.value = 1
    await RisingEdge(dut.clk)
    dut.mem_write.value = 0

    dut.mem_read.value = 0
    await Timer(1, unit="ns")
    got = int(dut.read_data.value)
    assert got == 0, f"expected 0 when mem_read=0, got {got:#010x}"

    dut.mem_read.value = 1
    await Timer(1, unit="ns")
    got = int(dut.read_data.value)
    assert got == 0x11112222, f"expected 0x11112222 when mem_read=1, got {got:#010x}"


@cocotb.test()
async def test_random_addresses(dut):
    random.seed(6004)
    await start_clock(dut)

    written = {}
    for _ in range(50):
        word_idx = random.randint(0, 255)
        addr = word_idx * 4
        data = random.randint(0, MASK32)
        dut.addr.value = addr
        dut.write_data.value = data
        dut.mem_write.value = 1
        await RisingEdge(dut.clk)
        dut.mem_write.value = 0
        written[addr] = data

    for addr, expected in written.items():
        dut.addr.value = addr
        dut.mem_read.value = 1
        await Timer(1, unit="ns")
        got = int(dut.read_data.value)
        assert got == expected, f"addr {addr:#x}: got {got:#010x}, expected {expected:#010x}"
