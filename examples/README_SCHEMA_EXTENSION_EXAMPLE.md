# `example_schema_extension.py` — Step by Step

## Why this example matters

Sooner or later, every real deployment needs an asset type CESDM
doesn't ship out of the box. The whole point of a schema-driven design
is that this shouldn't require touching the core schema or writing
new Python — this example proves it, adding
`ElectricVehicleChargingStation` end to end: write the schema files,
load them, build a model with the new class connected to a standard
`ElectricalBus`, validate, export. Zero core-schema edits, zero
Python-side class definitions.

Design background: [`docs/guide/03_schemas.md`](../docs/guide/03_schemas.md).

---

## Step 1: Write the extension's manifest

```python
core_schemas_rel = os.path.relpath(REPO_ROOT / "schemas", extension_dir)

(extension_dir / "SCHEMA_MANIFEST.yaml").write_text(f"""\
version: "0.1.0"
description: >
  Example schema extension adding ElectricVehicleChargingStation as a
  new CESDM asset type, without modifying the core schema at all.
changelog: none
extends:
  - {core_schemas_rel}
stability:
  assets: experimental
  attributes: experimental
  relations: experimental
""")
```

`extends:` is the same mechanism `schemas_agentbased/` uses to build
on the core schema — resolved relative to the manifest's own
directory, so it's computed here with `os.path.relpath` rather than
hardcoded, and works no matter where the extension directory ends up.

---

## Step 2: Check before defining a new attribute

```python
(extension_dir / "attributes" / "attributes.yaml").write_text("""\
attributes:
  number_of_charging_points:
    label: Number of Charging Points
    description: Count of individual EV charging points at the station.
    value:
      type: integer
      constraints:
        minimum: 1
""")
```

Only **one** new attribute is defined here —
`number_of_charging_points`. The obvious second candidate,
`maximum_charging_power`, turned out to already exist in the core
schema (registered originally for a different asset) — it's reused
directly in Step 4 rather than redefined. Always check
`model.global_attributes` for an existing match before adding a new
one; a duplicate definition with a different meaning is exactly the
kind of drift `docs/architecture/schema_governance.md` warns about.

---

## Step 3: Define the new entity class and its dispatch view

```python
(extension_dir / "assets" / "ElectricVehicleChargingStation.yaml").write_text("""\
name: ElectricVehicleChargingStation
parents:
  - EnergyAssetInstance
description: >
  A public or private electric-vehicle charging installation, modelled
  as a controllable electricity demand asset.
attributes:
  - id: number_of_charging_points
    required: true
relations: []
""")

(extension_dir / "views" / "ElectricVehicleChargingStation.DispatchView.yaml").write_text("""\
name: ElectricVehicleChargingStation.DispatchView
parents:
  - OperationalDispatchView
description: >
  Operational dispatch parameters for an EV charging station.
view_family: dispatch
attributes:
  - id: maximum_charging_power
    required: true
  - id: annual_energy_demand
    required: false
relations:
  - id: representsAsset
    target: ElectricVehicleChargingStation
    required: true
""")
```

Two things worth noticing:

- `parents: [EnergyAssetInstance]` — inheriting from the same base
  every core CESDM asset class does gives it `name`/`long_name`/
  `description` for free, and makes it a valid target for
  `SinglePort.TopologyView` (whose own `representsAsset.target` is
  the base `EnergyAssetInstance` class, not a specific list of named
  asset classes) — so the *existing* topology-connection machinery
  works on it with no changes at all.
- `view_family: dispatch` on the view — this is what makes `.dispatch`
  on the proxy API resolve to it automatically for this asset class,
  the exact same schema-driven mechanism every built-in dispatch view
  uses (see [`docs/architecture/proxy_api.md`](../docs/architecture/proxy_api.md)).

---

## Step 4: Load it and build a model

```python
model = build_model_from_yaml(extension_dir)
print("ElectricVehicleChargingStation registered:",
      "ElectricVehicleChargingStation" in model.classes)
# -> ElectricVehicleChargingStation registered: True

bus1 = model.add_bus("bus.1", nominal_voltage=20)

# No dedicated builder function exists for the new class -- that's the
# whole point of a schema-only extension. Built with the same
# low-level calls every builder function uses internally.
station = model.ensure_entity(
    "ElectricVehicleChargingStation", "ev.station.1",
    name="Highway rest-stop charger",
)
station.number_of_charging_points = 8

model.add_entity("ElectricVehicleChargingStation.DispatchView", "dispatch.ev.station.1")
model.add_relation("dispatch.ev.station.1", "representsAsset", "ev.station.1")
model.add_attribute("dispatch.ev.station.1", "maximum_charging_power", 2.0)
model.add_attribute("dispatch.ev.station.1", "annual_energy_demand", 3500)

model.connect_single_port("ev.station.1", "bus.1")
```

`build_model_from_yaml(extension_dir)` loads *both* the new class and
every core CESDM class in one call — `add_bus(...)` above is the
ordinary, unmodified core builder function.

---

## Step 5: Validate and export exactly like any other model

```python
errors = model.validate()
print(f"model.validate(): {len(errors)} error(s)")
# -> model.validate(): 0 error(s)

model.export_yaml_hierarchical(out_dir / "ev_charging_model.yaml")
```

The new class round-trips through the same export/import machinery
as every built-in one — nothing about it is special-cased.

---

## Run it yourself

```bash
python examples/example_schema_extension.py
```
