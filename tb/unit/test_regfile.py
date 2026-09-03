import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

MASK32 = 0xFFFF_FFFF


class GoldenRegfile:
    def __init__(self):
        self.regs = [0] * 32

    def read(self, addr):
        return 0 if addr == 0 else self.regs[addr]

    def write(self, addr, data):
        if addr != 0:
            self.regs[addr] = data & MASK32


async def start_clock(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.we.value = 0
    dut.rs1_addr.value = 0
    dut.rs2_addr.value = 0
    dut.rd_addr.value = 0
    dut.rd_data.value = 0
    await RisingEdge(dut.clk)


def check_reads(dut, golden, rs1_addr, rs2_addr, label=""):
    got1 = int(dut.rs1_data.value)
    got2 = int(dut.rs2_data.value)
    exp1 = golden.read(rs1_addr)
    exp2 = golden.read(rs2_addr)
    assert got1 == exp1, f"{label} rs1_data (addr {rs1_addr}): got {got1:#x}, expected {exp1:#x}"
    assert got2 == exp2, f"{label} rs2_data (addr {rs2_addr}): got {got2:#x}, expected {exp2:#x}"


@cocotb.test()
async def test_x0_hardwired_zero(dut):
    golden = GoldenRegfile()
    await start_clock(dut)

    dut.we.value = 1
    dut.rd_addr.value = 0
    dut.rd_data.value = 0xDEADBEEF
    dut.rs1_addr.value = 0
    dut.rs2_addr.value = 0
    await Timer(1, unit="ns")
    check_reads(dut, golden, 0, 0, "x0 write-attempt, same-cycle read")

    await RisingEdge(dut.clk)
    dut.we.value = 0
    await Timer(1, unit="ns")
    check_reads(dut, golden, 0, 0, "x0 read after clock edge")


@cocotb.test()
async def test_same_cycle_bypass(dut):
    golden = GoldenRegfile()
    await start_clock(dut)

    dut.we.value = 1
    dut.rd_addr.value = 5
    dut.rd_data.value = 0x1111_1111
    dut.rs1_addr.value = 5
    dut.rs2_addr.value = 5
    golden.write(5, 0x1111_1111)
    await RisingEdge(dut.clk)
    dut.we.value = 0
    await Timer(1, unit="ns")
    check_reads(dut, golden, 5, 5, "priming x5")

    dut.we.value = 1
    dut.rd_addr.value = 5
    dut.rd_data.value = 0x2222_2222
    dut.rs1_addr.value = 5
    dut.rs2_addr.value = 5
    await Timer(1, unit="ns")
    got = int(dut.rs1_data.value)
    assert got == 0x2222_2222, (
        f"same-cycle bypass failed: got {got:#x}, expected 0x22222222"
    )

    await RisingEdge(dut.clk)
    dut.we.value = 0
    golden.write(5, 0x2222_2222)
    await Timer(1, unit="ns")
    check_reads(dut, golden, 5, 5, "x5 after the write has landed")


@cocotb.test()
async def test_random_read_write(dut):
    random.seed(6004)
    golden = GoldenRegfile()
    await start_clock(dut)

    for addr in range(32):
        val = random.randint(0, MASK32)
        dut.we.value = 1
        dut.rd_addr.value = addr
        dut.rd_data.value = val
        dut.rs1_addr.value = 0
        dut.rs2_addr.value = 0
        await RisingEdge(dut.clk)
        golden.write(addr, val)
    dut.we.value = 0
    await RisingEdge(dut.clk)

    for i in range(300):
        we = random.random() < 0.7
        rd_addr = random.randint(0, 31)
        rd_data = random.randint(0, MASK32)

        if random.random() < 0.3:
            rs1_addr = rd_addr
        else:
            rs1_addr = random.randint(0, 31)
        if random.random() < 0.3:
            rs2_addr = rd_addr
        else:
            rs2_addr = random.randint(0, 31)

        dut.we.value = 1 if we else 0
        dut.rd_addr.value = rd_addr
        dut.rd_data.value = rd_data
        dut.rs1_addr.value = rs1_addr
        dut.rs2_addr.value = rs2_addr

        await Timer(1, unit="ns")

        def expect(addr):
            if we and addr == rd_addr and addr != 0:
                return rd_data & MASK32
            return golden.read(addr)

        got1 = int(dut.rs1_data.value)
        got2 = int(dut.rs2_data.value)
        assert got1 == expect(rs1_addr), (
            f"iter {i}: rs1 (addr {rs1_addr}) got {got1:#x}, expected {expect(rs1_addr):#x}"
        )
        assert got2 == expect(rs2_addr), (
            f"iter {i}: rs2 (addr {rs2_addr}) got {got2:#x}, expected {expect(rs2_addr):#x}"
        )

        await RisingEdge(dut.clk)
        if we:
            golden.write(rd_addr, rd_data)
