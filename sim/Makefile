# sim/Makefile
# Usage:
#   make MODULE=test_alu TOPLEVEL=alu SOURCES=../rtl/core/alu.v
# or just: make        (builds the default target below)
#
# Verilator is used for speed at pipeline scale; Icarus works as a drop-in
# by overriding SIM=icarus if you prefer it for a given block.

SIM ?= verilator
TOPLEVEL_LANG ?= verilog

RTL_DIR := $(abspath ../rtl)
TB_DIR  := $(abspath ../tb)

# Default target: ALU unit test. Override on the command line for other blocks, e.g.:
#   make MODULE=test_regfile TOPLEVEL=regfile VERILOG_SOURCES="$(RTL_DIR)/core/regfile.v"
MODULE    ?= test_alu
TOPLEVEL  ?= alu
VERILOG_SOURCES ?= $(RTL_DIR)/core/alu.v

VERILOG_INCLUDE_DIRS := $(RTL_DIR)/core

COMPILE_ARGS += -I$(RTL_DIR)/core

ifeq ($(SIM),verilator)
EXTRA_ARGS += --trace --trace-structs
endif

export PYTHONPATH := $(TB_DIR)/unit:$(TB_DIR)/integration:$(PYTHONPATH)

include $(shell cocotb-config --makefiles)/Makefile.sim
