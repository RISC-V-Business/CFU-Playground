# ASIC build facade for CFU-Playground.
#
# Do not include PDK or shuttle Makefiles here.  Those files contain generic
# targets (`all`, `setup`, `sim`, ...) and assume their own working directory.
# Recursive make keeps those implementation details behind this interface.

ASIC_DIR := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))
CFU_ROOT ?= $(realpath $(ASIC_DIR)/../..)

TARGET ?= gf180
SHUTTLE ?= wafer_space
PROJ ?= wamCFU
SLOT ?= 1x1
PDK ?= gf180mcuD
SCL ?= gf180mcu_fd_sc_mcu7t5v0
PAD ?= gf180mcu_fd_io
SRAM ?= gf180mcu_fd_ip_sram
CPU_VARIANT ?= minimal+cfu

ASIC_PYTHON ?= $(CFU_ROOT)/scripts/pyrun
ASIC_CLI := $(ASIC_PYTHON) $(ASIC_DIR)/scripts/asic.py
ASIC_PLUGIN_DIR := $(ASIC_DIR)/librelane/gf180mcu-waferspace-plugin
ASIC_NIX_INSTALLER ?= https://nixos.org/nix/install

ASIC_COMMON_ARGS := \
	--target $(TARGET) \
	--shuttle $(SHUTTLE) \
	--project $(PROJ) \
	--slot $(SLOT) \
	--scl $(SCL) \
	--pad $(PAD) \
	--sram $(SRAM) \
	--cpu-variant $(CPU_VARIANT)

ifeq ($(filter $(TARGET),gf180 gf180mcu),)
$(error Unsupported ASIC TARGET '$(TARGET)'; supported targets: gf180)
endif

ifeq ($(filter $(SHUTTLE),wafer_space wafer-space waferspace),)
$(error Unsupported SHUTTLE '$(SHUTTLE)'; supported shuttles: wafer_space)
endif

ifneq ($(PDK),gf180mcuD)
$(error Wafer.Space GF180 requires PDK=gf180mcuD, got '$(PDK)')
endif

.PHONY: asic asic-help asic-setup asic-env asic-describe asic-generate asic-build
.PHONY: asic-cocotb asic-cocotb-gl cocoTB cocotb setup env

# Compatibility with the requested command spelling:
#   make asic setup
#   make asic env SHUTTLE=wafer_space
# With a subcommand present, `asic` is a dispatcher rather than a build goal.
ifneq ($(filter setup env,$(MAKECMDGOALS)),)
asic:
	@:
else
asic: asic-build
endif

setup: asic-setup

env: asic-env

asic-setup:
	@if command -v nix >/dev/null 2>&1; then \
		echo "Nix is already installed: $$(nix --version)"; \
	else \
		echo "Installing Nix from $(ASIC_NIX_INSTALLER)"; \
		command -v curl >/dev/null 2>&1 || { echo "curl is required to install Nix" >&2; exit 1; }; \
		curl --proto '=https' --tlsv1.2 -sSf -L $(ASIC_NIX_INSTALLER) | sh -s -- --daemon; \
	fi
	@echo "Run 'make asic env SHUTTLE=$(SHUTTLE)' to enter the LibreLane shell."

asic-env:
	@$(ASIC_CLI) describe $(ASIC_COMMON_ARGS)
	@exec nix develop $(ASIC_PLUGIN_DIR)

asic-help:
	@echo "ASIC targets (configuration is centralized in soc/asic/asic.mk):"
	@echo "  make asic setup"
	@echo "  make asic env SHUTTLE=wafer_space"
	@echo "  make asic TARGET=gf180 SHUTTLE=wafer_space PROJ=$(PROJ)"
	@echo "  make cocoTB"
	@echo "Options: PROJ TARGET SHUTTLE PDK SLOT SCL PAD SRAM CPU_VARIANT"

asic-describe:
	@$(ASIC_CLI) describe $(ASIC_COMMON_ARGS)

asic-generate:
	$(ASIC_CLI) generate $(ASIC_COMMON_ARGS)

asic-build:
	@command -v librelane >/dev/null 2>&1 || { \
		echo "LibreLane is not on PATH. Enter the environment with 'make asic env SHUTTLE=$(SHUTTLE)'." >&2; \
		exit 1; \
	}
	$(ASIC_CLI) generate $(ASIC_COMMON_ARGS)
	$(MAKE) -C $(ASIC_PLUGIN_DIR) librelane \
		PDK=$(PDK) SLOT=$(SLOT) SCL=$(SCL) PAD=$(PAD) SRAM=$(SRAM)

asic-cocotb cocoTB cocotb:
	@command -v python3 >/dev/null 2>&1
	$(ASIC_CLI) generate $(ASIC_COMMON_ARGS)
	$(MAKE) -C $(ASIC_PLUGIN_DIR) sim \
		PDK=$(PDK) SLOT=$(SLOT) SCL=$(SCL) PAD=$(PAD) SRAM=$(SRAM)

asic-cocotb-gl:
	$(MAKE) -C $(ASIC_PLUGIN_DIR) sim-gl \
		PDK=$(PDK) SLOT=$(SLOT) SCL=$(SCL) PAD=$(PAD) SRAM=$(SRAM)
