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

        // 0x10: sw   x3, 0(x0)     (mem[0] = 15)
        instr_mem[4] = 32'h00302023;

        // 0x14: lw   x5, 0(x0)     (x5 = 15)
        instr_mem[5] = 32'h00002283;

        // 0x18: beq  x1, x1, 8     (taken -- x1==x1 -- jumps to 0x20, skipping 0x1C)
        instr_mem[6] = 32'h00108463;

        // 0x1C: addi x6, x0, 99    (should be SKIPPED by the taken branch above)
        instr_mem[7] = 32'h06300313;

        // 0x20: addi x7, x0, 42    (branch target -- should execute)
        instr_mem[8] = 32'h02a00393;

        // 0x24: beq  x1, x2, 8     (NOT taken -- x1=5, x2=10, not equal -- falls through)
        instr_mem[9] = 32'h00208463;

        // 0x28: addi x8, x0, 77    (fallthrough target -- should execute)
        instr_mem[10] = 32'h04d00413;

        // 0x2C: jal  x9, 8         (unconditional jump to 0x34, x9 = return addr 0x30)
        instr_mem[11] = 32'h008004ef;

        // 0x30: addi x10, x0, 55   (should be SKIPPED by the jal above)
        instr_mem[12] = 32'h03700513;

        // 0x34: addi x11, x0, 66   (jal target -- should execute)
        instr_mem[13] = 32'h04200593;
    end
endmodule
