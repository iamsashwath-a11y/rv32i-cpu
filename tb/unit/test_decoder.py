import cocotb
from cocotb.triggers import Timer

ALU_ADD, ALU_SUB = 0, 1
IMM_I, IMM_S, IMM_B, IMM_U, IMM_J = 0, 1, 2, 3, 4
OPC_OP_IMM = 0b0010011
OPC_OP     = 0b0110011
OPC_LOAD   = 0b0000011
OPC_STORE  = 0b0100011
OPC_BRANCH = 0b1100011
OPC_LUI    = 0b0110111
OPC_JAL    = 0b1101111


def encode_r(funct7, rs2, rs1, funct3, rd, opcode):
    return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode


def encode_i(imm12, rs1, funct3, rd, opcode):
    return ((imm12 & 0xFFF) << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode


def encode_s(imm12, rs2, rs1, funct3, opcode):
    imm = imm12 & 0xFFF
    return ((imm >> 5) << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | ((imm & 0x1F) << 7) | opcode


async def get_outputs(dut, inst):
    dut.inst.value = inst
    await Timer(1, unit="ns")
    return dict(
        alu_op=int(dut.alu_op.value), imm_type=int(dut.imm_type.value),
        reg_write=int(dut.reg_write.value), mem_read=int(dut.mem_read.value),
        mem_write=int(dut.mem_write.value), branch=int(dut.branch.value),
        alu_src_imm=int(dut.alu_src_imm.value), rs1=int(dut.rs1.value),
        rs2=int(dut.rs2.value), rd=int(dut.rd.value),
    )


@cocotb.test()
async def test_addi(dut):
    inst = encode_i(10, 2, 0b000, 5, OPC_OP_IMM)
    o = await get_outputs(dut, inst)
    assert o["rs1"] == 2 and o["rd"] == 5
    assert o["alu_op"] == ALU_ADD and o["imm_type"] == IMM_I
    assert o["reg_write"] == 1 and o["alu_src_imm"] == 1
    assert o["mem_read"] == 0 and o["mem_write"] == 0 and o["branch"] == 0


@cocotb.test()
async def test_add_sub(dut):
    inst_add = encode_r(0b0000000, 2, 1, 0b000, 3, OPC_OP)
    o = await get_outputs(dut, inst_add)
    assert o["alu_op"] == ALU_ADD and o["reg_write"] == 1 and o["alu_src_imm"] == 0
    assert o["rs1"] == 1 and o["rs2"] == 2 and o["rd"] == 3

    inst_sub = encode_r(0b0100000, 2, 1, 0b000, 3, OPC_OP)
    o = await get_outputs(dut, inst_sub)
    assert o["alu_op"] == ALU_SUB and o["reg_write"] == 1 and o["alu_src_imm"] == 0


@cocotb.test()
async def test_lw(dut):
    inst = encode_i(4, 2, 0b010, 5, OPC_LOAD)
    o = await get_outputs(dut, inst)
    assert o["rs1"] == 2 and o["rd"] == 5
    assert o["alu_op"] == ALU_ADD and o["imm_type"] == IMM_I
    assert o["mem_read"] == 1 and o["reg_write"] == 1 and o["alu_src_imm"] == 1
    assert o["mem_write"] == 0


@cocotb.test()
async def test_sw(dut):
    inst = encode_s(8, 5, 6, 0b010, OPC_STORE)
    o = await get_outputs(dut, inst)
    assert o["rs1"] == 6 and o["rs2"] == 5
    assert o["alu_op"] == ALU_ADD and o["imm_type"] == IMM_S
    assert o["mem_write"] == 1 and o["reg_write"] == 0 and o["alu_src_imm"] == 1


@cocotb.test()
async def test_beq(dut):
    inst = encode_s(0, 2, 1, 0b000, OPC_BRANCH)
    o = await get_outputs(dut, inst)
    assert o["rs1"] == 1 and o["rs2"] == 2
    assert o["alu_op"] == ALU_SUB and o["imm_type"] == IMM_B
    assert o["branch"] == 1 and o["reg_write"] == 0 and o["alu_src_imm"] == 0


@cocotb.test()
async def test_lui(dut):
    inst = (0x12345 << 12) | (5 << 7) | OPC_LUI
    o = await get_outputs(dut, inst)
    assert o["rd"] == 5
    assert o["imm_type"] == IMM_U and o["reg_write"] == 1


@cocotb.test()
async def test_jal(dut):
    inst = (0 << 31) | (0 << 12) | (0 << 20) | (0 << 21) | (1 << 7) | OPC_JAL
    o = await get_outputs(dut, inst)
    assert o["rd"] == 1
    assert o["imm_type"] == IMM_J and o["reg_write"] == 1
