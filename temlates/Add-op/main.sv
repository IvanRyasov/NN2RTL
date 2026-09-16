module Addition
(
    parameter N,
    parameter M,
    parameter DATA_WIDTH,
)
(
    input clk,
    input rst,

    input logic [DATA_W - 1:0] A [0:N - 1][0:M - 1],
    input logic [DATA_W - 1:0] B [0:N - 1][0:M - 1],
    input vld_in,

    output logic [DATA_W - 1:0] C [0:N - 1][0:M - 1],
    output logic vld_out
);

genvar i;
genvar j;
generate
    always_ff @(posedge clk) begin
        if(rst)
            vld_out <= 1'b0;
        else begin
            if(vld_in)
                for(i = 0; i < N; i++)
                    for(j = 0; j < M; j++)
                        C[i][j] <= A[i][j] + B[i][j]
                vld_out <= 1'b1;
            else
                vld_out <= 1'b0;
        end
    end
endgenerate

endmodule