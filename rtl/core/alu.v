`include "rv32i_pkg.vh"

// Purely combinational 32-bit ALU. No clock, no reset.
// Kept synthesis-clean on purpose: this is the first block hardened through
// OpenLane, so it doubles as a smoke test for the whole flow before the
// full core exists.
module alu (
    input  wire [31:0] a,
    input  wire [31:0] b,
    input  wire [3:0]  alu_op,
    output reg  [31:0] result,
    output wire        zero        // result == 0, used later for branch compares
);

    wire [4:0] shamt = b[4:0];

    always @(*) begin
        case (alu_op)
            `ALU_ADD:  result = a + b;
            `ALU_SUB:  result = a - b;
            `ALU_SLL:  result = a << shamt;
            `ALU_SLT:  result = ($signed(a) < $signed(b)) ? 32'd1 : 32'd0;
            `ALU_SLTU: result = (a < b) ? 32'd1 : 32'd0;
            `ALU_XOR:  result = a ^ b;
            `ALU_SRL:  result = a >> shamt;
            `ALU_SRA:  result = $signed(a) >>> shamt;
            `ALU_OR:   result = a | b;
            `ALU_AND:  result = a & b;
            default:   result = 32'd0;
        endcase
    end

    assign zero = (result == 32'd0);

endmodule
