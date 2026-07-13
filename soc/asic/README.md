# CFU-Playground ASIC integration

The public ASIC interface is [`asic.mk`](asic.mk). The main CFU-Playground
Makefile imports that file for ASIC goals; PDK, shuttle, slot, library, CPU and
project choices are not spread across the main Makefile.

The default target is a standalone LiteX/VexRiscv+CFU SoC in the Wafer.Space
GF180 pad ring. It uses the Caravel management-SoC generator as the reusable
LiteX harness, ties off Caravel-only housekeeping/LA/Wishbone inputs, and maps
QSPI, UART, SPI, GPIO and four IRQ inputs to Wafer.Space pads.

## Commands

Run from the repository root or from `src/CFU-Playground`:

```sh
make asic setup
make asic env SHUTTLE=wafer_space
make asic TARGET=gf180 SHUTTLE=wafer_space PROJ=wamCFU
make cocoTB
```

Canonical single-goal aliases are also available: `asic-setup`, `asic-env`,
`asic-generate`, `asic-build`, `asic-cocotb`, and `asic-cocotb-gl`.

The current defaults are `PDK=gf180mcuD`, `SLOT=1x1`,
`SCL=gf180mcu_fd_sc_mcu7t5v0`, `PAD=gf180mcu_fd_io`,
`SRAM=gf180mcu_fd_ip_sram`, `CPU_VARIANT=minimal+cfu`, and a 25 MHz clock.
The 3.3 V experimental libraries must be selected as one coherent SCL/PAD/SRAM
bundle.

## Integration structure

- `asic.mk`: user-facing variables, target/provider validation and commands.
- `targets/`: small declarative description of each logical ASIC target.
- `workflows/`: deterministic LiteX generation and shuttle-specific export.
- `templates/`: generated Wafer.Space core adapter and SRAM selector.
- `scripts/`: the internal export command invoked by `asic.mk`.
- `core/`: vendor harnesses and PDK-specific hard-memory support.
- `librelane/`: shuttle plugins, physical configuration and verification.

The generated SoC and manifest are written under
`soc/build/asic/gf180.wafer_space.<project>/`. LibreLane consumes an exported
copy under the selected plugin's `src/generated/` directory.

## FPGA parity

The normal project-local FPGA flow remains unchanged:

```sh
make -C proj/wamCFU bitstream TARGET=tul_pynq_z2 USE_SYMBIFLOW=1
```

Both flows select the same `proj/<project>/cfu.sv` or `cfu.v`. Platform-specific
clock/reset, boot memory and I/O stay in the FPGA board target or ASIC adapter.

## Tapeout inputs to freeze

Before signoff, confirm the Wafer.Space slot, voltage/library bundle, 25 MHz
timing target, external QSPI boot device, pad map, and the four hard-SRAM macro
placements. A full run is complete only after final views, gate-level cocotb,
and the Wafer.Space GF180 precheck pass.
