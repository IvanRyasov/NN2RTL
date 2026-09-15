module Gemm_op
#(
    parameter DATA_WIDTH = 8;
    parameter N;
    parameter M;
)
(
    input  logic clk,
    input  logic rst,

    // Inputs from back layer
    input  logic [DATA_WIDTH - 1:0] x_input [0:N - 1],
    input  logic start,
    input  Wights[0:N - 1][0:M - 1],

    // Outputs to next layer
    output logic [DATA_WIDTH - 1:0] y_output [0:M - 1],
    output logic vld_out
);

    localparam W_WIDTH = 8;
    localparam X_WIDTH = 8;

    generate
        genvar i;
        genvar j;

        logic [DATA_WIDTH - 1:0]  x_pipe[0:N - 2][0:M - 1];
        logic [DATA_WIDTH - 1:0]  psumm [0:N - 1][0:M - 1];
        logic vld_data[0:N - 2][0:M - 1];

        syst_node_i
        #(
            W_WIDTH(DATA_WIDTH),
            X_WIDTH(DATA_WIDTH),
            SI_WIDTH(DATA_WIDTH),
            SO_WIDTH(DATA_WIDTH)
        ) node
        (
            .clk(clk),
            .rst(rst),
            .weight_i(Wights[0][0]),
            .psumm_i('0),
            .vld(start),
            .x_i(x_input[0]),
            .psumm_o(psumm[0][0]),
            .x_o(x_pipe[0][0]),
            .vld_o(vld_data[0][0])
        )

        for(j = 1; j < M; j++) begin
            syst_node_i
            #(
                W_WIDTH(DATA_WIDTH),
                X_WIDTH(DATA_WIDTH),
                SI_WIDTH(DATA_WIDTH),
                SO_WIDTH(DATA_WIDTH)
            ) node
            (
                .clk(clk),
                .rst(rst),
                .weight_i(Wights[0][j]),
                .psumm_i('0),
                .vld(vld_data[0][j - 1]),
                .x_i(x_input[j]),
                .psumm_o(psumm[0][j]),
                .x_o(x_pipe[0][j]),
                .vld_o(vld_data[0][j])
            )
            end

        for(i = 1; i < N; i++) begin
            for(j = 0; j < M; j++) begin
                syst_node_i
                #(
                    W_WIDTH(DATA_WIDTH),
                    X_WIDTH(DATA_WIDTH),
                    SI_WIDTH(DATA_WIDTH),
                    SO_WIDTH(DATA_WIDTH)
                ) node
                (
                    .clk(clk),
                    .rst(rst),
                    .weight_i(Wights[i][j]),
                    .psumm_i(psumm[i][j - 1]),
                    .vld(vld_data[i - 1][j] | vld_data[i][j - 1]),
                    .x_i(x_pipe[i - 1][j]),
                    .psumm_o(psumm[i][j - 1]),
                    .x_o(x_pipe[i][j]),
                    .vld_o(vld_data[i][j])
                )
            end
        end

        always_ff @(posedge clk)
        begin
            for (int k = 0; k < N; k++)
                if(vld_data[k][M - 1]) begin
                    y <= psumm[k][M - 1];
                    vld_out <= 1'b1;
                end
                else
                    vld_out <= 1'b0;

        end

    endgenerate


    

endmodule
