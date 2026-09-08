`include "rv32i_pkg.vh"
module cpu_core (
    input  wire clk,
    input  wire reset
);
    // =========================================================================
    // 1. Internal Wire Declarations (Connecting the Datapath)
    // =========================================================================
    wire [31:0] pc_out;
    wire [31:0] pc_next;
    wire [31:0] inst;
    // Decoder Output Control Signals & Register Addresses
    wire [3:0]  alu_op;
    wire [2:0]  imm_type;
    wire        reg_write;
    wire        mem_read;
    wire        mem_write;
    wire        branch;
    wire        alu_src_imm;
    wire [4:0]  rs1;
    wire [4:0]  rs2;
    wire [4:0]  rd;
    // Data Signals
    wire [31:0] rs1_data;
    wire [31:0] rs2_data;
    wire [31:0] imm_out;
    wire [31:0] alu_b_input;
    wire [31:0] alu_result;
    wire        alu_zero;
    // =========================================================================
    // 2. Program Counter Next Logic (Simple PC + 4 for today)
    // =========================================================================
    assign pc_next = pc_out + 32'd4;
    // =========================================================================
    // 3. Module Instantiations
    // =========================================================================
    // Program Counter Register
    pc u_pc (
        .clk    (clk),
        .reset  (reset),
        .pc_next(pc_next),
        .pc_out (pc_out)
    );
    // Instruction Memory (Pre-loaded with test program)
    imem u_imem (
        .pc         (pc_out),
        .instruction(inst)
    );
    // Instruction Decoder
    decoder u_decoder (
        .inst       (inst),
        .alu_op     (alu_op),
        .imm_type   (imm_type),
        .reg_write  (reg_write),
        .mem_read   (mem_read),
        .mem_write  (mem_write),
        .branch     (branch),
        .alu_src_imm(alu_src_imm),
        .rs1        (rs1),
        .rs2        (rs2),
        .rd         (rd)
    );
    // Immediate Generator
    imm_gen u_imm_gen (
        .inst    (inst),
        .imm_type(imm_type),
        .imm_out (imm_out)
    );
    // Register File
    regfile u_regfile (
        .clk     (clk),
        .we      (reg_write),
        .rs1_addr(rs1),
        .rs2_addr(rs2),
        .rd_addr (rd),
        .rd_data (alu_result), // Direct writeback from ALU result (No memory yet)
        .rs1_data(rs1_data),
        .rs2_data(rs2_data)
    );
    // =========================================================================
    // 4. ALU Input MUX
    // =========================================================================
    // alu_src_imm = 0: Operand B comes from Register File (rs2_data)
    // alu_src_imm = 1: Operand B comes from Immediate Generator (imm_out)
    assign alu_b_input = (alu_src_imm) ? imm_out : rs2_data;
    // Arithmetic Logic Unit (ALU)
    alu u_alu (
        .a     (rs1_data),
        .b     (alu_b_input),
        .alu_op(alu_op),
        .result(alu_result),
        .zero  (alu_zero)
    );
endmodule
