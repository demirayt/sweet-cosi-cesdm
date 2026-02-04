"""example_multienergy.py

Multi-energy (electricity + heat + gas) toy model
=================================================

What this example demonstrates
------------------------------
- How to build a CESDM model programmatically (no YAML input required)
- How to represent *multiple energy domains* and connect components across them
- How to validate and export the resulting model

Model sketch
------------
- One region: Switzerland (CH)
- Three carriers: Gas (fuel), Electricity (end-use), Heat (end-use)
- Three domains: Gas, Electricity, Heat
- One node per domain ("buses")
- One CHP (gas -> electricity + heat)
- One gas supply (exogenous gas source)
- Two loads (electricity + heat)

This is intentionally small and uses illustrative numbers.
"""

from __future__ import annotations

from pathlib import Path
import sys


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


# Make sure we can import from the repo root when running as a script.
sys.path.insert(0, str(_repo_root()))

from cesdm_toolbox import build_model_from_yaml  # noqa: E402


def build_multienergy_model(schema_dir: Path):
    """Create a small multi-energy CESDM model (explicit, no helper functions).

    This is a mechanically-expanded version of the original example where every
    entity, attribute, and relation is added explicitly (one by one).
    """
    m = build_model_from_yaml(str(schema_dir))
    m.import_library("../library/default_library.yaml")
    m.resolve_inheritance()

    # ------------------------------------------------------------------
    # Top-level container + region
    # ------------------------------------------------------------------
    m.add_entity(entity_class="EnergySystemModel", entity_id="esm")
    m.add_attribute(entity_id="esm", attribute_id="long_name", value="CH multi-energy demo (gas + electricity + heat)")

    m.add_entity(entity_class="GeographicalRegion", entity_id="CH")
    m.add_attribute(entity_id="CH", attribute_id="name", value="Switzerland")

    # ------------------------------------------------------------------
    # Carriers (EnergyCarrier) — added explicitly (no helper)
    # ------------------------------------------------------------------
    # # Gas (fuel)
    # m.add_entity(entity_class="EnergyCarrier", entity_id="gas")
    # m.add_attribute(entity_id="gas", attribute_id="name", value="Natural gas")
    # m.add_attribute(entity_id="gas", attribute_id="energy_carrier_type", value="FUEL")
    # m.add_attribute(entity_id="gas", attribute_id="energy_carrier_cost", value=60.0)
    # m.add_attribute(entity_id="gas", attribute_id="co2_emission_intensity", value=0.20)

    # # Electricity (domain carrier)
    # m.add_entity(entity_class="EnergyCarrier", entity_id="electricity")
    # m.add_attribute(entity_id="electricity", attribute_id="name", value="electricity")
    # m.add_attribute(entity_id="electricity", attribute_id="energy_carrier_type", value="DOMAIN")
    # m.add_attribute(entity_id="electricity", attribute_id="energy_carrier_cost", value=0.0)
    # m.add_attribute(entity_id="electricity", attribute_id="co2_emission_intensity", value=0.0)

    # # Heat (domain carrier)
    # m.add_entity(entity_class="EnergyCarrier", entity_id="heat")
    # m.add_attribute(entity_id="heat", attribute_id="name", value="heat")
    # m.add_attribute(entity_id="heat", attribute_id="energy_carrier_type", value="DOMAIN")
    # m.add_attribute(entity_id="heat", attribute_id="energy_carrier_cost", value=0.0)
    # m.add_attribute(entity_id="heat", attribute_id="co2_emission_intensity", value=0.0)

    # ------------------------------------------------------------------
    # Domains (EnergyDomain) — added explicitly (no helper)
    # ------------------------------------------------------------------
    m.add_entity(entity_class="EnergyDomain", entity_id="D_GAS")
    m.add_attribute(entity_id="D_GAS", attribute_id="name", value="Gas")
    m.add_relation(entity_id="D_GAS", relation_id="hasEnergyCarrier", target_entity_id="carrier.fuel.fossil.gas.natural_gas")

    m.add_entity(entity_class="EnergyDomain", entity_id="D_ELEC")
    m.add_attribute(entity_id="D_ELEC", attribute_id="name", value="Electricity")
    m.add_relation(entity_id="D_ELEC", relation_id="hasEnergyCarrier", target_entity_id="carrier.electricity")

    m.add_entity(entity_class="EnergyDomain", entity_id="D_HEAT")
    m.add_attribute(entity_id="D_HEAT", attribute_id="name", value="Heat")
    m.add_relation(entity_id="D_HEAT", relation_id="hasEnergyCarrier", target_entity_id="carrier.heat")

    # ------------------------------------------------------------------
    # Nodes (EnergyNode) — one per domain
    # ------------------------------------------------------------------
    m.add_entity(entity_class="EnergyNode", entity_id="N_CH_GAS")
    m.add_attribute(entity_id="N_CH_GAS", attribute_id="name", value="CH gas bus")
    m.add_relation(entity_id="N_CH_GAS", relation_id="isInGeographicalRegion", target_entity_id="CH")
    m.add_relation(entity_id="N_CH_GAS", relation_id="isInEnergyDomain", target_entity_id="D_GAS")

    m.add_entity(entity_class="EnergyNode", entity_id="N_CH_ELEC")
    m.add_attribute(entity_id="N_CH_ELEC", attribute_id="name", value="CH electricity bus")
    m.add_relation(entity_id="N_CH_ELEC", relation_id="isInGeographicalRegion", target_entity_id="CH")
    m.add_relation(entity_id="N_CH_ELEC", relation_id="isInEnergyDomain", target_entity_id="D_ELEC")

    m.add_entity(entity_class="EnergyNode", entity_id="N_CH_HEAT")
    m.add_attribute(entity_id="N_CH_HEAT", attribute_id="name", value="CH heat bus")
    m.add_relation(entity_id="N_CH_HEAT", relation_id="isInGeographicalRegion", target_entity_id="CH")
    m.add_relation(entity_id="N_CH_HEAT", relation_id="isInEnergyDomain", target_entity_id="D_HEAT")

    # ------------------------------------------------------------------
    # Technologies
    # ------------------------------------------------------------------
    # Exogenous gas supply (simple 1x1 pass-through: gas -> gas)
    m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="GAS_SUPPLY")
    m.add_attribute(entity_id="GAS_SUPPLY", attribute_id="name", value="Gas supply")
    m.add_attribute(entity_id="GAS_SUPPLY", attribute_id="input_origin", value="exogenous")
    # m.add_attribute(entity_id="GAS_SUPPLY", attribute_id="energy_conversion_efficiency", value=1.0)
    m.add_attribute(entity_id="GAS_SUPPLY", attribute_id="nominal_power_capacity", value=100.0)
    m.add_relation(entity_id="GAS_SUPPLY", relation_id="isOutputNodeOf", target_entity_id="N_CH_GAS")
    # m.add_relation(entity_id="GAS_SUPPLY", relation_id="hasInputEnergyCarrier", target_entity_id="gas")
    # m.add_relation(entity_id="GAS_SUPPLY", relation_id="hasOutputEnergyCarrier", target_entity_id="gas")
    m.add_relation(entity_id="GAS_SUPPLY", relation_id="instanceOf", target_entity_id="Supply.Gas")
 
    # CHP (gas -> electricity + heat)
    m.add_entity(entity_class="CombinedHeatandPowerPlant", entity_id="CHP_1")
    m.add_attribute(entity_id="CHP_1", attribute_id="name", value="CHP plant")
    # Carrier references
    m.add_relation(entity_id="CHP_1", relation_id="hasFuelCarrier", target_entity_id="carrier.fuel.fossil.gas.natural_gas")
    m.add_relation(entity_id="CHP_1", relation_id="hasElectricityAsCarrier", target_entity_id="carrier.electricity")
    m.add_relation(entity_id="CHP_1", relation_id="hasHeatAsCarrier", target_entity_id="carrier.heat")
    # Node references
    m.add_relation(entity_id="CHP_1", relation_id="isFuelInputNodeOf", target_entity_id="N_CH_GAS")
    m.add_relation(entity_id="CHP_1", relation_id="isElectricityOutputNodeOf", target_entity_id="N_CH_ELEC")
    m.add_relation(entity_id="CHP_1", relation_id="isHeatOutputNodeOf", target_entity_id="N_CH_HEAT")
    # Efficiencies + capacities (illustrative)
    m.add_attribute(entity_id="CHP_1", attribute_id="input_origin", value="endogenous")
    m.add_attribute(entity_id="CHP_1", attribute_id="net_electrical_efficiency", value=0.35)
    m.add_attribute(entity_id="CHP_1", attribute_id="net_thermal_efficiency", value=0.45)
    m.add_attribute(entity_id="CHP_1", attribute_id="rated_electrical_power_capacity", value=50.0)
    m.add_attribute(entity_id="CHP_1", attribute_id="rated_thermal_output_capacity", value=60.0)

    # ------------------------------------------------------------------
    # Loads
    # ------------------------------------------------------------------
    m.add_entity(entity_class="EnergyDemand", entity_id="LOAD_ELEC")
    m.add_attribute(entity_id="LOAD_ELEC", attribute_id="name", value="Electricity demand")
    m.add_attribute(entity_id="LOAD_ELEC", attribute_id="annual_energy_demand", value=200_000.0)
    m.add_relation(entity_id="LOAD_ELEC", relation_id="isConnectedToNode", target_entity_id="N_CH_ELEC")

    m.add_entity(entity_class="EnergyDemand", entity_id="LOAD_HEAT")
    m.add_attribute(entity_id="LOAD_HEAT", attribute_id="name", value="Heat demand")
    m.add_attribute(entity_id="LOAD_HEAT", attribute_id="annual_energy_demand", value=300_000.0)
    m.add_relation(entity_id="LOAD_HEAT", relation_id="isConnectedToNode", target_entity_id="N_CH_HEAT")

    return m
def main() -> None:
    root = _repo_root()
    schema_dir = root / "schemas"
    out_dir = root / "output" / "multienergy"
    out_dir.mkdir(parents=True, exist_ok=True)

    model = build_multienergy_model(schema_dir)

    errors = model.validate()
    if errors:
        print("Model has validation issues:")
        for e in errors:
            print("  -", e)
        raise SystemExit(1)
    print("Model validated successfully.")

    model.export_json(str(out_dir / "multienergy.json"))
    model.export_yaml(str(out_dir / "multienergy.yaml"))
    model.export_csv_by_class_wide(str(out_dir / "csv_wide"))
    model.export_long_csv(str(out_dir / "eav_long.csv"))
    print(f"Wrote outputs to: {out_dir}")


if __name__ == "__main__":
    main()
