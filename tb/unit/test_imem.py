import cocotb
from cocotb.triggers import Timer

OPC_OP_IMM = 0b0010011
OPC_OP     = 0b0110011


def encode_r(funct7, rs2, rs1, funct3, rd, opcode):
    return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode


def encode_i(imm12, rs1, funct3, rd, opcode):
    return ((imm12 & 0xFFF) << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode


EXPECTED_PROGRAM = [
    encode_i(5, 0, 0b000, 1, OPC_OP_IMM),               # addi x1, x0, 5
    encode_i(10, 0, 0b000, 2, OPC_OP_IMM),               # addi x2, x0, 10
    encode_r(0b0000000, 2, 1, 0b000, 3, OPC_OP),         # add  x3, x1, x2
    encode_r(0b0100000, 1, 3, 0b000, 4, OPC_OP),         # sub  x4, x3, x1
]
NOP = 0x0000_0013


async def read(dut, pc):
    dut.pc.value = pc
    await Timer(1, unit="ns")
    return int(dut.instruction.value)


@cocotb.test()
async def test_program_contents(dut):
    """Check each hardcoded instruction against a correctly-computed encoding."""
    for i, expected in enumerate(EXPECTED_PROGRAM):
        pc = i * 4
        got = await read(dut, pc)
        assert got == expected, (
            f"instr_mem[{i}] (pc={pc:#x}): got {got:#010x}, expected {expected:#010x}"
        )


@cocotb.test()
async def test_nop_fill(dut):
    """Everything past the 4-instruction program should read back as NOP."""
    for i in [4, 5, 10, 255]:
        got = await read(dut, i * 4)
        assert got == NOP, f"instr_mem[{i}]: expected NOP {NOP:#010x}, got {got:#010x}"


@cocotb.test()
async def test_byte_to_word_addressing(dut):
    """pc is a byte address; instruction[1] should show up at pc=4, not pc=1."""
    got_at_4 = await read(dut, 4)
    assert got_at_4 == EXPECTED_PROGRAM[1], (
        f"pc=4 should read instr_mem[1], got {got_at_4:#010x}, expected {EXPECTED_PROGRAM[1]:#010x}"
    )
