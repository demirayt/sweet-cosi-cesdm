"""example_multienergy.py

Multi-energy (electricity + heat + gas) toy model — CESDM V4
=============================================================

Built with the object-oriented proxy API (`model.create_demand_unit(...)`,
`demand.dispatch.x = y`, `.connect(bus)`, ...) wherever it's covered --
see docs/architecture/proxy_api.md. See docs/getting_started.md for
the same style of model built with lower-level EAR calls instead.

Three things the object-oriented layer does not cover yet, used here
as raw low-level calls (the schema, and the low-level API underneath
it, stay fully available and powerful for exactly this kind of gap):
- Non-electrical bus classes (GasBus, HeatBus) -- only `add_bus()`
  (ElectricalBus specifically) exists as a builder today.
  `ensure_entity()` (returns an AssetProxy directly) is the closest
  equivalent.
- `ExternalSupply` has no dedicated builder either -- same treatment.
- ConversionUnit's Tier-2 MIMO ports (ConversionPort entities) -- no
  builder exists for these at all yet.

What this example demonstrates
-------------------------------
- Building a CESDM V4 model programmatically (no YAML input required)
- Multiple carrier domains and typed bus subclasses per carrier
- Cross-domain conversion (CHP: Gas → Electricity + Heat) using
  ``ConversionUnit`` + explicit ``ConversionPort`` entities
- Demand as ``DemandUnit`` + ``Demand.DispatchView``
- Simple generation as ``GenerationUnit`` + ``Generation.DispatchView``

Model sketch
------------
- One region: Switzerland (CH)
- Three carriers: Gas (fuel), Electricity, Heat
- Three CarrierDomains: D_GAS, D_ELEC, D_HEAT
- One bus per domain: GasBus, ElectricalBus, HeatBus
- One exogenous gas supply
- One CHP plant (ConversionUnit: Gas → Electricity + Heat)
- Two loads (electricity + heat demand)

------------------------------
- ``EnergyDomain``       → ``CarrierDomain``
- ``EnergyNode``         → ``GasBus`` / ``ElectricalBus`` / ``HeatBus``
- ``EnergyConversionTechnology1x1`` → ``GenerationUnit``
  + ``Generation.DispatchView`` + ``SinglePort.TopologyView``
- ``CombinedHeatandPowerPlant`` → ``ConversionUnit``
  + ``ConversionPort`` ×3 (Tier 2 MIMO: one port per physical port)
  + ``Conversion.DispatchView`` ×1 (operational parameters)
- ``EnergyDemand``       → ``DemandUnit``
  + ``Demand.DispatchView`` + ``SinglePort.TopologyView``
- ``hasEnergyCarrier``   → ``hasCarrier``
- ``isInEnergyDomain``   → ``belongsToCarrierDomain``
- ``isInGeographicalRegion`` → ``locatedIn``
- ``isOutputNodeOf``     → ``SinglePort.TopologyView.atNode``
- ``isConnectedToNode``  → ``SinglePort.TopologyView.atNode``
- CHP domain-specific topology → ``ConversionPort`` entities with ``belongsToUnit``, ``atNode`` and ``hasCarrier``
- ``instanceOf``         → ``hasTechnology``
- ``m.resolve_inheritance()`` / ``m.import_library()`` not needed in V4
- Operational attributes moved off entity identity onto dispatch views
"""

from __future__ import annotations

from pathlib import Path
import sys

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]

sys.path.insert(0, str(_repo_root()))

from cesdm_toolbox import build_model_from_yaml, CesdmModel  # noqa: E402
from cesdm.generated_proxies import ExternalSupplyProxy  # noqa: E402

def build_multienergy_model(schema_dir: Path) -> CesdmModel:
    """Create a small multi-energy CESDM V4 model."""
    m = build_model_from_yaml(str(schema_dir))

    # ------------------------------------------------------------------
    # Top-level container + region
    # ------------------------------------------------------------------
    m.add_entity("EnergySystemModel", "esm")
    m.add_attribute("esm", "long_name",
                    "CH multi-energy demo (gas + electricity + heat)")

    m.ensure_entity("GeographicalRegion", "CH", name="Switzerland")

    # ------------------------------------------------------------------
    # EnergyCarrier -- ensure_carrier() (proxy-returning)
    # ------------------------------------------------------------------
    for eid, name, co2, cost in [
        ("carrier.gas",         "Natural gas",  0.20, 60.0),
        ("carrier.electricity", "Electricity",  0.0,   0.0),
        ("carrier.heat",        "Heat",         0.0,   0.0),
    ]:
        carrier = m.ensure_carrier(eid, name=name)
        m.set_attribute_if_allowed(carrier, "co2_emission_intensity", co2)
        m.set_attribute_if_allowed(carrier, "energy_carrier_cost", cost)

    # ------------------------------------------------------------------
    # CarrierDomain -- no dedicated builder; ensure_entity() returns an
    # AssetProxy directly.
    # ------------------------------------------------------------------
    for did, name, carrier in [
        ("D_GAS",  "Gas",         "carrier.gas"),
        ("D_ELEC", "Electricity", "carrier.electricity"),
        ("D_HEAT", "Heat",        "carrier.heat"),
    ]:
        domain = m.ensure_entity("CarrierDomain", did, name=name)
        m.add_relation_if_allowed(domain, "hasCarrier", carrier)

    # ------------------------------------------------------------------
    # Buses — one typed bus per domain. ElectricalBus has a dedicated
    # builder (add_bus); GasBus/HeatBus don't yet, so ensure_entity() is
    # the closest object-oriented equivalent for those two.
    # ------------------------------------------------------------------
    n_gas = m.ensure_entity("GasBus", "N_CH_GAS", name="CH gas bus")
    m.add_relation_if_allowed(n_gas, "belongsToCarrierDomain", "D_GAS")
    m.add_relation_if_allowed(n_gas, "locatedIn", "CH")

    n_elec = m.add_bus("N_CH_ELEC", region_id="CH", carrier_domain_id="D_ELEC")
    m.set_attribute_if_allowed(n_elec, "name", "CH electricity bus")

    n_heat = m.ensure_entity("HeatBus", "N_CH_HEAT", name="CH heat bus")
    m.add_relation_if_allowed(n_heat, "belongsToCarrierDomain", "D_HEAT")
    m.add_relation_if_allowed(n_heat, "locatedIn", "CH")

    # ------------------------------------------------------------------
    # Exogenous gas supply -- no dedicated builder for ExternalSupply
    # exists yet; ensure_entity() + .connect() is the closest
    # object-oriented equivalent.
    # ------------------------------------------------------------------
    gas_supply = m.asset_as(
        m.ensure_entity("ExternalSupply", "GAS_SUPPLY", name="Gas supply"),
        ExternalSupplyProxy,
    )
    m.add_relation_if_allowed(gas_supply, "hasOutputCarrier", "carrier.gas")
    gas_supply.connect(n_gas)

    supply_view = gas_supply.dispatch
    supply_view.is_slack = True
    supply_view.supply_capacity = 1e6

    # ------------------------------------------------------------------
    # CHP plant: Gas → Electricity + Heat  (Tier 2 MIMO representation)
    #
    #   No proxy-API builder exists yet for ConversionUnit's Tier-2 MIMO
    #   ports (one ConversionPort entity per physical port) -- this
    #   section stays on the raw low-level API, matching the "schema
    #   stays powerful, use the low-level API for the long tail" design
    #   (docs/architecture/proxy_api.md, "What this does not do (yet)").
    #
    #   Tier 2 uses explicit ConversionPort entities — one per physical port.
    #   The gas input port is the reference port (flow_coefficient = -1.0).
    #   All other port flows are expressed as ratios to the reference.
    #
    #   Ports:
    #     port.CHP_1.gas_in    input   Gas bus   flow_coeff = -1.00 (reference)
    #     port.CHP_1.elec_out  output  Elec bus  flow_coeff = +0.35 (η_elec)
    #     port.CHP_1.heat_out  output  Heat bus  flow_coeff = +0.45 (η_heat)
    #
    #   Conversion.DispatchView only declares dispatch participation.
    #   The port entities carry the conversion semantics.
    # ------------------------------------------------------------------
    m.add_entity("ConversionUnit", "CHP_1")
    m.add_attribute("CHP_1", "name", "CHP plant")

    # ── Tier 2: ConversionPort entities ───────────────────────────────────
    # Reference port: gas input (flow_coefficient = -1.0, negative = withdrawal)
    m.add_entity("ConversionPort", "port.CHP_1.gas_in")
    m.add_attribute("port.CHP_1.gas_in", "port_direction",    "input")
    m.add_attribute("port.CHP_1.gas_in", "flow_coefficient",  -1.0)
    m.add_attribute("port.CHP_1.gas_in", "is_reference_port",  True)
    m.add_relation("port.CHP_1.gas_in",  "belongsToUnit",     "CHP_1")
    m.add_relation("port.CHP_1.gas_in",  "atNode",            n_gas)
    m.add_relation("port.CHP_1.gas_in",  "hasCarrier",        "carrier.gas")

    # Electricity output port
    m.add_entity("ConversionPort", "port.CHP_1.elec_out")
    m.add_attribute("port.CHP_1.elec_out", "port_direction",    "output")
    m.add_attribute("port.CHP_1.elec_out", "flow_coefficient",   0.35)
    m.add_attribute("port.CHP_1.elec_out", "maximum_output_power", 35.0)
    m.add_attribute("port.CHP_1.elec_out", "is_reference_port",  False)
    m.add_relation("port.CHP_1.elec_out",  "belongsToUnit",     "CHP_1")
    m.add_relation("port.CHP_1.elec_out",  "atNode",            n_elec)
    m.add_relation("port.CHP_1.elec_out",  "hasCarrier",        "carrier.electricity")

    # Heat output port
    m.add_entity("ConversionPort", "port.CHP_1.heat_out")
    m.add_attribute("port.CHP_1.heat_out", "port_direction",    "output")
    m.add_attribute("port.CHP_1.heat_out", "flow_coefficient",   0.45)
    m.add_attribute("port.CHP_1.heat_out", "maximum_output_power", 45.0)
    m.add_attribute("port.CHP_1.heat_out", "is_reference_port",  False)
    m.add_relation("port.CHP_1.heat_out",  "belongsToUnit",     "CHP_1")
    m.add_relation("port.CHP_1.heat_out",  "atNode",            n_heat)
    m.add_relation("port.CHP_1.heat_out",  "hasCarrier",        "carrier.heat")

    # ── Operational parameters (one view for the whole unit) ───────────────
    dv_chp = "conversion_dispatch_view.CHP_1"
    m.add_entity("Conversion.DispatchView", dv_chp)
    m.add_relation(dv_chp, "representsAsset",   "CHP_1")

    # ------------------------------------------------------------------
    # Demand: electricity + heat -- create_demand_unit() (proxy-returning)
    # ------------------------------------------------------------------
    for lid, name, demand_mwh, node in [
        ("LOAD_ELEC", "Electricity demand", 200_000.0, n_elec),
        ("LOAD_HEAT", "Heat demand",        300_000.0, n_heat),
    ]:
        load = m.create_demand_unit(lid, bus_id=node, carrier_id=None)
        m.set_attribute_if_allowed(load, "name", name)
        load.dispatch.annual_energy_demand = demand_mwh

    return m

def main() -> None:
    root       = _repo_root()
    schema_dir = root / "schemas"
    out_dir    = root / "output" / "multienergy" / "cesdm"
    out_dir.mkdir(parents=True, exist_ok=True)

    model  = build_multienergy_model(schema_dir)

    print(model.summary())
    print()

    errors = model.validate()
    if errors:
        print("Model has validation issues:")
        for e in errors:
            print("  -", e)
    else:
        print("Model validated successfully.")

    # Hierarchical YAML — representations nested under each asset
    model.export_yaml_hierarchical(out_dir / "yaml" / "multienergy_hierarchical.yaml")

    # Flat YAML — one section per class
    model.export_yaml(out_dir/ "yaml" / "multienergy_flat.yaml")

    # Frictionless Data Package — self-describing, one CSV per class
    model.export_frictionless(
        out_dir / "frictionless",
        name  = "cesdm-multienergy-demo",
        title = "Multi-energy CESDM Demo Model",
    )

    print(f"Wrote outputs to: {out_dir}")
    print(f"  {out_dir / 'yaml' / 'multienergy_hierarchical.yaml'}")
    print(f"  {out_dir / 'yaml' / 'multienergy_flat.yaml'}")
    print(f"  {out_dir / 'frictionless' / 'datapackage.json'}")

if __name__ == "__main__":
    main()
