import cocotb
from cocotb.triggers import Timer

OPC_OP_IMM = 0b0010011
OPC_OP     = 0b0110011
OPC_LOAD   = 0b0000011
OPC_STORE  = 0b0100011
OPC_BRANCH = 0b1100011
OPC_JAL    = 0b1101111


def encode_r(funct7, rs2, rs1, funct3, rd, opcode):
    return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode


def encode_i(imm12, rs1, funct3, rd, opcode):
    return ((imm12 & 0xFFF) << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode


def encode_s(imm12, rs2, rs1, funct3, opcode):
    imm = imm12 & 0xFFF
    return ((imm >> 5) << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | ((imm & 0x1F) << 7) | opcode


def encode_b(imm, rs2, rs1, funct3, opcode):
    imm12 = (imm >> 12) & 1
    imm11 = (imm >> 11) & 1
    imm10_5 = (imm >> 5) & 0x3F
    imm4_1 = (imm >> 1) & 0xF
    return (imm12 << 31) | (imm10_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm4_1 << 8) | (imm11 << 7) | opcode


def encode_j(imm, rd, opcode):
    imm20 = (imm >> 20) & 1
    imm19_12 = (imm >> 12) & 0xFF
    imm11 = (imm >> 11) & 1
    imm10_1 = (imm >> 1) & 0x3FF
    return (imm20 << 31) | (imm10_1 << 21) | (imm11 << 20) | (imm19_12 << 12) | (rd << 7) | opcode


EXPECTED_PROGRAM = [
    encode_i(5, 0, 0b000, 1, OPC_OP_IMM),               # addi x1, x0, 5
    encode_i(10, 0, 0b000, 2, OPC_OP_IMM),               # addi x2, x0, 10
    encode_r(0b0000000, 2, 1, 0b000, 3, OPC_OP),         # add  x3, x1, x2
    encode_r(0b0100000, 1, 3, 0b000, 4, OPC_OP),         # sub  x4, x3, x1
    encode_s(0, 3, 0, 0b010, OPC_STORE),                 # sw   x3, 0(x0)
    encode_i(0, 0, 0b010, 5, OPC_LOAD),                  # lw   x5, 0(x0)
    encode_b(8, 1, 1, 0b000, OPC_BRANCH),                # beq  x1, x1, 8  (taken)
    encode_i(99, 0, 0b000, 6, OPC_OP_IMM),               # addi x6, x0, 99 (skipped)
    encode_i(42, 0, 0b000, 7, OPC_OP_IMM),               # addi x7, x0, 42
    encode_b(8, 2, 1, 0b000, OPC_BRANCH),                # beq  x1, x2, 8  (not taken)
    encode_i(77, 0, 0b000, 8, OPC_OP_IMM),               # addi x8, x0, 77
    encode_j(8, 9, OPC_JAL),                             # jal  x9, 8
    encode_i(55, 0, 0b000, 10, OPC_OP_IMM),              # addi x10, x0, 55 (skipped)
    encode_i(66, 0, 0b000, 11, OPC_OP_IMM),              # addi x11, x0, 66
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
    for i in [14, 15, 50, 255]:
        got = await read(dut, i * 4)
        assert got == NOP, f"instr_mem[{i}]: expected NOP {NOP:#010x}, got {got:#010x}"


@cocotb.test()
async def test_byte_to_word_addressing(dut):
    """pc is a byte address; instruction[1] should show up at pc=4, not pc=1."""
    got_at_4 = await read(dut, 4)
    assert got_at_4 == EXPECTED_PROGRAM[1], (
        f"pc=4 should read instr_mem[1], got {got_at_4:#010x}, expected {EXPECTED_PROGRAM[1]:#010x}"
    )
