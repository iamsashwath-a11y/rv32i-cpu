import random
import cocotb
from cocotb.triggers import Timer

IMM_I, IMM_S, IMM_B, IMM_U, IMM_J = 0, 1, 2, 3, 4
MASK32 = 0xFFFF_FFFF


def sext(val, bits):
    val &= (1 << bits) - 1
    if val & (1 << (bits - 1)):
        val -= 1 << bits
    return val & MASK32


def golden_imm(inst, itype):
    if itype == IMM_I:
        return sext(inst >> 20, 12)
    if itype == IMM_S:
        imm = ((inst >> 25) << 5) | ((inst >> 7) & 0x1F)
        return sext(imm, 12)
    if itype == IMM_B:
        imm = (((inst >> 31) & 1) << 12) | (((inst >> 7) & 1) << 11) \
            | (((inst >> 25) & 0x3F) << 5) | (((inst >> 8) & 0xF) << 1)
        return sext(imm, 13)
    if itype == IMM_U:
        return inst & 0xFFFFF000
    if itype == IMM_J:
        imm = (((inst >> 31) & 1) << 20) | (((inst >> 12) & 0xFF) << 12) \
            | (((inst >> 20) & 1) << 11) | (((inst >> 21) & 0x3FF) << 1)
        return sext(imm, 21)


async def check(dut, inst, itype, label):
    dut.inst.value = inst & MASK32
    dut.imm_type.value = itype
    await Timer(1, unit="ns")
    got = int(dut.imm_out.value)
    exp = golden_imm(inst, itype)
    assert got == exp, f"{label}: got {got:#x}, expected {exp:#x}"


@cocotb.test()
async def test_worked_examples(dut):
    await check(dut, 0b000000001010_00000_000_00101_0010011, IMM_I, "addi imm=10")
    await check(dut, 0b0000000_00101_00110_010_01000_0100011, IMM_S, "sw imm=8")
    await check(dut, 0b1_111111_00010_00001_000_1100_1_1100011, IMM_B, "beq imm=-8")
    await check(dut, (0x12345 << 12) | (5 << 7) | 0b0110111, IMM_U, "lui imm=0x12345000")
    await check(dut, 0b0_0000001000_0_00000000_00001_1101111, IMM_J, "jal imm=16")


@cocotb.test()
async def test_random(dut):
    random.seed(6004)
    for _ in range(500):
        inst = random.randint(0, MASK32)
        itype = random.choice([IMM_I, IMM_S, IMM_B, IMM_U, IMM_J])
        await check(dut, inst, itype, "random")
