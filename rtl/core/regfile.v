// 32 x 32-bit register file.
// - x0 hardwired to zero (writes ignored, reads forced to 0)
// - Two combinational (async) read ports
// - One synchronous (posedge-clocked) write port
// - Same-cycle write-to-read bypass: if the address being read this cycle
//   is also being written this cycle, forward rd_data directly instead of
//   returning the stale value still sitting in storage.
module regfile (
    input  wire        clk,
    input  wire        we,
    input  wire [4:0]  rs1_addr,
    input  wire [4:0]  rs2_addr,
    input  wire [4:0]  rd_addr,
    input  wire [31:0] rd_data,
    output wire [31:0] rs1_data,
    output wire [31:0] rs2_data
);

    reg [31:0] regfile [0:31];

    assign rs1_data = (rs1_addr == 5'b0) ? 32'b0 :
                      (we && rd_addr == rs1_addr) ? rd_data :
                      regfile[rs1_addr];

    assign rs2_data = (rs2_addr == 5'b0) ? 32'b0 :
                      (we && rd_addr == rs2_addr) ? rd_data :
                      regfile[rs2_addr];

    always @(posedge clk) begin
        if (we && rd_addr != 5'b0) begin
            regfile[rd_addr] <= rd_data;
        end
    end

endmodule
