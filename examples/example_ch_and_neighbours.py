"""example_ch_and_neighbours.py

Switzerland + neighbours (electricity only) demo
================================================

This example is intentionally *didactic* rather than data-accurate.

What this example demonstrates
------------------------------
- How to create a multi-region electricity model (regions, nodes, loads)
- How to add a handful of generator fleets with different carriers (gas, water, uranium)
- How to represent cross-border interconnectors with ``NetTransferCapacity``
- How to validate, export, and round-trip import a model

Design choices (for clarity)
----------------------------
- One electricity bus (node) per country
- Aggregated annual demand per country (single ``EnergyDemand``)
- Aggregated generator fleets (one entity per technology per country)
- Interconnectors only between Switzerland and each neighbour

Run
---
    python examples/example_ch_and_neighbours.py

Outputs are written to ``./output/ch_and_neighbours``.
"""

from __future__ import annotations

from pathlib import Path
import sys


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


sys.path.insert(0, str(_repo_root()))

from cesdm_toolbox import build_model_from_yaml  # noqa: E402



def build_model(schema_dir: Path):
    """Build the CH + neighbours demo model *without helper functions*.

    This is a mechanically-expanded version of the original example where every
    entity, attribute, and relation is added explicitly (one by one), to make the
    schema-driven construction process maximally transparent.
    """
    m = build_model_from_yaml(str(schema_dir))
    m.import_library("../library/default_library.yaml")
    m.resolve_inheritance()

    # ------------------------------------------------------------------
    # Top-level container
    # ------------------------------------------------------------------
    m.add_entity(entity_class="EnergySystemModel", entity_id="CH_NEIGHBOURS")
    m.add_attribute(entity_id="CH_NEIGHBOURS", attribute_id="long_name", value="CH + neighbours (electricity only) demo")
    m.add_attribute(entity_id="CH_NEIGHBOURS", attribute_id="co2_price", value=120.0)

    # ------------------------------------------------------------------
    # Carriers
    # ------------------------------------------------------------------
    m.add_entity(entity_class="EnergyCarrier", entity_id="Electricity")
    m.add_attribute(entity_id="Electricity", attribute_id="name", value="Electricity")
    m.add_attribute(entity_id="Electricity", attribute_id="energy_carrier_type", value="DOMAIN")
    m.add_attribute(entity_id="Electricity", attribute_id="energy_carrier_cost", value=0.0)
    m.add_attribute(entity_id="Electricity", attribute_id="co2_emission_intensity", value=0.0)

    m.add_entity(entity_class="EnergyCarrier", entity_id="Gas")
    m.add_attribute(entity_id="Gas", attribute_id="name", value="Gas")
    m.add_attribute(entity_id="Gas", attribute_id="energy_carrier_type", value="FUEL")
    m.add_attribute(entity_id="Gas", attribute_id="energy_carrier_cost", value=50.0)
    m.add_attribute(entity_id="Gas", attribute_id="co2_emission_intensity", value=0.20)

    m.add_entity(entity_class="EnergyCarrier", entity_id="Water")
    m.add_attribute(entity_id="Water", attribute_id="name", value="Water")
    m.add_attribute(entity_id="Water", attribute_id="energy_carrier_type", value="RESOURCE")
    m.add_attribute(entity_id="Water", attribute_id="energy_carrier_cost", value=5.0)
    m.add_attribute(entity_id="Water", attribute_id="co2_emission_intensity", value=0.0)

    m.add_entity(entity_class="EnergyCarrier", entity_id="Uranium")
    m.add_attribute(entity_id="Uranium", attribute_id="name", value="Uranium")
    m.add_attribute(entity_id="Uranium", attribute_id="energy_carrier_type", value="FUEL")
    m.add_attribute(entity_id="Uranium", attribute_id="energy_carrier_cost", value=10.0)
    m.add_attribute(entity_id="Uranium", attribute_id="co2_emission_intensity", value=0.0)

    # ------------------------------------------------------------------
    # Energy domain
    # ------------------------------------------------------------------
    m.add_entity(entity_class="EnergyDomain", entity_id="ELEC")
    m.add_attribute(entity_id="ELEC", attribute_id="name", value="Electricity")
    m.add_relation(entity_id="ELEC", relation_id="hasEnergyCarrier", target_entity_id="Electricity")

    # ------------------------------------------------------------------
    # Regions (GeographicalRegion)
    # ------------------------------------------------------------------
    m.add_entity(entity_class="GeographicalRegion", entity_id="R_CH")
    m.add_attribute(entity_id="R_CH", attribute_id="name", value="Switzerland")

    m.add_entity(entity_class="GeographicalRegion", entity_id="R_DE")
    m.add_attribute(entity_id="R_DE", attribute_id="name", value="Germany")

    m.add_entity(entity_class="GeographicalRegion", entity_id="R_FR")
    m.add_attribute(entity_id="R_FR", attribute_id="name", value="France")

    m.add_entity(entity_class="GeographicalRegion", entity_id="R_IT")
    m.add_attribute(entity_id="R_IT", attribute_id="name", value="Italy")

    m.add_entity(entity_class="GeographicalRegion", entity_id="R_AT")
    m.add_attribute(entity_id="R_AT", attribute_id="name", value="Austria")

    m.add_entity(entity_class="GeographicalRegion", entity_id="R_LI")
    m.add_attribute(entity_id="R_LI", attribute_id="name", value="Liechtenstein")

    # ------------------------------------------------------------------
    # Nodes (ElectricityNode) — one per country
    # ------------------------------------------------------------------
    m.add_entity(entity_class="ElectricityNode", entity_id="N_CH")
    m.add_attribute(entity_id="N_CH", attribute_id="name", value="CH electricity bus")
    m.add_attribute(entity_id="N_CH", attribute_id="nominal_voltage", value=220.0)
    m.add_relation(entity_id="N_CH", relation_id="isInEnergyDomain", target_entity_id="ELEC")
    m.add_relation(entity_id="N_CH", relation_id="isInGeographicalRegion", target_entity_id="R_CH")

    m.add_entity(entity_class="ElectricityNode", entity_id="N_DE")
    m.add_attribute(entity_id="N_DE", attribute_id="name", value="DE electricity bus")
    m.add_attribute(entity_id="N_DE", attribute_id="nominal_voltage", value=220.0)
    m.add_relation(entity_id="N_DE", relation_id="isInEnergyDomain", target_entity_id="ELEC")
    m.add_relation(entity_id="N_DE", relation_id="isInGeographicalRegion", target_entity_id="R_DE")

    m.add_entity(entity_class="ElectricityNode", entity_id="N_FR")
    m.add_attribute(entity_id="N_FR", attribute_id="name", value="FR electricity bus")
    m.add_attribute(entity_id="N_FR", attribute_id="nominal_voltage", value=220.0)
    m.add_relation(entity_id="N_FR", relation_id="isInEnergyDomain", target_entity_id="ELEC")
    m.add_relation(entity_id="N_FR", relation_id="isInGeographicalRegion", target_entity_id="R_FR")

    m.add_entity(entity_class="ElectricityNode", entity_id="N_IT")
    m.add_attribute(entity_id="N_IT", attribute_id="name", value="IT electricity bus")
    m.add_attribute(entity_id="N_IT", attribute_id="nominal_voltage", value=220.0)
    m.add_relation(entity_id="N_IT", relation_id="isInEnergyDomain", target_entity_id="ELEC")
    m.add_relation(entity_id="N_IT", relation_id="isInGeographicalRegion", target_entity_id="R_IT")

    m.add_entity(entity_class="ElectricityNode", entity_id="N_AT")
    m.add_attribute(entity_id="N_AT", attribute_id="name", value="AT electricity bus")
    m.add_attribute(entity_id="N_AT", attribute_id="nominal_voltage", value=220.0)
    m.add_relation(entity_id="N_AT", relation_id="isInEnergyDomain", target_entity_id="ELEC")
    m.add_relation(entity_id="N_AT", relation_id="isInGeographicalRegion", target_entity_id="R_AT")

    m.add_entity(entity_class="ElectricityNode", entity_id="N_LI")
    m.add_attribute(entity_id="N_LI", attribute_id="name", value="LI electricity bus")
    m.add_attribute(entity_id="N_LI", attribute_id="nominal_voltage", value=220.0)
    m.add_relation(entity_id="N_LI", relation_id="isInEnergyDomain", target_entity_id="ELEC")
    m.add_relation(entity_id="N_LI", relation_id="isInGeographicalRegion", target_entity_id="R_LI")

    # ------------------------------------------------------------------
    # Loads (EnergyDemand) — one per country (annual demand in MWh)
    # ------------------------------------------------------------------
    m.add_entity(entity_class="EnergyDemand", entity_id="L_CH")
    m.add_attribute(entity_id="L_CH", attribute_id="name", value="CH aggregate load")
    m.add_attribute(entity_id="L_CH", attribute_id="annual_energy_demand", value=60e6)
    m.add_relation(entity_id="L_CH", relation_id="isConnectedToNode", target_entity_id="N_CH")

    m.add_entity(entity_class="EnergyDemand", entity_id="L_DE")
    m.add_attribute(entity_id="L_DE", attribute_id="name", value="DE aggregate load")
    m.add_attribute(entity_id="L_DE", attribute_id="annual_energy_demand", value=500e6)
    m.add_relation(entity_id="L_DE", relation_id="isConnectedToNode", target_entity_id="N_DE")

    m.add_entity(entity_class="EnergyDemand", entity_id="L_FR")
    m.add_attribute(entity_id="L_FR", attribute_id="name", value="FR aggregate load")
    m.add_attribute(entity_id="L_FR", attribute_id="annual_energy_demand", value=450e6)
    m.add_relation(entity_id="L_FR", relation_id="isConnectedToNode", target_entity_id="N_FR")

    m.add_entity(entity_class="EnergyDemand", entity_id="L_IT")
    m.add_attribute(entity_id="L_IT", attribute_id="name", value="IT aggregate load")
    m.add_attribute(entity_id="L_IT", attribute_id="annual_energy_demand", value=300e6)
    m.add_relation(entity_id="L_IT", relation_id="isConnectedToNode", target_entity_id="N_IT")

    m.add_entity(entity_class="EnergyDemand", entity_id="L_AT")
    m.add_attribute(entity_id="L_AT", attribute_id="name", value="AT aggregate load")
    m.add_attribute(entity_id="L_AT", attribute_id="annual_energy_demand", value=70e6)
    m.add_relation(entity_id="L_AT", relation_id="isConnectedToNode", target_entity_id="N_AT")

    m.add_entity(entity_class="EnergyDemand", entity_id="L_LI")
    m.add_attribute(entity_id="L_LI", attribute_id="name", value="LI aggregate load")
    m.add_attribute(entity_id="L_LI", attribute_id="annual_energy_demand", value=1e6)
    m.add_relation(entity_id="L_LI", relation_id="isConnectedToNode", target_entity_id="N_LI")

    # ------------------------------------------------------------------
    # Generator fleets (EnergyConversionTechnology1x1)
    # Gas -> Electricity (all countries)
    # Hydro (Water) -> Electricity (all countries)
    # Nuclear (Uranium) -> Electricity (CH, FR)
    # ------------------------------------------------------------------

    # --- CH gas
    m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_CH_GAS")
    m.add_attribute(entity_id="G_CH_GAS", attribute_id="name", value="CH gas fleet")
    # m.add_attribute(entity_id="G_CH_GAS", attribute_id="energy_conversion_efficiency", value=0.55)
    m.add_attribute(entity_id="G_CH_GAS", attribute_id="generator_technology_type", value="gas")
    m.add_attribute(entity_id="G_CH_GAS", attribute_id="nominal_power_capacity", value=3000.0)
    m.add_attribute(entity_id="G_CH_GAS", attribute_id="input_origin", value="exogenous")
    m.add_relation(entity_id="G_CH_GAS", relation_id="isOutputNodeOf", target_entity_id="N_CH")
    # m.add_relation(entity_id="G_CH_GAS", relation_id="hasInputEnergyCarrier", target_entity_id="Gas")
    # m.add_relation(entity_id="G_CH_GAS", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
    m.add_relation(entity_id="G_CH_GAS", relation_id="instanceOf", target_entity_id="Generation.Thermal.Gas.CCGT.New")

    # --- CH hydro
    m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_CH_HYD")
    m.add_attribute(entity_id="G_CH_HYD", attribute_id="name", value="CH hydro fleet")
    # m.add_attribute(entity_id="G_CH_HYD", attribute_id="energy_conversion_efficiency", value=0.90)
    m.add_attribute(entity_id="G_CH_HYD", attribute_id="generator_technology_type", value="hydro")
    m.add_attribute(entity_id="G_CH_HYD", attribute_id="nominal_power_capacity", value=8000.0)
    m.add_attribute(entity_id="G_CH_HYD", attribute_id="annual_resource_potential", value=40e6)
    m.add_attribute(entity_id="G_CH_HYD", attribute_id="input_origin", value="exogenous")
    m.add_relation(entity_id="G_CH_HYD", relation_id="isOutputNodeOf", target_entity_id="N_CH")
    # m.add_relation(entity_id="G_CH_HYD", relation_id="hasInputEnergyCarrier", target_entity_id="Water")
    # m.add_relation(entity_id="G_CH_HYD", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
    m.add_relation(entity_id="G_CH_HYD", relation_id="instanceOf", target_entity_id="Generation.Renewable.Hydro.RunOfRiver")

    # --- CH nuclear
    m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_CH_NUC")
    m.add_attribute(entity_id="G_CH_NUC", attribute_id="name", value="CH nuclear fleet")
    # m.add_attribute(entity_id="G_CH_NUC", attribute_id="energy_conversion_efficiency", value=0.33)
    m.add_attribute(entity_id="G_CH_NUC", attribute_id="generator_technology_type", value="nuclear")
    m.add_attribute(entity_id="G_CH_NUC", attribute_id="nominal_power_capacity", value=2000.0)
    m.add_attribute(entity_id="G_CH_NUC", attribute_id="input_origin", value="exogenous")
    m.add_relation(entity_id="G_CH_NUC", relation_id="isOutputNodeOf", target_entity_id="N_CH")
    # m.add_relation(entity_id="G_CH_NUC", relation_id="hasInputEnergyCarrier", target_entity_id="Uranium")
    # m.add_relation(entity_id="G_CH_NUC", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
    m.add_relation(entity_id="G_CH_NUC", relation_id="instanceOf", target_entity_id="Generation.Thermal.Nuclear.Standard")

    # --- DE gas
    m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_DE_GAS")
    m.add_attribute(entity_id="G_DE_GAS", attribute_id="name", value="DE gas fleet")
    # m.add_attribute(entity_id="G_DE_GAS", attribute_id="energy_conversion_efficiency", value=0.55)
    m.add_attribute(entity_id="G_DE_GAS", attribute_id="generator_technology_type", value="gas")
    m.add_attribute(entity_id="G_DE_GAS", attribute_id="nominal_power_capacity", value=6000.0)
    m.add_attribute(entity_id="G_DE_GAS", attribute_id="input_origin", value="exogenous")
    m.add_relation(entity_id="G_DE_GAS", relation_id="isOutputNodeOf", target_entity_id="N_DE")
    # m.add_relation(entity_id="G_DE_GAS", relation_id="hasInputEnergyCarrier", target_entity_id="Gas")
    # m.add_relation(entity_id="G_DE_GAS", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
    m.add_relation(entity_id="G_DE_GAS", relation_id="instanceOf", target_entity_id="Generation.Thermal.Gas.CCGT.New")

    # --- DE hydro
    m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_DE_HYD")
    m.add_attribute(entity_id="G_DE_HYD", attribute_id="name", value="DE hydro fleet")
    # m.add_attribute(entity_id="G_DE_HYD", attribute_id="energy_conversion_efficiency", value=0.90)
    m.add_attribute(entity_id="G_DE_HYD", attribute_id="generator_technology_type", value="hydro")
    m.add_attribute(entity_id="G_DE_HYD", attribute_id="nominal_power_capacity", value=2000.0)
    m.add_attribute(entity_id="G_DE_HYD", attribute_id="annual_resource_potential", value=10e6)
    m.add_attribute(entity_id="G_DE_HYD", attribute_id="input_origin", value="exogenous")
    m.add_relation(entity_id="G_DE_HYD", relation_id="isOutputNodeOf", target_entity_id="N_DE")
    # m.add_relation(entity_id="G_DE_HYD", relation_id="hasInputEnergyCarrier", target_entity_id="Water")
    # m.add_relation(entity_id="G_DE_HYD", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
    m.add_relation(entity_id="G_DE_HYD", relation_id="instanceOf", target_entity_id="Generation.Renewable.Hydro.RunOfRiver")

    # --- FR gas
    m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_FR_GAS")
    m.add_attribute(entity_id="G_FR_GAS", attribute_id="name", value="FR gas fleet")
    # m.add_attribute(entity_id="G_FR_GAS", attribute_id="energy_conversion_efficiency", value=0.55)
    m.add_attribute(entity_id="G_FR_GAS", attribute_id="generator_technology_type", value="gas")
    m.add_attribute(entity_id="G_FR_GAS", attribute_id="nominal_power_capacity", value=4000.0)
    m.add_attribute(entity_id="G_FR_GAS", attribute_id="input_origin", value="exogenous")
    m.add_relation(entity_id="G_FR_GAS", relation_id="isOutputNodeOf", target_entity_id="N_FR")
    # m.add_relation(entity_id="G_FR_GAS", relation_id="hasInputEnergyCarrier", target_entity_id="Gas")
    # m.add_relation(entity_id="G_FR_GAS", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
    m.add_relation(entity_id="G_FR_GAS", relation_id="instanceOf", target_entity_id="Generation.Thermal.Gas.CCGT.New")

    # --- FR hydro
    m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_FR_HYD")
    m.add_attribute(entity_id="G_FR_HYD", attribute_id="name", value="FR hydro fleet")
    # m.add_attribute(entity_id="G_FR_HYD", attribute_id="energy_conversion_efficiency", value=0.90)
    m.add_attribute(entity_id="G_FR_HYD", attribute_id="generator_technology_type", value="hydro")
    m.add_attribute(entity_id="G_FR_HYD", attribute_id="nominal_power_capacity", value=2000.0)
    m.add_attribute(entity_id="G_FR_HYD", attribute_id="annual_resource_potential", value=15e6)
    m.add_attribute(entity_id="G_FR_HYD", attribute_id="input_origin", value="exogenous")
    m.add_relation(entity_id="G_FR_HYD", relation_id="isOutputNodeOf", target_entity_id="N_FR")
    # m.add_relation(entity_id="G_FR_HYD", relation_id="hasInputEnergyCarrier", target_entity_id="Water")
    # m.add_relation(entity_id="G_FR_HYD", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
    m.add_relation(entity_id="G_FR_HYD", relation_id="instanceOf", target_entity_id="Generation.Renewable.Hydro.RunOfRiver")

    # --- FR nuclear
    m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_FR_NUC")
    m.add_attribute(entity_id="G_FR_NUC", attribute_id="name", value="FR nuclear fleet")
    # m.add_attribute(entity_id="G_FR_NUC", attribute_id="energy_conversion_efficiency", value=0.33)
    m.add_attribute(entity_id="G_FR_NUC", attribute_id="generator_technology_type", value="nuclear")
    m.add_attribute(entity_id="G_FR_NUC", attribute_id="nominal_power_capacity", value=4000.0)
    m.add_attribute(entity_id="G_FR_NUC", attribute_id="input_origin", value="exogenous")
    m.add_relation(entity_id="G_FR_NUC", relation_id="isOutputNodeOf", target_entity_id="N_FR")
    # m.add_relation(entity_id="G_FR_NUC", relation_id="hasInputEnergyCarrier", target_entity_id="Uranium")
    # m.add_relation(entity_id="G_FR_NUC", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
    m.add_relation(entity_id="G_FR_NUC", relation_id="instanceOf", target_entity_id="Generation.Thermal.Nuclear.Standard")

    # --- IT gas
    m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_IT_GAS")
    m.add_attribute(entity_id="G_IT_GAS", attribute_id="name", value="IT gas fleet")
    # m.add_attribute(entity_id="G_IT_GAS", attribute_id="energy_conversion_efficiency", value=0.55)
    m.add_attribute(entity_id="G_IT_GAS", attribute_id="generator_technology_type", value="gas")
    m.add_attribute(entity_id="G_IT_GAS", attribute_id="nominal_power_capacity", value=5000.0)
    m.add_attribute(entity_id="G_IT_GAS", attribute_id="input_origin", value="exogenous") 
    m.add_relation(entity_id="G_IT_GAS", relation_id="isOutputNodeOf", target_entity_id="N_IT")
    # m.add_relation(entity_id="G_IT_GAS", relation_id="hasInputEnergyCarrier", target_entity_id="Gas")
    # m.add_relation(entity_id="G_IT_GAS", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
    m.add_relation(entity_id="G_IT_GAS", relation_id="instanceOf", target_entity_id="Generation.Thermal.Gas.CCGT.New")

    # --- IT hydro
    m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_IT_HYD")
    m.add_attribute(entity_id="G_IT_HYD", attribute_id="name", value="IT hydro fleet")
    # m.add_attribute(entity_id="G_IT_HYD", attribute_id="energy_conversion_efficiency", value=0.90)
    m.add_attribute(entity_id="G_IT_HYD", attribute_id="generator_technology_type", value="hydro")
    m.add_attribute(entity_id="G_IT_HYD", attribute_id="nominal_power_capacity", value=2000.0)
    m.add_attribute(entity_id="G_IT_HYD", attribute_id="annual_resource_potential", value=18e6)
    m.add_attribute(entity_id="G_IT_HYD", attribute_id="input_origin", value="exogenous")
    m.add_relation(entity_id="G_IT_HYD", relation_id="isOutputNodeOf", target_entity_id="N_IT")
    # m.add_relation(entity_id="G_IT_HYD", relation_id="hasInputEnergyCarrier", target_entity_id="Water")
    # m.add_relation(entity_id="G_IT_HYD", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
    m.add_relation(entity_id="G_IT_HYD", relation_id="instanceOf", target_entity_id="Generation.Renewable.Hydro.RunOfRiver")

    # --- AT gas
    m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_AT_GAS")
    m.add_attribute(entity_id="G_AT_GAS", attribute_id="name", value="AT gas fleet")
    # m.add_attribute(entity_id="G_AT_GAS", attribute_id="energy_conversion_efficiency", value=0.55)
    m.add_attribute(entity_id="G_AT_GAS", attribute_id="generator_technology_type", value="gas")
    m.add_attribute(entity_id="G_AT_GAS", attribute_id="nominal_power_capacity", value=1000.0)
    m.add_attribute(entity_id="G_AT_GAS", attribute_id="input_origin", value="exogenous")
    m.add_relation(entity_id="G_AT_GAS", relation_id="isOutputNodeOf", target_entity_id="N_AT")
    # m.add_relation(entity_id="G_AT_GAS", relation_id="hasInputEnergyCarrier", target_entity_id="Gas")
    # m.add_relation(entity_id="G_AT_GAS", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
    m.add_relation(entity_id="G_AT_GAS", relation_id="instanceOf", target_entity_id="Generation.Thermal.Gas.CCGT.New")

    # --- AT hydro
    m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_AT_HYD")
    m.add_attribute(entity_id="G_AT_HYD", attribute_id="name", value="AT hydro fleet")
    # m.add_attribute(entity_id="G_AT_HYD", attribute_id="energy_conversion_efficiency", value=0.90)
    m.add_attribute(entity_id="G_AT_HYD", attribute_id="generator_technology_type", value="hydro")
    m.add_attribute(entity_id="G_AT_HYD", attribute_id="nominal_power_capacity", value=2000.0)
    m.add_attribute(entity_id="G_AT_HYD", attribute_id="annual_resource_potential", value=12e6)
    m.add_attribute(entity_id="G_AT_HYD", attribute_id="input_origin", value="exogenous")
    m.add_relation(entity_id="G_AT_HYD", relation_id="isOutputNodeOf", target_entity_id="N_AT")
    # m.add_relation(entity_id="G_AT_HYD", relation_id="hasInputEnergyCarrier", target_entity_id="Water")
    # m.add_relation(entity_id="G_AT_HYD", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
    m.add_relation(entity_id="G_AT_HYD", relation_id="instanceOf", target_entity_id="Generation.Renewable.Hydro.RunOfRiver")

    # --- LI gas
    m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_LI_GAS")
    m.add_attribute(entity_id="G_LI_GAS", attribute_id="name", value="LI gas fleet")
    # m.add_attribute(entity_id="G_LI_GAS", attribute_id="energy_conversion_efficiency", value=0.55)
    m.add_attribute(entity_id="G_LI_GAS", attribute_id="generator_technology_type", value="gas")
    m.add_attribute(entity_id="G_LI_GAS", attribute_id="nominal_power_capacity", value=200.0)
    m.add_attribute(entity_id="G_LI_GAS", attribute_id="input_origin", value="exogenous")
    m.add_relation(entity_id="G_LI_GAS", relation_id="isOutputNodeOf", target_entity_id="N_LI")
    # m.add_relation(entity_id="G_LI_GAS", relation_id="hasInputEnergyCarrier", target_entity_id="Gas")
    # m.add_relation(entity_id="G_LI_GAS", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
    m.add_relation(entity_id="G_LI_GAS", relation_id="instanceOf", target_entity_id="Generation.Thermal.Gas.CCGT.New")

    # --- LI hydro
    m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_LI_HYD")
    m.add_attribute(entity_id="G_LI_HYD", attribute_id="name", value="LI hydro fleet")
    # m.add_attribute(entity_id="G_LI_HYD", attribute_id="energy_conversion_efficiency", value=0.90)
    m.add_attribute(entity_id="G_LI_HYD", attribute_id="generator_technology_type", value="hydro")
    m.add_attribute(entity_id="G_LI_HYD", attribute_id="nominal_power_capacity", value=200.0)
    m.add_attribute(entity_id="G_LI_HYD", attribute_id="annual_resource_potential", value=0.5e6)
    m.add_attribute(entity_id="G_LI_HYD", attribute_id="input_origin", value="exogenous")
    m.add_relation(entity_id="G_LI_HYD", relation_id="isOutputNodeOf", target_entity_id="N_LI")
    # m.add_relation(entity_id="G_LI_HYD", relation_id="hasInputEnergyCarrier", target_entity_id="Water")
    # m.add_relation(entity_id="G_LI_HYD", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
    m.add_relation(entity_id="G_LI_HYD", relation_id="instanceOf", target_entity_id="Generation.Renewable.Hydro.RunOfRiver")

    # ------------------------------------------------------------------
    # Interconnectors (NetTransferCapacity) between Switzerland and neighbours
    # ------------------------------------------------------------------
    m.add_entity(entity_class="NetTransferCapacity", entity_id="NTC_CH_DE")
    m.add_attribute(entity_id="NTC_CH_DE", attribute_id="name", value="NTC CH-DE")
    m.add_attribute(entity_id="NTC_CH_DE", attribute_id="maximum_power_flow_1_to_2", value=6000.0)
    m.add_attribute(entity_id="NTC_CH_DE", attribute_id="maximum_power_flow_2_to_1", value=6000.0)
    m.add_relation(entity_id="NTC_CH_DE", relation_id="isFromNodeOf", target_entity_id="N_CH")
    m.add_relation(entity_id="NTC_CH_DE", relation_id="isToNodeOf", target_entity_id="N_DE")
    m.add_relation(entity_id="NTC_CH_DE", relation_id="isInEnergyDomain", target_entity_id="ELEC")

    m.add_entity(entity_class="NetTransferCapacity", entity_id="NTC_CH_FR")
    m.add_attribute(entity_id="NTC_CH_FR", attribute_id="name", value="NTC CH-FR")
    m.add_attribute(entity_id="NTC_CH_FR", attribute_id="maximum_power_flow_1_to_2", value=4000.0)
    m.add_attribute(entity_id="NTC_CH_FR", attribute_id="maximum_power_flow_2_to_1", value=4000.0)
    m.add_relation(entity_id="NTC_CH_FR", relation_id="isFromNodeOf", target_entity_id="N_CH")
    m.add_relation(entity_id="NTC_CH_FR", relation_id="isToNodeOf", target_entity_id="N_FR")
    m.add_relation(entity_id="NTC_CH_FR", relation_id="isInEnergyDomain", target_entity_id="ELEC")

    m.add_entity(entity_class="NetTransferCapacity", entity_id="NTC_CH_IT")
    m.add_attribute(entity_id="NTC_CH_IT", attribute_id="name", value="NTC CH-IT")
    m.add_attribute(entity_id="NTC_CH_IT", attribute_id="maximum_power_flow_1_to_2", value=5000.0)
    m.add_attribute(entity_id="NTC_CH_IT", attribute_id="maximum_power_flow_2_to_1", value=5000.0)
    m.add_relation(entity_id="NTC_CH_IT", relation_id="isFromNodeOf", target_entity_id="N_CH")
    m.add_relation(entity_id="NTC_CH_IT", relation_id="isToNodeOf", target_entity_id="N_IT")
    m.add_relation(entity_id="NTC_CH_IT", relation_id="isInEnergyDomain", target_entity_id="ELEC")

    m.add_entity(entity_class="NetTransferCapacity", entity_id="NTC_CH_AT")
    m.add_attribute(entity_id="NTC_CH_AT", attribute_id="name", value="NTC CH-AT")
    m.add_attribute(entity_id="NTC_CH_AT", attribute_id="maximum_power_flow_1_to_2", value=2000.0)
    m.add_attribute(entity_id="NTC_CH_AT", attribute_id="maximum_power_flow_2_to_1", value=2000.0)
    m.add_relation(entity_id="NTC_CH_AT", relation_id="isFromNodeOf", target_entity_id="N_CH")
    m.add_relation(entity_id="NTC_CH_AT", relation_id="isToNodeOf", target_entity_id="N_AT")
    m.add_relation(entity_id="NTC_CH_AT", relation_id="isInEnergyDomain", target_entity_id="ELEC")

    m.add_entity(entity_class="NetTransferCapacity", entity_id="NTC_CH_LI")
    m.add_attribute(entity_id="NTC_CH_LI", attribute_id="name", value="NTC CH-LI")
    m.add_attribute(entity_id="NTC_CH_LI", attribute_id="maximum_power_flow_1_to_2", value=300.0)
    m.add_attribute(entity_id="NTC_CH_LI", attribute_id="maximum_power_flow_2_to_1", value=300.0)
    m.add_relation(entity_id="NTC_CH_LI", relation_id="isFromNodeOf", target_entity_id="N_CH")
    m.add_relation(entity_id="NTC_CH_LI", relation_id="isToNodeOf", target_entity_id="N_LI")
    m.add_relation(entity_id="NTC_CH_LI", relation_id="isInEnergyDomain", target_entity_id="ELEC")

    return m


def main() -> None:
    root = _repo_root()
    schema_dir = root / "schemas"
    out_dir = root / "output" / "ch_and_neighbours"
    out_dir.mkdir(parents=True, exist_ok=True)

    model = build_model(schema_dir)
    errors = model.validate()
    if errors:
        print("Model has validation issues:")
        for e in errors:
            print("  -", e)
        raise SystemExit(1)
    print("Model validated successfully.")

    yaml_path = out_dir / "ch_and_neighbours.yaml"
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

    m2.export_yaml(str(out_dir / "ch_and_neighbours_roundtrip.yaml"))
    print(f"Wrote outputs to: {out_dir}")


if __name__ == "__main__":
    main()
