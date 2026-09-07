// Program counter: holds the address of the current instruction.
// Synchronous reset -- forces pc_out back to 0 on the next clock edge
// when reset is asserted, so the CPU always starts fetching from a known
// address at power-up.
module pc (
    input  wire        clk,
    input  wire        reset,
    input  wire [31:0] pc_next,
    output reg  [31:0] pc_out
);

    always @(posedge clk) begin
        if (reset) begin
            pc_out <= 32'd0;  // Reset PC to standard start address
        end else begin
            pc_out <= pc_next;       // Update PC to next instruction address on clock edge
        end
    end

endmodule
