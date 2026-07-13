// Auto-generated Wafer.Space adapter for the LiteX management SoC.
// Target clock: ${clock_hz} Hz.
`default_nettype none

module chip_core #(
    parameter integer NUM_INPUT_PADS = 4,
    parameter integer NUM_BIDIR_PADS = 38,
    parameter integer NUM_ANALOG_PADS = 1
) (
`ifdef USE_POWER_PINS
    inout  wire VDD,
    inout  wire VSS,
`endif
    input  wire clk,
    input  wire rst_n,

    input  wire [NUM_INPUT_PADS-1:0] input_in,
    output wire [NUM_INPUT_PADS-1:0] input_pu,
    output wire [NUM_INPUT_PADS-1:0] input_pd,

    input  wire [NUM_BIDIR_PADS-1:0] bidir_in,
    output logic [NUM_BIDIR_PADS-1:0] bidir_out,
    output logic [NUM_BIDIR_PADS-1:0] bidir_oe,
    output wire [NUM_BIDIR_PADS-1:0] bidir_cs,
    output wire [NUM_BIDIR_PADS-1:0] bidir_sl,
    output wire [NUM_BIDIR_PADS-1:0] bidir_ie,
    output wire [NUM_BIDIR_PADS-1:0] bidir_pu,
    output wire [NUM_BIDIR_PADS-1:0] bidir_pd,

    inout wire [NUM_ANALOG_PADS-1:0] analog
);
    // Fixed pad map shared by every Wafer.Space slot:
    //   0..3 QSPI DQ, 4 QSPI CS#, 5 QSPI CLK, 6 UART TX, 7 UART RX,
    //   8 SPI CLK, 9 SPI CS#, 10 SPI MOSI, 11 SPI MISO,
    //   12 GPIO, 13 debug select. input_in[3:0] are user IRQs.
    wire [3:0] flash_do;
    wire [3:0] flash_oeb;
    wire flash_cs_n;
    wire flash_clk;
    wire serial_tx;
    wire spi_clk;
    wire spi_cs_n;
    wire spi_mosi;
    wire gpio_out;
    wire gpio_outenb;

    assign input_pu = '0;
    assign input_pd = '0;
    assign bidir_cs = '0;
    assign bidir_sl = '0;
    assign bidir_ie = ~bidir_oe;
    assign bidir_pu = '0;
    assign bidir_pd = '0;

    always_comb begin
        bidir_out = '0;
        bidir_oe = '0;

        bidir_out[3:0] = flash_do;
        bidir_oe[3:0] = ~flash_oeb;
        bidir_out[4] = flash_cs_n;
        bidir_oe[4] = 1'b1;
        bidir_out[5] = flash_clk;
        bidir_oe[5] = 1'b1;
        bidir_out[6] = serial_tx;
        bidir_oe[6] = 1'b1;
        bidir_out[8] = spi_clk;
        bidir_oe[8] = 1'b1;
        bidir_out[9] = spi_cs_n;
        bidir_oe[9] = 1'b1;
        bidir_out[10] = spi_mosi;
        bidir_oe[10] = 1'b1;
        bidir_out[12] = gpio_out;
        bidir_oe[12] = ~gpio_outenb;
    end

    mgmt_core i_litex_soc (
`ifdef USE_POWER_PINS
        .VDD              (VDD),
        .VSS              (VSS),
`endif
        .core_clk         (clk),
        .core_rstn        (rst_n),
        .flash_cs_n       (flash_cs_n),
        .flash_clk        (flash_clk),
        .flash_io0_oeb    (flash_oeb[0]),
        .flash_io1_oeb    (flash_oeb[1]),
        .flash_io2_oeb    (flash_oeb[2]),
        .flash_io3_oeb    (flash_oeb[3]),
        .flash_io0_do     (flash_do[0]),
        .flash_io1_do     (flash_do[1]),
        .flash_io2_do     (flash_do[2]),
        .flash_io3_do     (flash_do[3]),
        .flash_io0_di     (bidir_in[0]),
        .flash_io1_di     (bidir_in[1]),
        .flash_io2_di     (bidir_in[2]),
        .flash_io3_di     (bidir_in[3]),
        .spi_clk          (spi_clk),
        .spi_cs_n         (spi_cs_n),
        .spi_mosi         (spi_mosi),
        .spi_miso         (bidir_in[11]),
        .serial_tx        (serial_tx),
        .serial_rx        (bidir_in[7]),
        .debug_in         (bidir_in[13]),
        .gpio_out_pad     (gpio_out),
        .gpio_in_pad      (bidir_in[12]),
        .gpio_outenb_pad  (gpio_outenb),
        .mprj_dat_i       (32'b0),
        .mprj_ack_i       (1'b1),
        .hk_dat_i         (32'b0),
        .hk_ack_i         (1'b1),
        .la_input         (64'b0),
        .user_irq         ({2'b0, input_in[3:0]}),
        .clk_in           (1'b0),
        .resetn_in        (1'b1),
        .serial_load_in   (1'b0),
        .serial_data_2_in (1'b0),
        .serial_resetn_in (1'b1),
        .serial_clock_in  (1'b0),
        .rstb_l_in        (1'b1),
        .por_l_in         (1'b1),
        .porb_h_in        (1'b1)
    );

    wire _unused = &{1'b0, analog};
endmodule

`default_nettype wire
