#!/usr/bin/env python3
"""
A tiny CESDM demo model that uses (at least once) each core energy-domain entity type.

Goal:
- Keep the system very small (2-3 electricity nodes) but still demonstrate:
  - EnergySystemModel
  - EnergyDomain
  - EnergyCarrier
  - GeographicalRegion
  - ElectricityNode / EnergyNode
  - EnergyDemand
  - EnergyConversionTechnology1x1
  - EnergyStorageTechnology
  - NetTransferCapacity
  - CombinedHeatandPowerPlant (CHP)

This script is intentionally explicit:
- every entity is created via add_entity
- every attribute via add_attribute
- every relation via add_relation
"""

from __future__ import annotations

from pathlib import Path
import sys


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


sys.path.insert(0, str(_repo_root()))

from cesdm_toolbox import build_model_from_yaml  # noqa: E402


def build_simple_model(schema_dir: Path):
    m = build_model_from_yaml(str(schema_dir))
    m.resolve_inheritance()

    # ------------------------------------------------------------------
    # 1) Root container
    # ------------------------------------------------------------------
    m.add_entity(entity_class="EnergySystemModel", entity_id="SIMPLE_DEMO")
    m.add_attribute(entity_id="SIMPLE_DEMO", attribute_id="long_name", value="Simple 3-node electricity + CHP + storage demo")
    m.add_attribute(entity_id="SIMPLE_DEMO", attribute_id="co2_price", value=100.0)

    # ------------------------------------------------------------------
    # 2) Carriers
    # ------------------------------------------------------------------
    m.add_entity(entity_class="EnergyCarrier", entity_id="Electricity")
    m.add_attribute(entity_id="Electricity", attribute_id="name", value="Electricity")
    m.add_attribute(entity_id="Electricity", attribute_id="energy_carrier_type", value="DOMAIN")
    m.add_attribute(entity_id="Electricity", attribute_id="energy_carrier_cost", value=0.0)
    m.add_attribute(entity_id="Electricity", attribute_id="co2_emission_intensity", value=0.0)

    m.add_entity(entity_class="EnergyCarrier", entity_id="Gas")
    m.add_attribute(entity_id="Gas", attribute_id="name", value="Gas")
    m.add_attribute(entity_id="Gas", attribute_id="energy_carrier_type", value="FUEL")
    m.add_attribute(entity_id="Gas", attribute_id="energy_carrier_cost", value=60.0)
    m.add_attribute(entity_id="Gas", attribute_id="co2_emission_intensity", value=0.20)

    m.add_entity(entity_class="EnergyCarrier", entity_id="Heat")
    m.add_attribute(entity_id="Heat", attribute_id="name", value="Heat")
    m.add_attribute(entity_id="Heat", attribute_id="energy_carrier_type", value="DOMAIN")
    m.add_attribute(entity_id="Heat", attribute_id="energy_carrier_cost", value=0.0)
    m.add_attribute(entity_id="Heat", attribute_id="co2_emission_intensity", value=0.0)

    m.add_entity(entity_class="EnergyCarrier", entity_id="Water")
    m.add_attribute(entity_id="Water", attribute_id="name", value="Water")
    m.add_attribute(entity_id="Water", attribute_id="energy_carrier_type", value="RESOURCE")
    m.add_attribute(entity_id="Water", attribute_id="energy_carrier_cost", value=5.0)
    m.add_attribute(entity_id="Water", attribute_id="co2_emission_intensity", value=0.0)

    # ------------------------------------------------------------------
    # 3) Domains
    # ------------------------------------------------------------------
    m.add_entity(entity_class="EnergyDomain", entity_id="ELEC")
    m.add_attribute(entity_id="ELEC", attribute_id="name", value="Electricity")
    m.add_relation(entity_id="ELEC", relation_id="hasEnergyCarrier", target_entity_id="Electricity")

    m.add_entity(entity_class="EnergyDomain", entity_id="HEAT")
    m.add_attribute(entity_id="HEAT", attribute_id="name", value="Heat")
    m.add_relation(entity_id="HEAT", relation_id="hasEnergyCarrier", target_entity_id="Heat")

    m.add_entity(entity_class="EnergyDomain", entity_id="GAS")
    m.add_attribute(entity_id="GAS", attribute_id="name", value="Gas")
    m.add_relation(entity_id="GAS", relation_id="hasEnergyCarrier", target_entity_id="Gas")

    # ------------------------------------------------------------------
    # 4) Regions (2 regions)
    # ------------------------------------------------------------------
    m.add_entity(entity_class="GeographicalRegion", entity_id="R_A")
    m.add_attribute(entity_id="R_A", attribute_id="name", value="Region A")

    m.add_entity(entity_class="GeographicalRegion", entity_id="R_B")
    m.add_attribute(entity_id="R_B", attribute_id="name", value="Region B")

    # ------------------------------------------------------------------
    # 5) Nodes
    #
    # Electricity: 3 nodes (small "3-node" network)
    # Gas + Heat: 1 node each (for CHP demonstration)
    # ------------------------------------------------------------------
    # Electricity nodes
    m.add_entity(entity_class="ElectricityNode", entity_id="N_E1")
    m.add_attribute(entity_id="N_E1", attribute_id="name", value="Electricity node E1")
    m.add_attribute(entity_id="N_E1", attribute_id="nominal_voltage", value=220.0)
    m.add_relation(entity_id="N_E1", relation_id="isInEnergyDomain", target_entity_id="ELEC")
    m.add_relation(entity_id="N_E1", relation_id="isInGeographicalRegion", target_entity_id="R_A")

    m.add_entity(entity_class="ElectricityNode", entity_id="N_E2")
    m.add_attribute(entity_id="N_E2", attribute_id="name", value="Electricity node E2")
    m.add_attribute(entity_id="N_E2", attribute_id="nominal_voltage", value=220.0)
    m.add_relation(entity_id="N_E2", relation_id="isInEnergyDomain", target_entity_id="ELEC")
    m.add_relation(entity_id="N_E2", relation_id="isInGeographicalRegion", target_entity_id="R_A")

    m.add_entity(entity_class="ElectricityNode", entity_id="N_E3")
    m.add_attribute(entity_id="N_E3", attribute_id="name", value="Electricity node E3")
    m.add_attribute(entity_id="N_E3", attribute_id="nominal_voltage", value=220.0)
    m.add_relation(entity_id="N_E3", relation_id="isInEnergyDomain", target_entity_id="ELEC")
    m.add_relation(entity_id="N_E3", relation_id="isInGeographicalRegion", target_entity_id="R_B")

    # Gas node (generic EnergyNode)
    m.add_entity(entity_class="EnergyNode", entity_id="N_G1")
    m.add_attribute(entity_id="N_G1", attribute_id="name", value="Gas node G1")
    m.add_relation(entity_id="N_G1", relation_id="isInEnergyDomain", target_entity_id="GAS")
    m.add_relation(entity_id="N_G1", relation_id="isInGeographicalRegion", target_entity_id="R_A")

    # Heat node (generic EnergyNode)
    m.add_entity(entity_class="EnergyNode", entity_id="N_H1")
    m.add_attribute(entity_id="N_H1", attribute_id="name", value="Heat node H1")
    m.add_relation(entity_id="N_H1", relation_id="isInEnergyDomain", target_entity_id="HEAT")
    m.add_relation(entity_id="N_H1", relation_id="isInGeographicalRegion", target_entity_id="R_A")

    # ------------------------------------------------------------------
    # 6) Loads (EnergyDemand)
    # ------------------------------------------------------------------
    m.add_entity(entity_class="EnergyDemand", entity_id="L_ELEC_A")
    m.add_attribute(entity_id="L_ELEC_A", attribute_id="name", value="Electricity demand in Region A")
    m.add_attribute(entity_id="L_ELEC_A", attribute_id="annual_energy_demand", value=5_000_000.0)
    m.add_relation(entity_id="L_ELEC_A", relation_id="isConnectedToNode", target_entity_id="N_E2")

    m.add_entity(entity_class="EnergyDemand", entity_id="L_HEAT_A")
    m.add_attribute(entity_id="L_HEAT_A", attribute_id="name", value="Heat demand in Region A")
    m.add_attribute(entity_id="L_HEAT_A", attribute_id="annual_energy_demand", value=3_000_000.0)
    m.add_relation(entity_id="L_HEAT_A", relation_id="isConnectedToNode", target_entity_id="N_H1")

    # ------------------------------------------------------------------
    # 7) Conversion technologies (EnergyConversionTechnology1x1)
    # ------------------------------------------------------------------
    # Gas turbine: Gas -> Electricity injected at N_E1
    m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="GT_A")
    m.add_attribute(entity_id="GT_A", attribute_id="name", value="Gas turbine A")
    m.add_attribute(entity_id="GT_A", attribute_id="generator_technology_type", value="gas")
    m.add_attribute(entity_id="GT_A", attribute_id="energy_conversion_efficiency", value=0.50)
    m.add_attribute(entity_id="GT_A", attribute_id="nominal_power_capacity", value=200.0)
    m.add_attribute(entity_id="GT_A", attribute_id="input_origin", value="exogenous")
    m.add_relation(entity_id="GT_A", relation_id="isOutputNodeOf", target_entity_id="N_E1")
    m.add_relation(entity_id="GT_A", relation_id="hasInputEnergyCarrier", target_entity_id="Gas")
    m.add_relation(entity_id="GT_A", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")

    # Run-of-river hydro: Water -> Electricity injected at N_E3
    m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="HYD_B")
    m.add_attribute(entity_id="HYD_B", attribute_id="name", value="Hydro B (run-of-river)")
    m.add_attribute(entity_id="HYD_B", attribute_id="generator_technology_type", value="hydro")
    m.add_attribute(entity_id="HYD_B", attribute_id="energy_conversion_efficiency", value=0.90)
    m.add_attribute(entity_id="HYD_B", attribute_id="nominal_power_capacity", value=150.0)
    m.add_attribute(entity_id="HYD_B", attribute_id="annual_resource_potential", value=1_500_000.0)
    m.add_attribute(entity_id="HYD_B", attribute_id="input_origin", value="exogenous")
    m.add_relation(entity_id="HYD_B", relation_id="isOutputNodeOf", target_entity_id="N_E3")
    m.add_relation(entity_id="HYD_B", relation_id="hasInputEnergyCarrier", target_entity_id="Water")
    m.add_relation(entity_id="HYD_B", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")

    # ------------------------------------------------------------------
    # 8) Storage technology (EnergyStorageTechnology)
    # ------------------------------------------------------------------
    # A simple electricity battery connected to node N_E2
    m.add_entity(entity_class="EnergyStorageTechnology", entity_id="BAT_E2")
    m.add_attribute(entity_id="BAT_E2", attribute_id="name", value="Battery at E2")
    m.add_attribute(entity_id="BAT_E2", attribute_id="energy_storage_capacity", value=500.0)
    m.add_attribute(entity_id="BAT_E2", attribute_id="nominal_power_capacity", value=100.0)
    m.add_attribute(entity_id="BAT_E2", attribute_id="maximum_charging_power", value=100.0)
    m.add_attribute(entity_id="BAT_E2", attribute_id="charging_efficiency", value=0.95)
    m.add_attribute(entity_id="BAT_E2", attribute_id="discharging_efficiency", value=0.95)
    m.add_attribute(entity_id="BAT_E2", attribute_id="initial_state_of_charge", value=0.50)
    m.add_relation(entity_id="BAT_E2", relation_id="hasInputEnergyCarrier", target_entity_id="Electricity")
    m.add_relation(entity_id="BAT_E2", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
    m.add_relation(entity_id="BAT_E2", relation_id="isConnectedToNode", target_entity_id="N_E2")

    # ------------------------------------------------------------------
    # 9) Net transfer capacities (NetTransferCapacity) between electricity nodes
    # ------------------------------------------------------------------
    # E1 <-> E2
    m.add_entity(entity_class="NetTransferCapacity", entity_id="NTC_E1_E2")
    m.add_attribute(entity_id="NTC_E1_E2", attribute_id="name", value="NTC E1-E2")
    m.add_attribute(entity_id="NTC_E1_E2", attribute_id="maximum_power_flow_1_to_2", value=300.0)
    m.add_attribute(entity_id="NTC_E1_E2", attribute_id="maximum_power_flow_2_to_1", value=300.0)
    m.add_relation(entity_id="NTC_E1_E2", relation_id="isFromNodeOf", target_entity_id="N_E1")
    m.add_relation(entity_id="NTC_E1_E2", relation_id="isToNodeOf", target_entity_id="N_E2")
    m.add_relation(entity_id="NTC_E1_E2", relation_id="isInEnergyDomain", target_entity_id="ELEC")

    # E2 <-> E3
    m.add_entity(entity_class="NetTransferCapacity", entity_id="NTC_E2_E3")
    m.add_attribute(entity_id="NTC_E2_E3", attribute_id="name", value="NTC E2-E3")
    m.add_attribute(entity_id="NTC_E2_E3", attribute_id="maximum_power_flow_1_to_2", value=200.0)
    m.add_attribute(entity_id="NTC_E2_E3", attribute_id="maximum_power_flow_2_to_1", value=200.0)
    m.add_relation(entity_id="NTC_E2_E3", relation_id="isFromNodeOf", target_entity_id="N_E2")
    m.add_relation(entity_id="NTC_E2_E3", relation_id="isToNodeOf", target_entity_id="N_E3")
    m.add_relation(entity_id="NTC_E2_E3", relation_id="isInEnergyDomain", target_entity_id="ELEC")

    # ------------------------------------------------------------------
    # 10) Multi-output technology: CombinedHeatandPowerPlant (CHP)
    # ------------------------------------------------------------------
    m.add_entity(entity_class="CombinedHeatandPowerPlant", entity_id="CHP_A")
    m.add_attribute(entity_id="CHP_A", attribute_id="name", value="CHP plant A")

    # --------------------Missing required attribute (completeness validation)---------------------------------
    # --------------------Uncomment the line below to get rid of the warning --------------------------
    # m.add_attribute(entity_id="CHP_A", attribute_id="input_origin", value="endogenous")
    # --------------------------------------------------------------------------------------------

    # --------------------Invalid enum constraint (attribute constraint validation)---------------------------------
    # --------------------Uncomment the line to test attribute constraint validation --------------------------
    m.add_attribute(entity_id="CHP_A", attribute_id="input_origin", value="endogenous")
    # --------------------------------------------------------------------------------------------

    m.add_relation(entity_id="CHP_A", relation_id="hasFuelCarrier", target_entity_id="Gas")
    # --------------------Missing required relation---------------------------------
    m.add_relation(entity_id="CHP_A", relation_id="hasElectricityAsCarrier", target_entity_id="Electricity")
    # --------------------Wrong relation ---------------------------------
    # m.add_relation(entity_id="CHP_A", relation_id="hasElectricityAsCarrier", target_entity_id="Elec")
    # --------------------Wrong relation type---------------------------------
    # m.add_relation(entity_id="CHP_A", relation_id="hasElectricityAsCarrier", target_entity_id="N_E1")
    # --------------------------------------------------------------------------------------------
    m.add_relation(entity_id="CHP_A", relation_id="hasHeatAsCarrier", target_entity_id="Heat")
    m.add_relation(entity_id="CHP_A", relation_id="isFuelInputNodeOf", target_entity_id="N_G1")
    m.add_relation(entity_id="CHP_A", relation_id="isElectricityOutputNodeOf", target_entity_id="N_E1")
    m.add_relation(entity_id="CHP_A", relation_id="isHeatOutputNodeOf", target_entity_id="N_H1")
    m.add_attribute(entity_id="CHP_A", attribute_id="net_electrical_efficiency", value=0.35)
    m.add_attribute(entity_id="CHP_A", attribute_id="net_thermal_efficiency", value=0.45)
    # -------------------- Invalid enum constraint (attribute constraint validation) ---------------------------------
    # m.add_attribute(entity_id="CHP_A", attribute_id="rated_electrical_power_capacity", value="Not_number")
    m.add_attribute(entity_id="CHP_A", attribute_id="rated_electrical_power_capacity", value=85.0)
    # --------------------------------------------------------------------------------------------
    m.add_attribute(entity_id="CHP_A", attribute_id="rated_thermal_output_capacity", value=100.0)

    return m


def main():
    root = _repo_root()
    schema_dir = root / "schemas"
    out_dir = root / "output" / "simple"
    out_dir.mkdir(parents=True, exist_ok=True)

    model = build_simple_model(schema_dir)
    errors = model.validate()
    if errors:
        print("Model has validation issues:")
        for e in errors:
            print("  -", e)
        raise SystemExit(1)
    print("Model validated successfully.")

    yaml_path = out_dir / "simple.yaml"
    model.export_yaml(str(yaml_path))
    model.export_csv_by_class_wide(str(out_dir / "csv_wide"))

    # Round-trip import (YAML -> model) to show interoperability
    m2 = build_model_from_yaml(str(schema_dir))
    m2.import_yaml(str(yaml_path))
    m2.resolve_inheritance()
    errors2 = m2.validate()
    if errors2:
        print("Round-trip model has validation issues:")
        for e in errors2:
            print("  -", e)
        raise SystemExit(1)
    print("Round-trip import validated successfully.")

    m2.export_yaml(str(out_dir / "simple_roundtrip.yaml"))
    print(f"Wrote outputs to: {out_dir}")


if __name__ == "__main__":
    main()
