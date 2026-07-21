# Getting started: the three layers, and how they relate

The [README](https://github.com/cesdm/cesdm-toolbox#a-first-example-two-ways) shows the same
small electricity system built two ways: the recommended
object-oriented layer (`model.add_generator(...)`, `gas.dispatch.x = y`,
`.connect(...)`), and the core EAR primitives underneath it
(`add_entity`, `add_attribute`, `add_relation`).

There's a third, in-between layer worth knowing about: the same
builder functions shown in the README (`add_bus`, `add_thermal_generator`,
`create_demand_unit`, `create_transmission_line`, ...) *without* the
object-oriented proxy sugar on top — using their plain string return
values and `ensure_*`/`set_attribute_if_allowed`/`ensure_dispatch_view`
directly, the way code written before the proxy API existed still
looks.

All three build the exact same underlying EAR data; none of them is a
separate or lesser representation. Pick whichever fits: proxy objects
for everyday model-building, builder functions with plain ids for
lower-level scripting or bulk import pipelines, raw EAR calls for
anything a builder doesn't cover yet or for writing a new importer.

```python
from pathlib import Path
from cesdm_toolbox import build_model_from_yaml

model = build_model_from_yaml("schemas")
model.import_library("library/default_library")

model.ensure_entity("EnergySystemModel", "ch_example")

bus_1 = model.add_bus("bus.ch.1", nominal_voltage=380)
bus_2 = model.add_bus("bus.ch.2", nominal_voltage=380)

gas_id = model.add_thermal_generator(
    "gas.ch.1", bus_id="bus.ch.1", nominal_power_capacity=400,
    technology_id="Generation.Thermal.Gas.CCGT.Present2",
)
model.set_attribute_if_allowed(gas_id, "name", "Gas turbine CH-1")

wind_id = model.add_wind_generator(
    "wind.ch.1", bus_id="bus.ch.1", nominal_power_capacity=120,
)

demand_id = model.create_demand_unit("demand.ch.1", bus_id="bus.ch.2")
model.ensure_dispatch_view(demand_id, view_class="Demand.DispatchView", maximum_energy_demand=250)

model.create_transmission_line("line.ch.1", "bus.ch.1", "bus.ch.2")

model.validate_or_raise()
print(model.summary())
# GenerationUnit            2
# DemandUnit                1
# TransmissionElement       1
```

Byte-for-byte the same model as both README versions.

`add_thermal_generator`/`add_wind_generator`/`create_demand_unit`/
`create_transmission_line` already return plain entity ids (`gas_id`,
`wind_id`, ...) — wrap any of them in `model.asset(entity_id)` to get
the same object-oriented proxy the README's first example uses,
whenever you decide you want `.dispatch`/`.connect(...)` after all:

```python
gas = model.asset(gas_id)
gas.dispatch.nominal_power_capacity = 450  # now using the proxy API
```

See [`docs/architecture/proxy_api.md`](architecture/proxy_api.md) for
the full design of the proxy layer, including what it deliberately
doesn't cover yet.
