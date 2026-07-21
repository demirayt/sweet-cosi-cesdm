#!/usr/bin/env python3
"""example_schema_extension.py

Demonstrates how to add a genuinely new entity type to CESDM *without
touching the core schema at all* -- writing a small, separate schema
tree that `extends:` the core `schemas/` directory (the same mechanism
`schemas_agentbased/` uses), then loading and using it exactly like
any built-in class. See docs/guide/03_schemas.md for the schema
authoring model this relies on.

The new type here is `ElectricVehicleChargingStation`, a controllable
electricity demand asset that doesn't correspond well to any existing
CESDM class -- along with a matching `.DispatchView` (`view_family:
dispatch`, so `.dispatch` on the proxy API resolves to it automatically,
exactly like any built-in dispatch view).

One schema-authoring practice worth noting: before defining a new
attribute, check whether one with the same meaning already exists.
`maximum_charging_power` turned out to already be a registered CESDM
attribute (added for a different asset originally) -- reused directly
below, rather than redefined. Only `number_of_charging_points` was
genuinely new.
"""

from __future__ import annotations

import os
from pathlib import Path

from cesdm_toolbox import build_model_from_yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def write_schema_extension(extension_dir: Path) -> None:
    """Write a small, self-contained schema extension to disk."""
    (extension_dir / "assets").mkdir(parents=True, exist_ok=True)
    (extension_dir / "views").mkdir(parents=True, exist_ok=True)
    (extension_dir / "attributes").mkdir(parents=True, exist_ok=True)

    # extends: is resolved relative to this manifest's own directory --
    # computed here so the example works regardless of where it's run from.
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

    # Only the genuinely new attribute -- maximum_charging_power already
    # exists in the core schema and is reused as-is below.
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


def main() -> None:
    out_dir = REPO_ROOT / "output" / "schema_extension_example"
    extension_dir = out_dir / "schemas_ev_charging"
    write_schema_extension(extension_dir)
    print(f"Wrote schema extension to {extension_dir}")

    # Loading the extension directory also pulls in every core CESDM
    # class via `extends:` -- add_bus(), add_generator(), etc. all still
    # work normally.
    model = build_model_from_yaml(extension_dir)
    print("ElectricVehicleChargingStation registered:",
          "ElectricVehicleChargingStation" in model.classes)

    bus1 = model.add_bus("bus.1", nominal_voltage=20)

    # The new class has no dedicated builder function (that's the whole
    # point of a schema-only extension -- no Python changes needed), so
    # it's built with the generic ensure_entity()/add_entity() calls, the
    # same low-level API every builder function uses internally.
    station = model.ensure_entity(
        "ElectricVehicleChargingStation", "ev.station.1",
        name="Highway rest-stop charger",
    )
    station.number_of_charging_points = 8

    model.add_entity("ElectricVehicleChargingStation.DispatchView", "dispatch.ev.station.1")
    model.add_relation("dispatch.ev.station.1", "representsAsset", "ev.station.1")
    model.add_attribute("dispatch.ev.station.1", "maximum_charging_power", 2.0)
    model.add_attribute("dispatch.ev.station.1", "annual_energy_demand", 3500)

    # SinglePort.TopologyView's representsAsset target is the base
    # EnergyAssetInstance class, so every subclass -- including this new
    # one -- can use the existing topology-connection machinery as-is.
    model.connect_single_port("ev.station.1", "bus.1")

    errors = model.validate()
    print(f"model.validate(): {len(errors)} error(s)")

    model.export_yaml_hierarchical(out_dir / "ev_charging_model.yaml")
    print(f"Wrote {out_dir / 'ev_charging_model.yaml'}")


if __name__ == "__main__":
    main()
