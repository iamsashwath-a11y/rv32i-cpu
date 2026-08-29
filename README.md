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
               a flow smoke test, gains a `core/` dir once Phase 4 is done)
scripts/       Toolchain glue (elf->hex for test programs, waveform helpers)
docs/          Design notes, ISA subset decisions, hazard analysis
tools/         riscv-gnu-toolchain / riscv-arch-test checkouts (gitignored)
```

## Status

- [x] Phase 0 — scaffolding
- [ ] Phase 1 — golden RV32I reference model
- [x] Phase 2 — first building block: `alu.v` + `test_alu.py` (start here)
- [ ] Phase 2 — regfile, imm_gen, decoder
- [ ] Phase 3 — single-cycle core composed + riscv-arch-test passing
- [ ] Phase 4 — pipeline registers inserted incrementally + hazard logic
- [ ] Phase 5 — synthesis-clean lint pass
- [ ] Phase 6 — OpenLane hardening, DRC/LVS clean
- [ ] Phase 7 — STA timing closure at target frequency

## Running the ALU unit test

```
cd sim
make
```

## Design rules (kept from day one so nothing needs retrofitting for OpenLane)

- Single clock domain, single synchronous active-low (or active-high — pick
  one and never mix) reset.
- No latches: every combinational `always @(*)` block must assign every
  output on every path.
- No `initial` blocks in synthesizable RTL (simulation-only files are exempt
  and live under `tb/`).
- No multi-driven nets, no combinational loops.
- Verilator `--lint-only` must be clean before a block is considered done.
