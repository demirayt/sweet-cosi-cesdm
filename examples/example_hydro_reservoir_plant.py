#!/usr/bin/env python3
"""
Example: reservoir hydro modelled with direct reservoir/generator assets,
built with the object-oriented proxy API's dedicated composite builders
(`add_reservoir_hydro`, `add_phs_closed_loop`) -- see
docs/architecture/proxy_api.md. See docs/getting_started.md for the
same style of model built with lower-level EAR calls instead.

HydroGenerationUnit assets link directly to ReservoirStorageUnit assets:
  - drawsFromReservoir: upper/source reservoir used for generation
  - dischargesToReservoir: lower/downstream reservoir where modelled
  - suppliesResourceTo: inverse link from reservoir to generator

No HydroPowerPlant wrapper is required. `add_reservoir_hydro()` and
`add_phs_closed_loop()` create both entities plus this composite
relation pairing in one call.
"""
from pathlib import Path
import sys

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]

_REPO_ROOT = _repo_root()
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
HERE = Path(__file__).resolve().parent

from cesdm_toolbox import build_model_from_yaml


def build_example(schema_dir: Path, library_path: Path):
    m = build_model_from_yaml(str(schema_dir))
    m.import_library(str(library_path))

    ELEC  = "carrier.electricity"
    WATER = "resource.water"

    domain = m.ensure_entity("CarrierDomain", "domain.electricity")
    m.add_relation_if_allowed(domain, "hasCarrier", ELEC)

    m.ensure_entity("GeographicalRegion", "region.ch", name="Switzerland")

    bus = m.add_bus("bus.ch", nominal_voltage=380.0,
                    region_id="region.ch", carrier_domain_id="domain.electricity")
    m.set_attribute_if_allowed(bus, "name", "Swiss 380kV bus")

    # ── Direct reservoir ↔ generator linkage (no HydroPowerPlant wrapper) ──
    # add_reservoir_hydro() creates the ReservoirStorageUnit + the paired
    # HydroGenerationUnit + the drawsFromReservoir/suppliesResourceTo
    # relation pairing, all in one call.
    reservoir, gen = m.add_reservoir_hydro(
        "gen.hydro.alpine", "reservoir.alpine", bus_id=bus,
        nominal_power_capacity=500.0, energy_storage_capacity=2500.0,
    )
    m.set_attribute_if_allowed(reservoir, "name", "Alpine reservoir")
    m.add_relation_if_allowed(reservoir, "storesResource", WATER)
    reservoir.dispatch.annual_natural_inflow_energy = 900_000.0

    m.set_attribute_if_allowed(gen, "name", "Alpine hydro turbine")
    m.set_attribute_if_allowed(gen, "is_reversible", False)
    m.add_relation_if_allowed(gen, "hasInputResource", WATER)
    m.add_relation_if_allowed(gen, "hasOutputCarrier", ELEC)
    gen.connect(bus)

    # dischargesToReservoir: where the turbine outflow goes (cascade
    # stage) -- for this example the outflow reaches the river directly,
    # no downstream reservoir modelled, so this is left unset.
    gen.dispatch.dispatch_type = "dispatchable"
    gen.dispatch.machine_role = "turbine"
    gen.dispatch.turbine_efficiency = 0.90
    gen.dispatch.annual_resource_potential = 900_000.0

    return m


def build_phs_example(schema_dir: Path, library_path: Path):
    """PHS closed-loop: same structure as reservoir-hydro, is_reversible=True."""
    m = build_model_from_yaml(str(schema_dir))
    m.import_library(str(library_path))

    ELEC  = "carrier.electricity"
    WATER = "resource.water"

    domain = m.ensure_entity("CarrierDomain", "domain.electricity")
    m.add_relation_if_allowed(domain, "hasCarrier", ELEC)
    m.ensure_entity("GeographicalRegion", "region.ch")
    bus = m.add_bus("bus.ch", region_id="region.ch", carrier_domain_id="domain.electricity")

    # add_phs_closed_loop() creates BOTH the upper and lower
    # ReservoirStorageUnit (when lower_reservoir_id is given) plus the
    # paired reversible HydroGenerationUnit and drawsFromReservoir/
    # suppliesResourceTo/dischargesToReservoir relations, all in one call.
    upper, gen = m.add_phs_closed_loop(
        "gen.phs.grimsel", "reservoir.grimsel.upper", lower_reservoir_id="reservoir.grimsel.lower",
        bus_id=bus, nominal_power_capacity=420.0, maximum_pumping_power=420.0,
        pumping_efficiency=0.82, turbine_efficiency=0.87,
    )
    lower = m.asset("reservoir.grimsel.lower")
    m.add_relation_if_allowed(lower, "storesResource", WATER)
    m.add_relation_if_allowed(upper, "storesResource", WATER)
    upper.dispatch.energy_storage_capacity = 1200.0

    m.set_attribute_if_allowed(gen, "name", "Grimsel reversible pump-turbine")
    m.set_attribute_if_allowed(gen, "is_reversible", True)
    m.set_attribute_if_allowed(gen, "turbine_type", "reversible_francis")
    m.add_relation_if_allowed(gen, "hasInputResource", WATER)
    m.add_relation_if_allowed(gen, "hasOutputCarrier", ELEC)
    gen.connect(bus)
    gen.dispatch.dispatch_type = "dispatchable"
    # machine_role is already set to "reversible" by add_phs_closed_loop()

    return m


if __name__ == "__main__":
    schema_dir   = HERE.parent / "schemas"
    library_path = HERE.parent / "library" / "default_library"

    print("=== Reservoir-Hydro example ===")
    model = build_example(schema_dir, library_path)
    print(model.summary())
    errors = model.validate()
    print(f"Validation errors: {len(errors)}")
    for error in errors[:20]:
        print(" -", error)
    print("Hydro reservoir composite example built.")

    print("\n=== PHS closed-loop example ===")
    phs_model = build_phs_example(schema_dir, library_path)
    print(phs_model.summary())
    phs_errors = phs_model.validate()
    print(f"Validation errors: {len(phs_errors)}")
    for error in phs_errors[:20]:
        print(" -", error)
    print("PHS closed-loop composite example built.")
