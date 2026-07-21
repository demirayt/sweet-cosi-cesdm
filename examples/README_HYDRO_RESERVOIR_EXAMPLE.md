# `example_hydro_reservoir_plant.py` — Step by Step

## Why this example matters

A hydro plant is never one entity — it's a reservoir (storage) linked
to a turbine (generation), connected by `drawsFromReservoir`/
`suppliesResourceTo` relations. There's no `HydroPowerPlant` wrapper
class hiding this; the composite builders create both entities and
wire the relation pairing between them in one call. This is the
general pattern for any physical system made of multiple linked
assets, not just hydro.

Two variants are shown: simple reservoir hydro, and closed-loop
pumped storage (PHS) — the same structural pattern, with a reversible
turbine and a second, lower reservoir.

---

## Reservoir hydro: two linked entities, one call

```python
reservoir, gen = m.add_reservoir_hydro(
    "gen.hydro.alpine", "reservoir.alpine", bus_id=bus,
    nominal_power_capacity=500.0, energy_storage_capacity=2500.0,
)

reservoir.name = "Alpine reservoir"
m.add_relation_if_allowed(reservoir, "storesResource", "resource.water")
reservoir.dispatch.annual_natural_inflow_energy = 900_000.0

gen.name = "Alpine hydro turbine"
gen.is_reversible = False
m.add_relation_if_allowed(gen, "hasInputResource", "resource.water")
m.add_relation_if_allowed(gen, "hasOutputCarrier", "carrier.electricity")
gen.connect(bus)

gen.dispatch.dispatch_type = "dispatchable"
gen.dispatch.machine_role = "turbine"
gen.dispatch.turbine_efficiency = 0.90
```

`add_reservoir_hydro(...)` returns *both* entities already linked —
the `ReservoirStorageUnit` and the paired `HydroGenerationUnit`, with
`drawsFromReservoir`/`suppliesResourceTo` wired between them
automatically. Everything after that is ordinary attribute-setting on
each of the two returned proxies.

`dischargesToReservoir` (where the turbine's outflow goes — a
downstream cascade stage) is deliberately left unset here: the
outflow reaches the river directly in this example, with no modelled
downstream reservoir.

---

## Pumped hydro storage (PHS): the same pattern, reversible

```python
upper, gen = m.add_phs_closed_loop(
    "gen.phs.grimsel", "reservoir.grimsel.upper",
    lower_reservoir_id="reservoir.grimsel.lower",
    bus_id=bus, nominal_power_capacity=420.0, maximum_pumping_power=420.0,
    pumping_efficiency=0.82, turbine_efficiency=0.87,
)
lower = m.asset("reservoir.grimsel.lower")

gen.is_reversible = True
gen.turbine_type = "reversible_francis"
gen.connect(bus)
# machine_role is already set to "reversible" by add_phs_closed_loop()
```

`add_phs_closed_loop(..., lower_reservoir_id=...)` creates **three**
linked entities in one call — the upper reservoir, the lower
reservoir, and the reversible turbine — with
`drawsFromReservoir`/`suppliesResourceTo`/`dischargesToReservoir` all
wired between them. The turbine can both generate (upper → lower,
producing electricity) and pump (lower → upper, consuming it) — that's
what `is_reversible=True` and `maximum_pumping_power` describe.

---

## Result

```
=== Reservoir-Hydro example ===
GenerationUnit       1
StorageUnit          1
Validation errors: 0

=== PHS closed-loop example ===
StorageUnit          2
GenerationUnit       1
Validation errors: 0
```

---

## Run it yourself

```bash
python examples/example_hydro_reservoir_plant.py
```
