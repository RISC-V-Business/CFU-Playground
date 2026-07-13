// Auto-generated GF180 SRAM selector.
`include "generated_defines.svh"

`ifdef SRAM_gf180mcu_ocd_ip_sram
`define CFU_SRAM_512X8 gf180mcu_ocd_ip_sram__sram512x8m8wm1
`else
`define CFU_SRAM_512X8 gf180mcu_fd_ip_sram__sram512x8m8wm1
`endif

module gf180_ram_512x8_wrapper (
    input  wire       CLK,
    input  wire       CEN,
    input  wire       GWEN,
    input  wire [7:0] WEN,
    input  wire [8:0] A,
    input  wire [7:0] D,
    output wire [7:0] Q
);
    `CFU_SRAM_512X8 RAM (
        .CLK  (CLK),
        .CEN  (CEN),
        .GWEN (GWEN),
        .WEN  (WEN),
        .A    (A),
        .D    (D),
        .Q    (Q),
        .VDD  (),
        .VSS  ()
    );
endmodule

`undef CFU_SRAM_512X8
