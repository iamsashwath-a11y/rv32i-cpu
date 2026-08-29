// rv32i_pkg.vh
// Shared opcode / funct field / ALU-op definitions for the RV32I core.
// Included (not `import`ed) so it works cleanly through Verilator + OpenLane's
// synthesis flow without SystemVerilog package elaboration quirks.

`ifndef RV32I_PKG_VH
`define RV32I_PKG_VH

// ---------------------------------------------------------------------------
// Major opcodes (inst[6:0])
// ---------------------------------------------------------------------------
`define OPC_LUI      7'b0110111
`define OPC_AUIPC    7'b0010111
`define OPC_JAL      7'b1101111
`define OPC_JALR     7'b1100111
`define OPC_BRANCH   7'b1100011
`define OPC_LOAD     7'b0000011
`define OPC_STORE    7'b0100011
`define OPC_OP_IMM   7'b0010011
`define OPC_OP       7'b0110011
`define OPC_FENCE    7'b0001111
`define OPC_SYSTEM   7'b1110011

// ---------------------------------------------------------------------------
// funct3 (BRANCH)
// ---------------------------------------------------------------------------
`define F3_BEQ  3'b000
`define F3_BNE  3'b001
`define F3_BLT  3'b100
`define F3_BGE  3'b101
`define F3_BLTU 3'b110
`define F3_BGEU 3'b111

// ---------------------------------------------------------------------------
// funct3 (LOAD / STORE)
// ---------------------------------------------------------------------------
`define F3_LB   3'b000
`define F3_LH   3'b001
`define F3_LW   3'b010
`define F3_LBU  3'b100
`define F3_LHU  3'b101
`define F3_SB   3'b000
`define F3_SH   3'b001
`define F3_SW   3'b010

// ---------------------------------------------------------------------------
// funct3 (OP / OP-IMM)
// ---------------------------------------------------------------------------
`define F3_ADD_SUB 3'b000
`define F3_SLL      3'b001
`define F3_SLT      3'b010
`define F3_SLTU     3'b011
`define F3_XOR      3'b100
`define F3_SRL_SRA  3'b101
`define F3_OR       3'b110
`define F3_AND      3'b111

// ---------------------------------------------------------------------------
// Internal ALU control encoding (decoder -> ALU). Not an ISA field.
// ---------------------------------------------------------------------------
`define ALU_ADD  4'd0
`define ALU_SUB  4'd1
`define ALU_SLL  4'd2
`define ALU_SLT  4'd3
`define ALU_SLTU 4'd4
`define ALU_XOR  4'd5
`define ALU_SRL  4'd6
`define ALU_SRA  4'd7
`define ALU_OR   4'd8
`define ALU_AND  4'd9

`endif // RV32I_PKG_VH
