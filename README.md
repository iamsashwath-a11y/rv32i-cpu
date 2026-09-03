# rv32i-cpu

A tape-out-ready RV32I core, built incrementally (MIT 6.004 style: verify
each small piece in isolation before composing), verified with cocotb,
hardened through OpenLane targeting the Sky130 PDK.

Target microarchitecture: **5-stage pipeline** (IF / ID / EX / MEM / WB).
A single-cycle behavioral reference is built first purely as a verification
oracle — it is never the synthesis target.

## Repo layout

```
rtl/
  core/        Non-pipelined building blocks: alu, regfile, imm_gen, decoder...
  pipeline/    Pipeline registers, hazard/forwarding unit, top-level core
tb/
  unit/        One cocotb test per rtl/core block, in isolation
  integration/ Full-core tests: golden-model comparison, hazard directed
               tests, riscv-arch-test compliance harness
sim/           Cocotb/Verilator Makefile
openlane/      One config dir per hardened design (starts with `alu/` as
               a flow smoke test, gains a `core/` dir once the pipeline is done)
scripts/       Toolchain glue (elf->hex for test programs, waveform helpers)
docs/          Design notes, ISA subset decisions, hazard analysis
tools/         riscv-gnu-toolchain / riscv-arch-test checkouts (gitignored)
```

## Status

- [x] `alu.v` + `test_alu.py` — combinational ALU (add/sub/shifts/compares)
- [x] `regfile.v` + `test_regfile.py` — 32 registers, x0 hardwiring, same-cycle write/read bypass
- [x] `imm_gen.v` + `test_imm_gen.py` — I/S/B/U/J-type immediate extraction
- [x] `decoder.v` + `test_decoder.py` — addi, add, sub, lw, sw, beq, lui, jal
- [ ] Wire alu/regfile/imm_gen/decoder + PC + instruction memory into a single-cycle core
- [ ] Add data memory (loads/stores) + branch/jump datapath wiring
- [ ] Verify single-cycle core thoroughly (golden-model + riscv-arch-test)
- [ ] Insert pipeline registers incrementally (IF/ID, ID/EX, EX/MEM, MEM/WB)
- [ ] Hazard handling: forwarding, load-use stall, branch flush
- [ ] Synthesis-clean lint pass
- [ ] OpenLane hardening: synth -> floorplan -> place -> CTS -> route
- [ ] DRC/LVS sign-off, timing closure

## Running the unit tests

Each module has its own cocotb test. From `sim/`:

```
make SIM=icarus MODULE=test_alu     TOPLEVEL=alu     VERILOG_SOURCES=../rtl/core/alu.v
make SIM=icarus MODULE=test_regfile TOPLEVEL=regfile VERILOG_SOURCES=../rtl/core/regfile.v
make SIM=icarus MODULE=test_imm_gen TOPLEVEL=imm_gen VERILOG_SOURCES=../rtl/core/imm_gen.v
make SIM=icarus MODULE=test_decoder TOPLEVEL=decoder VERILOG_SOURCES=../rtl/core/decoder.v
```

(Clean `sim/sim_build/` between runs of different top-level modules.)
Drop `SIM=icarus` to default to Verilator once available in your environment.

## Design rules (kept from day one so nothing needs retrofitting for OpenLane)

- Single clock domain, single synchronous reset convention (kept consistent
  once reset is introduced at the pipeline stage).
- No latches: every combinational `always @(*)` block assigns every output
  on every path.
- No `initial` blocks in synthesizable RTL (simulation-only files are exempt
  and live under `tb/`).
- No multi-driven nets, no combinational loops.
