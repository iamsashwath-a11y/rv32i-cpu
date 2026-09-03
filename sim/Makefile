SIM ?= verilator
TOPLEVEL_LANG ?= verilog

RTL_DIR := $(abspath ../rtl)
TB_DIR  := $(abspath ../tb)

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
