import random

import cocotb
from cocotb.triggers import Timer

ALU_ADD, ALU_SUB, ALU_SLL, ALU_SLT, ALU_SLTU = 0, 1, 2, 3, 4
ALU_XOR, ALU_SRL, ALU_SRA, ALU_OR, ALU_AND = 5, 6, 7, 8, 9

MASK32 = 0xFFFF_FFFF


def to_signed(x, bits=32):
    x &= (1 << bits) - 1
    if x & (1 << (bits - 1)):
        x -= 1 << bits
    return x


def golden_alu(a, b, op):
    a &= MASK32
    b &= MASK32
    shamt = b & 0x1F
    if op == ALU_ADD:
        return (a + b) & MASK32
    if op == ALU_SUB:
        return (a - b) & MASK32
    if op == ALU_SLL:
        return (a << shamt) & MASK32
    if op == ALU_SLT:
        return 1 if to_signed(a) < to_signed(b) else 0
    if op == ALU_SLTU:
        return 1 if a < b else 0
    if op == ALU_XOR:
        return a ^ b
    if op == ALU_SRL:
        return (a & MASK32) >> shamt
    if op == ALU_SRA:
        return (to_signed(a) >> shamt) & MASK32
    if op == ALU_OR:
        return a | b
    if op == ALU_AND:
        return a & b
    return 0


async def check(dut, a, b, op, label=""):
    dut.a.value = a & MASK32
    dut.b.value = b & MASK32
    dut.alu_op.value = op
    await Timer(1, unit="ns")
    expected = golden_alu(a, b, op)
    got = int(dut.result.value)
    assert got == expected, (
        f"{label} a={a:#x} b={b:#x} op={op} -> got {got:#x}, expected {expected:#x}"
    )
    assert int(dut.zero.value) == (1 if expected == 0 else 0), f"{label} zero flag mismatch"


@cocotb.test()
async def test_alu_directed(dut):
    cases = [
        (0x7FFFFFFF, 1, ALU_ADD, "signed overflow"),
        (0x80000000, 0xFFFFFFFF, ALU_ADD, "unsigned wrap"),
        (0, 0, ALU_SUB, "zero result -> zero flag"),
        (0x80000000, 1, ALU_SLT, "min negative vs positive"),
        (1, 0x80000000, ALU_SLTU, "small vs huge unsigned"),
        (0xFFFFFFFF, 0, ALU_SLL, "shift by 0"),
        (1, 31, ALU_SLL, "shift by 31"),
        (0x80000000, 31, ALU_SRA, "arithmetic shift sign extend"),
        (0x80000000, 31, ALU_SRL, "logical shift no sign extend"),
    ]
    for a, b, op, label in cases:
        await check(dut, a, b, op, label)


@cocotb.test()
async def test_alu_random(dut):
    random.seed(6004)
    ops = [ALU_ADD, ALU_SUB, ALU_SLL, ALU_SLT, ALU_SLTU,
           ALU_XOR, ALU_SRL, ALU_SRA, ALU_OR, ALU_AND]
    for _ in range(500):
        a = random.randint(0, MASK32)
        b = random.randint(0, MASK32)
        op = random.choice(ops)
        await check(dut, a, b, op, "random")
