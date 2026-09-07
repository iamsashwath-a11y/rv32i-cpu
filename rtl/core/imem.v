// Instruction Memory (Sim-Only / Pre-Loaded Storage)
// 1KB (256 words x 32 bits) combinational instruction memory.
// Note: Contains an initial block for simulation testing (non-synthesizable).
module imem (
    input  wire [31:0] pc,
    output wire [31:0] instruction
);
    // Storage array: 256 words (32-bit width)
    reg [31:0] instr_mem [0:255];
    // Byte address to word index conversion
    // Dropping bottom 2 bits divides PC by 4 (pc[31:2])
    wire [7:0] word_addr = pc[9:2];
    // Combinational (asynchronous) read
    assign instruction = instr_mem[word_addr];
    // Simulation-only initial block to load test program
    initial begin
        // Safe default: fill memory with NOPs (addi x0, x0, 0 -> 32'h00000013)
        integer i;
        for (i = 0; i < 256; i = i + 1) begin
            instr_mem[i] = 32'h0000_0013;
        end
        // --- Hardcoded Test Program ---
        // 0x00: addi x1, x0, 5     (x1 = 5)
        instr_mem[0] = 32'h00500093;

        // 0x04: addi x2, x0, 10    (x2 = 10)
        instr_mem[1] = 32'h00a00113;

        // 0x08: add  x3, x1, x2    (x3 = 15)
        instr_mem[2] = 32'h002081b3;

        // 0x0C: sub  x4, x3, x1    (x4 = 10)
        instr_mem[3] = 32'h40118233;
    end
endmodule
