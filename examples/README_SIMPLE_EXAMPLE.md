# `example_simple.py` — Step by Step

## Why this example matters

One small system (3 electricity nodes) touching almost every core
entity type in one place: carriers, carrier domains, regions, three
different bus types, demand, two kinds of generation (dispatchable
and non-dispatchable), storage, interconnectors, and a multi-port
conversion unit. If you want to see how much of the schema fits
together without reading a huge system, this is the fastest way in.

It's also explicit about where the proxy API's coverage currently
ends: `ConversionUnit`'s multi-port (MIMO) structure has no dedicated
builder yet, so that section stays on the raw, low-level API on
purpose — "the schema stays powerful, use the low-level API for the
long tail" (see [`docs/architecture/proxy_api.md`](../docs/architecture/proxy_api.md), "What this does not do (yet)").

---

## Carriers, domains, regions, buses

```python
for eid, name, co2, cost in [
    ("Electricity", "Electricity", 0.0,  0.0),
    ("Gas",         "Gas",         0.20, 60.0),
    ("Heat",        "Heat",        0.0,  0.0),
    ("Water",       "Water",       0.0,  5.0),
    ("Uranium",     "Uranium",     0.0,  10.0),
]:
    m.ensure_carrier(eid, name=name)
    carrier = m.asset(eid)
    carrier.co2_emission_intensity = co2
    carrier.energy_carrier_cost = cost

for did, name, carrier in [("ELEC", "Electricity", "Electricity"), ("HEAT", "Heat", "Heat"), ("GAS", "Gas", "Gas")]:
    m.add_carrier_domain(did, name=name, hasCarrier=m.asset(carrier))
```

Three bus classes, not one generic "bus":

```python
n_e1 = m.add_bus("N_E1", nominal_voltage=220.0, region_id="R_A", carrier_domain_id="ELEC")
n_g1 = m.add_gas_bus("N_G1", name="Gas node G1", belongsToCarrierDomain=m.asset("GAS"), locatedIn=m.asset("R_A"))
n_h1 = m.add_heat_bus("N_H1", name="Heat node H1", belongsToCarrierDomain=m.asset("HEAT"), locatedIn=m.asset("R_A"))
```

`add_bus()` is specifically `ElectricalBus`; gas and heat get their
own typed node classes and their own builder functions.

---

## Two kinds of generation: dispatchable and not

```python
# Dispatchable: a gas turbine, carriers assigned directly (no technology template)
gt_a = m.create_generation_unit("GT_A", bus_id=n_e1, input_carrier_id="Gas", output_carrier_id="Electricity")
gt_a.dispatch.generator_technology_type = "gas"
gt_a.dispatch.energy_conversion_efficiency = 0.50
gt_a.dispatch.nominal_power_capacity = 200.0

# Non-dispatchable: run-of-river hydro -- a different concrete class
# (HydroGenerationUnit) and dispatch view (HydroGenerationUnit.DispatchView)
hyd_b = m.create_generation_unit(
    "HYD_B", class_name="HydroGenerationUnit", bus_id=n_e3,
    input_carrier_id="Water", output_carrier_id="Electricity",
    dispatch_view_class="HydroGenerationUnit.DispatchView",
)
hyd_b.dispatch.dispatch_type = "nondispatchable"
hyd_b.dispatch.turbine_efficiency = 0.90
hyd_b.dispatch.annual_resource_potential = 1_500_000.0
```

`create_generation_unit()` (not `add_generator(technology=...)`) is
the right tool here specifically because carriers are assigned
directly rather than resolved from a technology template — the two
builders cover two genuinely different starting points.

---

## Storage

```python
bat_e2 = m.create_storage_unit("BAT_E2", bus_id=n_e2, carrier_id="Electricity")
bat_e2.dispatch.energy_storage_capacity = 500.0
bat_e2.dispatch.nominal_power_capacity = 100.0
bat_e2.dispatch.maximum_charging_power = 100.0
bat_e2.dispatch.charging_efficiency = 0.95
bat_e2.dispatch.discharging_efficiency = 0.95
bat_e2.dispatch.initial_state_of_charge = 0.50
```

---

## Interconnectors

```python
ntc = m.add_interconnector("NTC_E1_E2", name="NTC E1-E2")
ntc.connect(n_e1, n_e2)
ntc.powerflow.maximum_power_flow_from_to = 300.0
ntc.powerflow.maximum_power_flow_to_from = 300.0
```

---

## The part with no builder yet: a multi-port fuel cell

A PEM fuel cell (H₂ + implicit air → electricity + heat) needs three
separate `ConversionPort` entities — one per physical port, each with
its own flow coefficient defining the conversion ratio:

```python
fuel_cell = m.add_conversion_unit("FC_A", name="PEM Fuel Cell A")

# Reference port: H2 input (negative = withdrawal)
m.add_conversion_port(
    "port.FC_A.h2_in", port_direction="input", flow_coefficient=-1.0,
    is_reference_port=True, belongsToUnit=fuel_cell, atNode=n_h2, hasCarrier=h2,
)
# Electricity output
m.add_conversion_port(
    "port.FC_A.elec_out", port_direction="output", flow_coefficient=0.55,
    maximum_output_power=55.0, belongsToUnit=fuel_cell, atNode=n_e1,
    hasCarrier=m.asset("Electricity"),
)
# Heat output
m.add_conversion_port(
    "port.FC_A.heat_out", port_direction="output", flow_coefficient=0.30,
    maximum_output_power=30.0, belongsToUnit=fuel_cell, atNode=n_h1,
    hasCarrier=m.asset("Heat"),
)

m.add_conversion_dispatch_view("conversion_dispatch_view.FC_A", representsAsset=fuel_cell)
```

`add_conversion_unit`/`add_conversion_port`/`add_conversion_dispatch_view`
are generated (schema-driven, one per class) builders, not composite
ones — there's no single call that wires up a whole multi-port unit
yet, so each port is created individually, exactly the "long tail"
case the low-level API exists for.

---

## Result

```
DemandUnit                2
GenerationUnit            2
TransmissionElement       2
ConversionUnit            1
StorageUnit               1

Model validated successfully.
```

---

## Run it yourself

```bash
python examples/example_simple.py
```
