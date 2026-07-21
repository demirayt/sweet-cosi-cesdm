#!/usr/bin/env python3
"""example_simple.py

A tiny CESDM V4 demo model using each core energy-domain entity type,
built with the object-oriented proxy API (`model.add_generator(...)`,
`gen.dispatch.x = y`, `gen.connect(bus)`, ...) wherever it's covered --
see docs/architecture/proxy_api.md. See docs/getting_started.md for
the same style of model built with lower-level EAR calls instead.

Two things the object-oriented layer does not cover yet, used here as-is:
- Non-electrical bus classes (GasBus, HeatBus, HydrogenBus) -- only
  `add_bus()` (ElectricalBus specifically) exists as a builder today.
  `model.ensure_entity(...)` + `model.asset(...)` is the closest
  equivalent, and is used below.
- ConversionUnit's Tier-2 MIMO ports (ConversionPort entities) -- there
  is no builder for these at all yet, so this section is still raw
  add_entity/add_attribute/add_relation, matching the "schema stays
  powerful, use the low-level API for the long tail" design.

Goal
----
Keep the system very small (3 electricity nodes) but demonstrate every
V4 entity class at least once:

  EnergySystemModel, EnergyCarrier, CarrierDomain,
  GeographicalRegion, ElectricalBus, GasBus, HeatBus,
  DemandUnit + Demand.DispatchView,
  GenerationUnit + Generation.DispatchView + SinglePort.TopologyView,
  StorageUnit + Storage.DispatchView + SinglePort.TopologyView,
  TransmissionElement + TwoPort.TopologyView + TransmissionLine.PowerFlowView,
  ConversionUnit + ConversionPort ×3 (Tier 2 MIMO) + Conversion.DispatchView (operational)

V4 design rules applied throughout
------------------------------------
- Asset identity entities carry only ``name`` + optional ``hasTechnology``
- All operational/physical attributes live on typed representation views
- Profile references use ``hasDemandProfile`` / ``hasAvailabilityProfile``
  relations pointing to ``Profile`` entities (not plain string attributes)
- ``CarrierDomain`` replaces ``EnergyDomain``
- ``ElectricalBus`` / ``GasBus`` / ``HeatBus`` replace the generic
  ``ElectricityNode`` / ``EnergyNode`` with carrier-specific typed nodes
- ``belongsToCarrierDomain`` replaces ``isInEnergyDomain``
- ``locatedIn`` replaces ``isInGeographicalRegion``
- ``atNode`` on ``SinglePort.TopologyView`` replaces ``isOutputNodeOf`` /
  ``isConnectedToNode``
- ``fromNode`` / ``toNode`` on ``TwoPort.TopologyView`` replace
  ``isFromNodeOf`` / ``isToNodeOf``
- ``hasTechnology`` replaces ``instanceOf``
- carrier relations are represented through ConversionPort.hasCarrier for ConversionUnit examples;
  ``hasInputEnergyCarrier`` / ``hasOutputEnergyCarrier``
"""

from __future__ import annotations

from pathlib import Path
import sys

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]

sys.path.insert(0, str(_repo_root()))

from cesdm_toolbox import build_model_from_yaml, CesdmModel  # noqa: E402

def build_simple_model(schema_dir: Path) -> CesdmModel:
    m = build_model_from_yaml(str(schema_dir))

    # ------------------------------------------------------------------
    # 1) Root container
    # ------------------------------------------------------------------
    m.add_energy_system_model(
        "SIMPLE_DEMO",
        long_name="Simple 3-node electricity + CHP + storage demo",
        co2_price=100.0,
    )

    # ------------------------------------------------------------------
    # 2) EnergyCarrier entities, via ensure_carrier() (proxy-returning)
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # 3) CarrierDomain entities through the generated API.
    # ------------------------------------------------------------------
    for did, name, carrier in [
        ("ELEC", "Electricity", "Electricity"),
        ("HEAT", "Heat",        "Heat"),
        ("GAS",  "Gas",         "Gas"),
    ]:
        m.add_carrier_domain(
            did, name=name, hasCarrier=m.asset(carrier)
        )

    # ------------------------------------------------------------------
    # 4) GeographicalRegion
    # ------------------------------------------------------------------
    for rid, name in [("R_A", "Region A"), ("R_B", "Region B")]:
        m.add_geographical_region(rid, name=name)

    # ------------------------------------------------------------------
    # 5) Buses
    # ------------------------------------------------------------------
    # Three ElectricalBus nodes (small 3-node electricity network) --
    # add_bus() is the proxy-returning builder for this class.
    n_e1 = m.add_bus("N_E1", nominal_voltage=220.0, region_id="R_A", carrier_domain_id="ELEC")
    n_e2 = m.add_bus("N_E2", nominal_voltage=220.0, region_id="R_A", carrier_domain_id="ELEC")
    n_e3 = m.add_bus("N_E3", nominal_voltage=220.0, region_id="R_B", carrier_domain_id="ELEC")
    for bus, name in [(n_e1, "Electricity node E1"), (n_e2, "Electricity node E2"),
                      (n_e3, "Electricity node E3")]:
        bus.name = name

    n_g1 = m.add_gas_bus(
        "N_G1", name="Gas node G1",
        belongsToCarrierDomain=m.asset("GAS"), locatedIn=m.asset("R_A"),
    )
    n_h1 = m.add_heat_bus(
        "N_H1", name="Heat node H1",
        belongsToCarrierDomain=m.asset("HEAT"), locatedIn=m.asset("R_A"),
    )

    # ------------------------------------------------------------------
    # 6) DemandUnit -- create_demand_unit() (proxy-returning), then
    #    demand.dispatch.x = y and demand.connect(bus)
    # ------------------------------------------------------------------
    demand_elec = m.create_demand_unit("L_ELEC_A", bus_id=n_e2)
    demand_elec.name="Electricity demand in Region A"
    demand_elec.dispatch.annual_energy_demand = 5_000_000.0

    demand_heat = m.create_demand_unit("L_HEAT_A", bus_id=n_h1)
    demand_heat.name="Heat demand in Region A"
    demand_heat.dispatch.annual_energy_demand = 3_000_000.0

    # ------------------------------------------------------------------
    # 7) GenerationUnit -- no specific technology template is being
    #    used here (the original demo assigns carriers directly, not a
    #    technology), so create_generation_unit() (the lower-level of the
    #    two proxy-returning generator builders) is the right fit, not
    #    add_generator(technology=...).
    # ------------------------------------------------------------------
    # Gas turbine: Gas -> Electricity at N_E1
    gt_a = m.create_generation_unit(
        "GT_A", bus_id=n_e1,
        input_carrier_id="Gas", output_carrier_id="Electricity",
    )
    gt_a.name="Gas turbine A"
    gt_a.dispatch.generator_technology_type = "gas"
    gt_a.dispatch.energy_conversion_efficiency = 0.50
    gt_a.dispatch.nominal_power_capacity = 200.0

    # Run-of-river hydro: Water -> Electricity at N_E3. Nondispatchable,
    # so this uses HydroGenerationUnit.DispatchView with dispatch_type
    # set explicitly (reservoir-coupled dispatchable units would use a
    # different view family entirely -- see add_reservoir_hydro()).
    hyd_b = m.create_generation_unit(
        "HYD_B", class_name="HydroGenerationUnit", bus_id=n_e3,
        input_carrier_id="Water", output_carrier_id="Electricity",
        dispatch_view_class="HydroGenerationUnit.DispatchView",
    )
    hyd_b.name="Hydro B (run-of-river)"
    hyd_b.dispatch.dispatch_type = "nondispatchable"
    hyd_b.dispatch.turbine_efficiency = 0.90
    hyd_b.dispatch.nominal_power_capacity = 150.0
    hyd_b.dispatch.annual_resource_potential = 1_500_000.0

    # ------------------------------------------------------------------
    # 8) StorageUnit -- create_storage_unit() (proxy-returning)
    # ------------------------------------------------------------------
    bat_e2 = m.create_storage_unit("BAT_E2", bus_id=n_e2, carrier_id="Electricity")
    bat_e2.name="Battery at E2"
    bat_e2.dispatch.energy_storage_capacity = 500.0
    bat_e2.dispatch.nominal_power_capacity = 100.0
    bat_e2.dispatch.maximum_charging_power = 100.0
    bat_e2.dispatch.charging_efficiency = 0.95
    bat_e2.dispatch.discharging_efficiency = 0.95
    bat_e2.dispatch.initial_state_of_charge = 0.50

    # ------------------------------------------------------------------
    # 9) Interconnectors through the generated API and typed views.
    # ------------------------------------------------------------------
    for ntc_id, name, frm, to, p12, p21 in [
        ("NTC_E1_E2", "NTC E1-E2", n_e1, n_e2, 300.0, 300.0),
        ("NTC_E2_E3", "NTC E2-E3", n_e2, n_e3, 200.0, 200.0),
    ]:
        ntc = m.add_interconnector(ntc_id, name=name)
        ntc.connect(frm, to)  # TwoPort.TopologyView / fromNode+toNode
        pv = ntc.powerflow
        pv.maximum_power_flow_from_to = p12
        pv.maximum_power_flow_to_from = p21

    # ------------------------------------------------------------------
    # 10) ConversionUnit — Tier 2 MIMO: PEM Fuel Cell (H2 + Air → Elec + Heat)
    #
    #   No proxy-API builder exists yet for ConversionUnit's Tier-2 MIMO
    #   ports (one ConversionPort entity per physical port) -- this
    #   section stays on the raw low-level API, exactly as it should:
    #   the object-oriented layer covers the common cases, the schema
    #   (and the low-level API underneath it) stays available and fully
    #   powerful for everything else. See docs/architecture/proxy_api.md,
    #   "What this does not do (yet)".
    #
    #   Ports:
    #     port.FC_A.h2_in    input   H2 bus     flow_coeff = -1.00  (reference)
    #     port.FC_A.air_in   input   (lumped)   flow_coeff = -0.30  (air consumed)
    #     port.FC_A.elec_out output  elec bus   flow_coeff = +0.55
    #     port.FC_A.heat_out output  heat bus   flow_coeff = +0.30
    #
    #   Conversion.DispatchView only declares dispatch participation.
    #   Port-level coefficients and the is_reference_port flag define the
    #   conversion ratios and reference scale.
    # ------------------------------------------------------------------

    # We reuse the existing carriers and add H2 for this demo
    m.ensure_carrier("H2", name="Hydrogen")
    h2 = m.asset("H2")
    h2.co2_emission_intensity = 0.0

    # H2 bus (new for the fuel cell)
    n_h2 = m.add_hydrogen_bus("N_H2", name="H2 bus")

    # Asset identity
    fuel_cell = m.add_conversion_unit("FC_A", name="PEM Fuel Cell A")

    # ── Tier 2: ConversionPort entities ───────────────────────────────────
    # Reference port: H2 input (flow_coefficient = -1.0, negative = withdrawal)
    m.add_conversion_port(
        "port.FC_A.h2_in", port_direction="input", flow_coefficient=-1.0,
        is_reference_port=True, belongsToUnit=fuel_cell, atNode=n_h2,
        hasCarrier=h2,
    )

    # Electricity output port
    m.add_conversion_port(
        "port.FC_A.elec_out", port_direction="output", flow_coefficient=0.55,
        maximum_output_power=55.0, is_reference_port=False,
        belongsToUnit=fuel_cell, atNode=n_e1, hasCarrier=m.asset("Electricity"),
    )

    # Heat output port
    m.add_conversion_port(
        "port.FC_A.heat_out", port_direction="output", flow_coefficient=0.30,
        maximum_output_power=30.0, is_reference_port=False,
        belongsToUnit=fuel_cell, atNode=n_h1, hasCarrier=m.asset("Heat"),
    )

    # ── Operational parameters (one view for the whole unit) ───────────────
    m.add_conversion_dispatch_view(
        "conversion_dispatch_view.FC_A", representsAsset=fuel_cell
    )

    return m

def main():
    root       = _repo_root()
    schema_dir = root / "schemas"
    out_dir    = root / "output" / "simple" / "cesdm"
    out_dir.mkdir(parents=True, exist_ok=True)

    model  = build_simple_model(schema_dir)

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
    model.export_yaml_hierarchical(out_dir / "yaml" / "simple_hierarchical.yaml")

    # Flat YAML — one section per class
    model.export_yaml(out_dir / "yaml" / "simple_flat.yaml")

    # Frictionless Data Package — self-describing, one CSV per class
    model.export_frictionless(
        out_dir / "frictionless",
        name  = "cesdm-simple-demo",
        title = "Simple CESDM Demo Model",
    )

    print(f"Wrote outputs to: {out_dir}")
    print(f"  {out_dir / 'yaml' / 'simple_hierarchical.yaml'}")
    print(f"  {out_dir / 'yaml' / 'simple_flat.yaml'}")
    print(f"  {out_dir / 'frictionless' / 'datapackage.json'}")

if __name__ == "__main__":
    main()
