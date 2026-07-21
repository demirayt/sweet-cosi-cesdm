# `example_kundur_two_area.py` — Step by Step

## Why this example matters

This is the only example reaching past steady-state dispatch and power
flow into dynamic/stability modelling — machine models, voltage
regulators (AVR), turbine governors (GOV), and power system stabilizers
(PSS). It reproduces a genuinely well-known benchmark (Kundur's
four-machine, two-area system, *Power System Stability and Control*,
1994, Ch. 12), so every number in it is independently checkable
against a real textbook, not invented for the demo.

It's also the example that found and fixed a real CESDM bug: AVR, GOV,
and PSS controllers used to all share the same `view_family` as the
machine's own dynamic view, so `gen.dynamic` could resolve to an
arbitrary one of the four. Each controller type now has its own
family, so `gen.dynamic`/`gen.avr`/`gen.governor`/`gen.pss` are each
independently, unambiguously readable.

---

## One generator, four distinct dynamic/controller views

```python
gen = model.create_generation_unit(gen_id, bus_id=bus_id)
pf = gen.powerflow
for attr, val in _GEN_PF[gen_id].items():
    setattr(pf, attr, val)

# Machine model (subtransient)
dyn = model.add_generator_dynamic_view_subtransient(
    f"dyn.machine.{gen_id}", representsAsset=gen,
    **mach,  # MACHINE_xd, MACHINE_H, MACHINE_xd_prime, ... -- all underscore-separated ids
)

# Automatic Voltage Regulator (SEXS model)
avr = model.add_controller_view_avr_sexs(f"dyn.avr.{gen_id}", representsAsset=gen, **_AVR)
dyn.hasAutomaticVoltageRegulator = avr

# Power System Stabilizer (STAB1 model)
pss = model.add_controller_view_pss_stab1(f"dyn.pss.{gen_id}", representsAsset=gen, **_PSS)
dyn.hasPowerSystemStabilizer = pss

# Turbine governor (IEEEG1 model)
governor = model.add_controller_view_gov_ieeeg1(f"dyn.gov.{gen_id}", representsAsset=gen, **gov)
dyn.hasTurbineGovernor = governor
```

Four separate concrete view classes on the same asset, each created
via its own generated constructor (`add_generator_dynamic_view_
subtransient`, `add_controller_view_avr_sexs`, ...) rather than
through `.dynamic`/`.avr`/etc — explicit construction stays the
clearest way to create four specifically-named views on one asset.
Reading them back afterward (`gen.dynamic.MACHINE_xd`, `gen.avr.
AVR_SEXS_Ka`, ...) works through the proxy properties, now that each
family has its own `view_family` to resolve against unambiguously.

---

## Power-flow parameters: transformers and lines

```python
tfr = model.add_transformer(tfr_id, name=tfr_id.upper())
tfr.connect(from_bus, to_bus)
tfr.powerflow.short_circuit_voltage_in_percentage = scc_pct
tfr.powerflow.thermal_capacity_rating = rated_mva

line = model.create_transmission_line(line_id, from_bus, to_bus)
line.powerflow.series_resistance_per_km = pu_to_ohm(r_pu, Z_base_sys)
line.powerflow.series_reactance_per_km = pu_to_ohm(x_pu, Z_base_sys)
line.powerflow.shunt_susceptance_per_km = pu_to_siemens(b_pu, Z_base_sys)
```

The source data (Kundur's own textbook table) gives impedances in
per-unit on the system base — `pu_to_ohm`/`pu_to_siemens` convert them
to physical units before they're stored, since CESDM's power-flow
attributes are physical-unit quantities, not per-unit ones.

---

## Result

```
Network nodes  : 11 buses
Generators     : 4 units
Transformers   : 4 units
Lines          : 7 circuits
Loads          : 2 units

Generator machine parameters (converted to physical units)
             Xd [Ω]    X'd [Ω]  X'' d [Ω]  H [s]  Pset [MW]
gen.g1       1.8000     0.3000     0.2500    6.5      700.0
gen.g2       1.8000     0.3000     0.2500    6.5      700.0
gen.g3       1.8000     0.3000     0.2500    6.5      719.0
gen.g4       1.8000     0.3000     0.2500    6.5      700.0
```

Every value printed here is recomputed from what's actually stored in
the model (converted back from physical units for display) — not
copy-pasted from the source table — so it also serves as an implicit
round-trip check.

---

## Run it yourself

```bash
python examples/example_kundur_two_area.py
```
