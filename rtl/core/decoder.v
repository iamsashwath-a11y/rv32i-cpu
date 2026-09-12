`include "rv32i_pkg.vh"

module decoder (
    input  wire [31:0] inst,
    output reg  [3:0]  alu_op,
    output reg  [2:0]  imm_type,
    output reg         reg_write,
    output reg         mem_read,
    output reg         mem_write,
    output reg         branch,
    output reg         jump,
    output reg         alu_src_imm,
    output reg  [4:0]  rs1,
    output reg  [4:0]  rs2,
    output reg  [4:0]  rd
);

    wire [6:0] opcode = inst[6:0];

    always @(*) begin
        // Fields in fixed positions regardless of instruction type.
        rs1 = inst[19:15];
        rs2 = inst[24:20];
        rd  = inst[11:7];

        // Safe defaults -- every output must be assigned on every path.
        alu_op      = `ALU_ADD;
        imm_type    = `IMM_I;
        reg_write   = 1'b0;
        mem_read    = 1'b0;
        mem_write   = 1'b0;
        branch      = 1'b0;
        jump        = 1'b0;
        alu_src_imm = 1'b0;

        case (opcode)
            `OPC_OP_IMM: begin
                alu_op      = `ALU_ADD;
                imm_type    = `IMM_I;
                reg_write   = 1'b1;
                alu_src_imm = 1'b1;
            end

            `OPC_OP: begin
                alu_op      = (inst[30]) ? `ALU_SUB : `ALU_ADD;
                imm_type    = `IMM_I;
                reg_write   = 1'b1;
                alu_src_imm = 1'b0;
            end

            `OPC_LOAD: begin
                alu_op      = `ALU_ADD;
                imm_type    = `IMM_I;
                reg_write   = 1'b1;
                mem_read    = 1'b1;
                alu_src_imm = 1'b1;
            end

            `OPC_STORE: begin
                alu_op      = `ALU_ADD;
                imm_type    = `IMM_S;
                reg_write   = 1'b0;
                mem_write   = 1'b1;
                alu_src_imm = 1'b1;
            end

            `OPC_BRANCH: begin
                alu_op      = `ALU_SUB;
                imm_type    = `IMM_B;
                reg_write   = 1'b0;
                branch      = 1'b1;
                alu_src_imm = 1'b0;
            end

            `OPC_LUI: begin
                imm_type    = `IMM_U;
                reg_write   = 1'b1;
            end

            `OPC_JAL: begin
                imm_type    = `IMM_J;
                reg_write   = 1'b1;
                jump        = 1'b1;
            end

            default: begin
            end
        endcase
    end

endmodule
