from __future__ import annotations

import os
import re
import zipfile
from pathlib import Path
import sys
import pandas as pd
import numpy as np
import h5py

# Add the project root (one level up from docs/) to the Python path
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../tools/"))

# Import from the provided cesdm_toolbox.py
# If cesdm_toolbox.py is in your working directory, this will work as-is.
from cesdm_toolbox import build_model_from_yaml
from import_flexeco import export_to_flexeco, import_from_flexeco 

domain_id = "domain.electricity"
electricity_carrier_id = "carrier.electricity"

def get_attr_value(model, entity_class, entity_id, name, default=None):
    """Return the 'value' part of an attribute (handles AttributeValue and legacy scalars)."""
    entity = model.entities[entity_class][entity_id]

    raw = getattr(entity, "data", {}).get(name, default)

    if isinstance(raw, dict) and "value" in raw:
        return raw["value"]

    if isinstance(entity, dict) and name in entity:
        return entity[name]
    return raw

def save_timeseries_to_hdf5(filename, timestamps, data_dict):

    # only folder part:
    directory = os.path.dirname(filename)   # -> "./path/folder"
    # create the folder if does not exist
    os.makedirs(directory, exist_ok=True)

    # import pdb
    # pdb.set_trace()
    series_names = list(data_dict.keys())
    data_matrix = np.vstack([data_dict[k] for k in series_names]).T

    with h5py.File(filename, "w") as f:
        f.create_dataset("values", data=data_matrix)
        # f.create_dataset("time", data=np.array(timestamps, dtype="S32"))
        f.create_dataset("series_names", data=np.array(series_names, dtype="S64"))

def slugify(s: str) -> str:
    import re
    s = s.lower()
    # s = re.sub(r'[a-z0-9.-/]+', '_', s)
    # return s.strip('-')
    s = re.sub(r"[ \-]+", "_", s)
    s = re.sub(r"[ \(\)]+", "", s)
    return s
# tech_id -> "AssetClass.Family.Subfamily.Variant"  (use "." as split points)
TECH_HIERARCHY = {
    # =========================
    # GENERATION — THERMAL
    # =========================
    "nuclear": "Generation.Thermal.Nuclear.Standard",

    # Hard coal
    "hard_coal_old_1":    "Generation.Thermal.Coal.HardCoal.Old1",
    "hard_coal_old_2":    "Generation.Thermal.Coal.HardCoal.Old2",
    "hard_coal_new":      "Generation.Thermal.Coal.HardCoal.New",
    "hard_coal_ccs":      "Generation.Thermal.Coal.HardCoal.CCS",
    "hard_coal_biofuel":  "Generation.Thermal.Coal.HardCoal.Biofuel",

    # Lignite
    "lignite_old_1":      "Generation.Thermal.Coal.Lignite.Old1",
    "lignite_old_2":      "Generation.Thermal.Coal.Lignite.Old2",
    "lignite_new":        "Generation.Thermal.Coal.Lignite.New",
    "lignite_ccs":        "Generation.Thermal.Coal.Lignite.CCS",
    "lignite_biofuel":    "Generation.Thermal.Coal.Lignite.Biofuel",

    # Gas conventional
    "gas_conventional_old_1": "Generation.Thermal.Gas.Conventional.Old1",
    "gas_conventional_old_2": "Generation.Thermal.Gas.Conventional.Old2",

    # Gas CCGT
    "gas_ccgt_old_1":      "Generation.Thermal.Gas.CCGT.Old1",
    "gas_ccgt_old_2":      "Generation.Thermal.Gas.CCGT.Old2",
    "gas_ccgt_present_1":  "Generation.Thermal.Gas.CCGT.Present1",
    "gas_ccgt_present_2":  "Generation.Thermal.Gas.CCGT.Present2",
    "gas_ccgt_new":        "Generation.Thermal.Gas.CCGT.New",
    "gas_ccgt_ccs":        "Generation.Thermal.Gas.CCGT.CCS",

    # Gas OCGT
    "gas_ocgt_old":        "Generation.Thermal.Gas.OCGT.Old",
    "gas_ocgt_new":        "Generation.Thermal.Gas.OCGT.New",

    # Oil
    "light_oil":           "Generation.Thermal.Oil.LightOil.Standard",
    "heavy_oil_old_1":     "Generation.Thermal.Oil.HeavyOil.Old1",
    "heavy_oil_old_2":     "Generation.Thermal.Oil.HeavyOil.Old2",

    # Oil shale
    "oil_shale_old":       "Generation.Thermal.OilShale.Standard.Old",
    "oil_shale_new":       "Generation.Thermal.OilShale.Standard.New",
    "oil_shale_biofuel":   "Generation.Thermal.OilShale.Biofuel.Standard",

    # Residual thermal
    "others_non_renewable":"Generation.Thermal.Other.NonRenewable.Residual",

    # =========================
    # GENERATION — RENEWABLE (PROFILED)
    # =========================
    "wind_offshore":       "Generation.Renewable.Wind.Offshore",
    "wind_onshore":        "Generation.Renewable.Wind.Onshore",

    "solar_photovoltaic":  "Generation.Renewable.Solar.PV",
    "solar_thermal":       "Generation.Renewable.Solar.Thermal",

    "run_of_river":        "Generation.Renewable.Hydro.RunOfRiver",

    "others_renewable":    "Generation.Renewable.Other.Residual",

    # =========================
    # STORAGE
    # =========================
    "battery_storage":          "Storage.Electrochemical.Battery",
    "pump_storage_closed_loop": "Storage.Hydro.PumpedHydro.ClosedLoop",
    "pump_storage_open_loop":   "Storage.Hydro.PumpedHydro.OpenLoop",
    "reservoir":                "Storage.Hydro.Reservoir",
    "pondage":                  "Storage.Hydro.Pondage",

    # =========================
    # HYDROGEN & P2X
    # =========================
    # "electrolyser_load":   "Conversion.Hydrogen.PowerToHydrogen.Electrolyser",
    "hydrogen_fuel_cell":  "Generation.Hydrogen.FuelCell",
    "hydrogen_ccgt":       "Generation.Hydrogen.CCGT",

    # # =========================
    # # DEMAND & FLEXIBILITY
    # # =========================
    "demand_side_response_explicit": "Generation.DemandResponse",
    "demand_side_response_implicit": "Generation.DemandResponse",
    "demand_side_response": "Generation.DemandResponse",

    # =========================
    # BIOFUEL HYBRIDS
    # =========================
    "gas_biofuel":         "Generation.Thermal.Gas.CCGT.Biofuel",
}


TYNDP_TECH_DATA = {

    # =========================
    # GENERATION — THERMAL
    # =========================
    "Generation.Thermal.Nuclear.Standard": {"eff": 0.33, "co2": 0.00, "dispatchable": True},

    # Hard coal
    "Generation.Thermal.Coal.HardCoal.Old1": {"eff": 0.35, "co2": 0.97, "dispatchable": True},
    "Generation.Thermal.Coal.HardCoal.Old2": {"eff": 0.40, "co2": 0.85, "dispatchable": True},
    "Generation.Thermal.Coal.HardCoal.New":  {"eff": 0.46, "co2": 0.74, "dispatchable": True},
    "Generation.Thermal.Coal.HardCoal.CCS":  {"eff": 0.38, "co2": 0.09, "dispatchable": True},
    "Generation.Thermal.Coal.HardCoal.Biofuel": {"eff": 0.38, "co2": 0.09, "dispatchable": True},

    # Lignite
    "Generation.Thermal.Coal.Lignite.Old1": {"eff": 0.35, "co2": 1.04, "dispatchable": True},
    "Generation.Thermal.Coal.Lignite.Old2": {"eff": 0.40, "co2": 0.91, "dispatchable": True},
    "Generation.Thermal.Coal.Lignite.New":  {"eff": 0.46, "co2": 0.79, "dispatchable": True},
    "Generation.Thermal.Coal.Lignite.CCS":  {"eff": 0.38, "co2": 0.10, "dispatchable": True},
    "Generation.Thermal.Coal.Lignite.Biofuel": {"eff": 0.35, "co2": 0.10, "dispatchable": True},

    # Gas conventional
    "Generation.Thermal.Gas.Conventional.Old1": {"eff": 0.36, "co2": 0.57, "dispatchable": True},
    "Generation.Thermal.Gas.Conventional.Old2": {"eff": 0.41, "co2": 0.50, "dispatchable": True},

    # Gas CCGT
    "Generation.Thermal.Gas.CCGT.Old1": {"eff": 0.40, "co2": 0.51, "dispatchable": True},
    "Generation.Thermal.Gas.CCGT.Old2": {"eff": 0.48, "co2": 0.43, "dispatchable": True},
    "Generation.Thermal.Gas.CCGT.Present1": {"eff": 0.56, "co2": 0.37, "dispatchable": True},
    "Generation.Thermal.Gas.CCGT.Present2": {"eff": 0.58, "co2": 0.35, "dispatchable": True},
    "Generation.Thermal.Gas.CCGT.New": {"eff": 0.60, "co2": 0.34, "dispatchable": True},
    "Generation.Thermal.Gas.CCGT.CCS": {"eff": 0.51, "co2": 0.04, "dispatchable": True},

    # Gas OCGT
    "Generation.Thermal.Gas.OCGT.Old": {"eff": 0.35, "co2": 0.59, "dispatchable": True},
    "Generation.Thermal.Gas.OCGT.New": {"eff": 0.42, "co2": 0.49, "dispatchable": True},

    # Oil
    "Generation.Thermal.Oil.LightOil.Standard": {"eff": 0.35, "co2": 0.80, "dispatchable": True},
    "Generation.Thermal.Oil.HeavyOil.Old1": {"eff": 0.35, "co2": 0.80, "dispatchable": True},
    "Generation.Thermal.Oil.HeavyOil.Old2": {"eff": 0.40, "co2": 0.70, "dispatchable": True},

    # Oil shale
    "Generation.Thermal.OilShale.Standard.Old": {"eff": 0.29, "co2": 1.24, "dispatchable": True},
    "Generation.Thermal.OilShale.Standard.New": {"eff": 0.39, "co2": 0.92, "dispatchable": True},
    "Generation.Thermal.OilShale.Biofuel.Standard": {"eff": 0.29, "co2": 0.00, "dispatchable": True},

    # =========================
    # GENERATION — RENEWABLE
    # =========================
    "Generation.Renewable.Wind.Offshore": {"eff": 1.00, "co2": 0.00, "dispatchable": False},
    "Generation.Renewable.Wind.Onshore": {"eff": 1.00, "co2": 0.00, "dispatchable": False},

    "Generation.Renewable.Solar.PV": {"eff": 1.0, "co2": 0.0, "dispatchable": False},
    "Generation.Renewable.Solar.Thermal": {"eff": 0.35, "co2": 0.0, "dispatchable": False},

    "Generation.Renewable.Hydro.RunOfRiver": {"eff": 1.0, "co2": 0.0, "dispatchable": False},

    "Generation.Renewable.Other.Residual": {"eff": 1.0, "co2": 0.0, "dispatchable": True},
    "Generation.Thermal.Other.NonRenewable.Residual": {"eff": 1.0, "co2": 0.0, "dispatchable": True},

    # =========================
    # STORAGE
    # =========================
    "Storage.Electrochemical.Battery": {"eff": 0.95, "charge_eff": 0.90, "co2": 0.0, "dispatchable": True},
    "Storage.Hydro.PumpedHydro.ClosedLoop": {"eff": 0.90, "charge_eff": 0.85, "co2": 0.0, "dispatchable": True},
    "Storage.Hydro.PumpedHydro.OpenLoop": {"eff": 0.88, "charge_eff": 0.80, "co2": 0.0, "dispatchable": True},
    "Storage.Hydro.Reservoir": {"eff": 0.9, "charge_eff": 0.00, "co2": 0.0, "dispatchable": True},
    "Storage.Hydro.Pondage": {"eff": 0.9, "charge_eff": 0.00, "co2": 0.0, "dispatchable": True},

    # =========================
    # HYDROGEN & P2X
    # =========================
    # "Conversion.Hydrogen.PowerToHydrogen.Electrolyser": {"eff": 0.70, "co2": 0.0},
    "Generation.Hydrogen.FuelCell": {"eff": 0.55, "co2": 0.0, "dispatchable": True},
    "Generation.Hydrogen.CCGT": {"eff": 0.58, "co2": 0.0, "dispatchable": True},

    # # =========================
    # # DEMAND & FLEXIBILITY
    # # =========================
    "Generation.DemandResponse": {"eff": 1.0, "co2": 0.0, "dispatchable": True},

    # =========================
    # BIOFUEL HYBRIDS
    # =========================
    "Generation.Thermal.Gas.CCGT.Biofuel": {"eff": 0.55, "co2": 0.0, "dispatchable": True},
}

ENERGY_CARRIER_PRICE = {
    "natural_gas": 22.642024452658500,
    "hard_coal": 6.396724667349030,
    "lignite": 7.18,
    "oil": 33.026621160409600,
    "oil_shale": 6.696000000000000,
    "biomass": 67.6936567357147,
    "hydrogen": 54.432000000000000,
    "uranium": 6.051054545454550,
    "solar": 0.0,
    "wind": 0.0,
    "water": 0.0,
    "electricity": 0.0
}

ENERGY_CARRIER_CO2  = {
    "natural_gas": 0.203,
    "hard_coal": 0.340,
    "lignite": 0.363,
    "oil": 0.280,
    "oil_shale": 0.359,
    "biomass": 0.0,
    "hydrogen": 0.0,
    "uranium": 0.0,
    "solar": 0.0,
    "wind": 0.0,
    "water": 0.0,
    "electricity": 0.0
}

TYPE_MAP = {
  "Reservoir - Total reservoir capacity (GWh)": "reservoir",
  "Pondage - Total reservoir capacity (GWh)": "pondage",
  "Pump Storage (open loop, with natural inflows) - Total reservoir capacity (GWh)": "pump-storage-open-loop",
  "Pure Pump Storage (closed loop, no natural inflows) - Total reservoir capacity (GWh)": "pump-storage-closed-loop",
  "Storage capacities Solar Thermal with Storage - Total reservoir capacity (GWh)": "solar-thermal",
}

def _slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"-+", "-", s).strip("_")
    return s or ""

import pandas as pd

def carry_forward_year_per_group(
    df: pd.DataFrame,
    *,
    year_col: str = "Year",
    requested_year: int,
    group_cols: list[str],
) -> pd.DataFrame:
    """
    For each group (group_cols), keep only rows for the latest available year <= requested_year.
    If a group has no year <= requested_year, it keeps the earliest available year for that group.
    """
    out = df.copy()
    out[year_col] = pd.to_numeric(out[year_col], errors="coerce").astype("Int64")

    # best year per group
    def pick_year(s: pd.Series) -> int:
        years = sorted([int(x) for x in s.dropna().unique()])
        le = [y for y in years if y <= int(requested_year)]
        return le[-1] if le else years[0]

    chosen = (
        out.groupby(group_cols, dropna=False)[year_col]
           .apply(pick_year)
           .reset_index()
           .rename(columns={year_col: "_chosen_year"})
    )

    out = out.merge(chosen, on=group_cols, how="left")
    out = out[out[year_col] == out["_chosen_year"]].drop(columns=["_chosen_year"])
    return out


def _carrier_for_type(type_name: str) -> str:
    """
    Best-effort mapping from TYNDP Installed Capacities 'Type' to an input carrier.
    You can extend this mapping to match your conventions.
    """
    t = (type_name or "").lower()

    # Storage-like
    if any(k in t for k in ["battery"]):
        return "electricity"  # storage usually electricity->electricity

    if any(k in t for k in ["pumped", "storage", "psh"]):
        return "water"  # storage usually electricity->electricity


    # Renewables
    if "wind" in t:
        return "wind"
    if "solar" in t or "pv" in t:
        return "solar"
    if "hydro" in t or "run-of-river" in t or "ror" in t or "pondage" in t or "reservoir" in t:
        return "water"
    if "geothermal" in t:
        return "geothermal"
    if "biomass" in t or "biogas" in t or "waste" in t:
        return "biomass"

    # Fossils / thermal
    if "nuclear" in t:
        return "uranium"
    if "lignite" in t:
        return "lignite"
    if "hard coal" in t:
        return "hard coal"
    if "oil shale" in t:
        return "oil_shale"
    if "oil" in t:
        return "oil"
    if "gas" in t:
        return "natural_gas"
    if "diesel" in t:
        return "oil"
    if "demand" in t:
        return "electricity"

    return "electricity"

def assign_installed_capacity_from_tyndp_csv(
    model,
    installed_capacity_csv_path: str,
    *,
    policy: str | None = None,
    year: int | None = None,
    climate_year: int | None = None,  # not in this CSV, but kept for compatibility
    drop_zero: bool = True,
):
    """
    Reads TYNDP24_StorageCapacitites.csv and sets:
        energy_storage_capacity [MWh]
    on storage entities.

    Matching strategy:
      - Builds the same ID pattern used earlier: tech.<type>.<node>.<dim_part>
      - dim_part includes policy/year/climate year if those were used in your model IDs.
      - Tries both class names: EnergyStorageTechnology and EnergyStorage
    """

    # 3) Read CSV and filter
    df = pd.read_csv(Path(installed_capacity_csv_path))

    # Keep only installed capacity variable rows (defensive)
    if "Variable" in df.columns:
        df = df[df["Variable"].astype(str).str.contains("Installed|Charging", case=False, na=False)]

    if policy is not None and "Policy" in df.columns:
        df = df[df["Policy"] == policy]
    if year is not None and "Year" in df.columns:
        # Choose group columns that define a unique profile in your file
        group_cols = ["Node"]  # extend depending on the routine
        df = carry_forward_year_per_group(
            df,
            year_col="Year",
            requested_year=int(year),
            group_cols=group_cols,
        )
    if climate_year is not None and "Climate Year" in df.columns:
        df = df[df["Climate Year"] == climate_year]

    if drop_zero and "Value" in df.columns:
        df = df[df["Value"].fillna(0.0) != 0.0]

    # Normalize types
    df["Type"] = df["Type"].astype(str).str.strip()
    df["Node"] = df["Node"].astype(str).str.strip()
    df["Country"] = df["Country"].astype(str).str.strip()

    # # 4) Create a domain + electricity carrier
    if domain_id not in model.entities.get("EnergyDomain", {}):
        model.add_entity("EnergyDomain", domain_id)
        model.add_attribute(domain_id, "name", "ElectricityDomain")

    # # Relate domain -> carrier (hasEnergyCarrier)
    # # Safe even if repeated: add_relation updates/overwrites to same target
    # model.add_relation(domain_id, "hasEnergyCarrier", electricity_carrier_id)

    # Helpers to create carriers/nodes on demand
    def ensure_carrier(carrier_name: str) -> str:
        cid = f"carrier.{_slug(carrier_name)}"
        if cid not in model.entities.get("EnergyCarrier", {}):
            model.add_entity("EnergyCarrier", cid)
            model.add_attribute(cid, "name", carrier_name)
        # also attach to domain
        model.add_relation(domain_id, "hasEnergyCarrier", cid)

        return cid

    # def ensure_node(node_code: str, country: str | None) -> str:
    #     nid = f"node.{_slug(node_code)}"
    #     if nid not in model.entities.get("EnergyNode", {}):
    #         model.add_entity("EnergyNode", nid)
    #         node_name = f"{node_code}" + (f" ({country})" if country and country != "nan" else "")
    #         model.add_attribute(nid, "name", node_name)
    #         model.add_relation(nid, "isInEnergyDomain", domain_id)
    #     return nid

    def ensure_technology_type(type_name: str, input_carrier_id: str, output_carrier_id: str) -> str:
        """Create or reuse a generic TechnologyType for a given source 'Type'."""

        t_low = type_name.lower()
        is_storage = any(k in t_low for k in ["battery", "pumped", "storage", "psh", "reservoir", "pondage"])

        if _slug(type_name) not in TECH_HIERARCHY:
            print(f"{type_name} not in TECH_HIERARCHY")
            return None

        if is_storage==False:
            tt_id = f"{TECH_HIERARCHY[_slug(type_name)]}"
            if tt_id not in model.entities.get("TechnologyType", {}):
                model.add_entity("TechnologyType", tt_id)
                model.add_attribute(tt_id, "name", type_name)
                # model.add_attribute(tt_id, "source_type", type_name)
                # model.add_relation(tt_id, "isInEnergyDomain", domain_id)
                # Defaults (optional)
                model.add_relation(tt_id, "hasInputEnergyCarrier", input_carrier_id)
                model.add_relation(tt_id, "hasOutputEnergyCarrier", output_carrier_id)

                key = TECH_HIERARCHY[slugify(type_name)]

                if key in TYNDP_TECH_DATA:
                    model.add_attribute(tt_id,
                        "energy_conversion_efficiency",
                        TYNDP_TECH_DATA[key]["eff"]
                    )

                    if "dispatchable" in TYNDP_TECH_DATA[key]:
                        if TYNDP_TECH_DATA[key]["dispatchable"]==True:
                            model.add_attribute(tt_id,
                                "dispatch_type",
                                "dispatchable"
                            )
                        else:
                            model.add_attribute(tt_id,
                                "dispatch_type",
                                "nondispatchable"
                            )
                else:
                    model.add_attribute(tt_id,
                        "energy_conversion_efficiency",
                        1.0
                    )
                    # model.add_attribute(tt_id,
                    #     "co2_emission_factor",
                    #     TYNDP_TECH_DATA[key]["co2"]
                    # )
        else:
            tt_id = f"{TECH_HIERARCHY[_slug(type_name)]}"

            if tt_id not in model.entities.get("StorageTechnologyType", {}):
                model.add_entity("StorageTechnologyType", tt_id)
                model.add_attribute(tt_id, "name", tt_id)
                # model.add_attribute(tt_id, "source_type", type_name)
                # model.add_relation(tt_id, "isInEnergyDomain", domain_id)
                # Defaults (optional)
                model.add_relation(tt_id, "hasInputEnergyCarrier", input_carrier_id)
                model.add_relation(tt_id, "hasOutputEnergyCarrier", output_carrier_id)

                key = slugify(type_name)
                model.add_attribute(tt_id, "hasInflow", {"value": False})
                model.add_attribute(tt_id, "hasCharging", {"value": True})

                if "pump_storage_open_loop" in key:
                    key = f"{TECH_HIERARCHY[_slug('pump_storage_open_loop')]}"
                    model.add_attribute(tt_id, "hasInflow", {"value": True})
                elif "pump_storage_closed_loop" in key:
                    key = f"{TECH_HIERARCHY[_slug('pump_storage_closed_loop')]}"
                elif "battery_storage" in key:
                    key = f"{TECH_HIERARCHY[_slug('battery_storage')]}"
                elif "pondage" in key:
                    key = f"{TECH_HIERARCHY[_slug('pondage')]}"
                    model.add_attribute(tt_id, "hasInflow", {"value": True})
                    model.add_attribute(tt_id, "hasCharging", {"value": False})
                elif "reservoir" in key:
                    key = f"{TECH_HIERARCHY[_slug('reservoir')]}"
                    model.add_attribute(tt_id, "hasInflow", {"value": True})
                    model.add_attribute(tt_id, "hasCharging", {"value": False})

                if key in TYNDP_TECH_DATA:
                    model.add_attribute(tt_id,
                        "discharging_efficiency",
                        TYNDP_TECH_DATA[key]["eff"]
                    )
                    model.add_attribute(tt_id,
                        "charging_efficiency",
                        TYNDP_TECH_DATA[key]["charge_eff"]
                    )

        return tt_id

    # 5) Create technologies
    # Aggregate capacities by the keys we care about, to avoid duplicates.
    group_cols = [c for c in ["Type", "Node", "Country", "Policy", "Year", "Variable", "Climate Year"] if c in df.columns]
    df_agg = df.groupby(group_cols, dropna=False, as_index=False)["Value"].sum()

    for _, row in df_agg.iterrows():
        type_name = str(row["Type"])
        node_code = str(row["Node"])
        country = str(row["Country"]) if "Country" in row else None
        cap_mw = None
        charg_mw = None
        var = str(row["Variable"])

        if "Installed" in var:
            cap_mw = float(row["Value"])
        elif "Charging" in var:
            charg_mw = float(row["Value"])

        node_code = str(row["Node"]).strip()[0:4]
        load_type = str(row["Node"]).strip()[4:]


        nid = f"node.{_slug(node_code)}"
        load_type = f"{_slug(load_type)}"

        if nid not in model.entities["EnergyNode"]:
            continue

        cid = f"country.{_slug(country)}"
        if cid not in model.entities.get("GeographicalRegion", {}):
            model.add_entity("GeographicalRegion", cid)
            model.add_attribute(cid, "name", node_code)
            model.add_relation(nid, "isInGeographicalRegion", cid)


        # Decide if storage
        t_low = type_name.lower()
        is_storage = any(k in t_low for k in ["battery", "pumped", "storage", "psh", "reservoir", "pondage"])

        input_carrier_name = _carrier_for_type(type_name)
        input_carrier_id = ensure_carrier(input_carrier_name)

        tech_type_id = ensure_technology_type(type_name, input_carrier_id, electricity_carrier_id)

        if tech_type_id == None:
            continue

        # Entity ID includes scenario dimensions if present (keeps IDs unique)
        dims = []
        if "Policy" in df_agg.columns:
            dims.append(f"pol={row['Policy']}")
        if "Year" in df_agg.columns:
            dims.append(f"y={int(row['Year']) if pd.notna(row['Year']) else 'na'}")
        if "Climate Year" in df_agg.columns:
            dims.append(f"cy={int(row['Climate Year']) if pd.notna(row['Climate Year']) else 'na'}")
        dim_part = ".".join(_slug(str(d)) for d in dims) if dims else "base"

        tech_id = f"tech.{_slug(type_name)}.{_slug(node_code)}"

        if is_storage:
            cls = "EnergyStorageTechnology"
            if tech_id not in model.entities.get(cls, {}):
                model.add_entity(cls, tech_id)
                model.add_attribute(tech_id, "name", f"{type_name} @ {node_code}")
                if cap_mw is not None:
                    model.add_attribute(tech_id, "nominal_power_capacity", {"value": cap_mw, "unit": "MW"})
                if charg_mw is not None:
                    model.add_attribute(tech_id, "maximum_charging_power", {"value": charg_mw, "unit": "MW"})
                model.add_relation(tech_id, "instanceOf", tech_type_id)
                # model.add_relation(tech_id, "hasInputEnergyCarrier", electricity_carrier_id)
                # model.add_relation(tech_id, "hasOutputEnergyCarrier", electricity_carrier_id)
                model.add_relation(tech_id, "isConnectedToNode", nid)
            else:
                if "ev_passenger" in load_type:
                    continue
                if cap_mw is not None:
                    current_value = get_attr_value(model,cls,tech_id,"nominal_power_capacity", 0.0)
                    model.add_attribute(tech_id, "nominal_power_capacity", {"value": cap_mw + current_value, "unit": "MW"})
                if charg_mw is not None:
                    current_value = get_attr_value(model,cls,tech_id,"maximum_charging_power", 0.0)
                    model.add_attribute(tech_id, "maximum_charging_power", {"value": charg_mw + current_value, "unit": "MW"})
   
        else:
            cls = "EnergyConversionTechnology1x1"
            if tech_id not in model.entities.get(cls, {}):
                model.add_entity(cls, tech_id)
                model.add_attribute(tech_id, "name", f"{type_name} @ {node_code}")
                model.add_attribute(tech_id, "nominal_power_capacity", {"value": cap_mw, "unit": "MW"})
                model.add_relation(tech_id, "instanceOf", tech_type_id)
                # model.add_relation(tech_id, "hasInputEnergyCarrier", input_carrier_id)
                # model.add_relation(tech_id, "hasOutputEnergyCarrier", electricity_carrier_id)
                model.add_relation(tech_id, "isOutputNodeOf", nid)

                if "DemandResponse" in tech_type_id:
                    model.add_attribute(tech_id, "variable_operating_cost", {"value": 300.0})
            else:
                current_capacity = get_attr_value(model,cls,tech_id,"nominal_power_capacity", 0.0)
                model.add_attribute(tech_id, "nominal_power_capacity", {"value": cap_mw + current_capacity, "unit": "MW"})



    for carrier, co2 in ENERGY_CARRIER_CO2.items():
        cid = f"carrier.{carrier}"
        if cid in model.entities["EnergyCarrier"]:
            model.add_attribute(cid, "co2_emission_intensity", co2)

    for carrier, price in ENERGY_CARRIER_PRICE.items():
        cid = f"carrier.{carrier}"
        if cid in model.entities["EnergyCarrier"]:
            model.add_attribute(cid, "energy_carrier_cost", price)

def assign_energy_storage_capacity_from_tyndp_csv(
    model,
    storage_cap_csv_path: str,
    *,
    policy: str | None = None,
    year: int | None = None,
    climate_year: int | None = None,  # not in this CSV, but kept for compatibility
    drop_zero: bool = True,
):
    """
    Reads TYNDP24_StorageCapacitites.csv and sets:
        energy_storage_capacity [MWh]
    on storage entities.

    Matching strategy:
      - Builds the same ID pattern used earlier: tech.<type>.<node>.<dim_part>
      - dim_part includes policy/year/climate year if those were used in your model IDs.
      - Tries both class names: EnergyStorageTechnology and EnergyStorage
    """

    df = pd.read_csv(storage_cap_csv_path)

    # Defensive filters
    if "Variable" in df.columns:
        df = df[df["Variable"].astype(str).str.contains("Capacity", case=False, na=False)]

    policy = "NT"
    if policy is not None and "Policy" in df.columns:
        df = df[df["Policy"] == policy]
    if year is not None and "Year" in df.columns:
        # Choose group columns that define a unique profile in your file
        group_cols = ["Node"]  # extend depending on the routine
        df = carry_forward_year_per_group(
            df,
            year_col="Year",
            requested_year=int(year),
            group_cols=group_cols,
        )

    if drop_zero and "Value" in df.columns:
        df = df[df["Value"].fillna(0.0) != 0.0]

    # Aggregate (avoid duplicates)
    group_cols = [c for c in ["Type", "Node", "Policy", "Year"] if c in df.columns]
    df_agg = df.groupby(group_cols, dropna=False, as_index=False)["Value"].sum()

    # Determine which storage class exists in your model
    storage_class = None
    for candidate in ("EnergyStorageTechnology", "EnergyStorage"):
        if candidate in model.entities:
            storage_class = candidate
            break
    if storage_class is None:
        raise KeyError("Neither 'EnergyStorageTechnology' nor 'EnergyStorage' exists in model.entities")

    # Fast lookup of existing IDs for that class
    existing_ids = set(model.entities.get(storage_class, {}).keys())

    assigned = 0
    missing = []

    for _, row in df_agg.iterrows():
        type_name = str(row["Type"])
        node_code = str(row["Node"])
        e_mwh = float(row["Value"])

        # Build same dimension suffix you used for tech IDs
        dims = []
        if "Policy" in df_agg.columns:
            dims.append(f"pol={row['Policy']}")
        if "Year" in df_agg.columns:
            dims.append(f"y={int(row['Year']) if pd.notna(row['Year']) else 'na'}")
        # climate_year not in this CSV; only include if caller forces it
        if climate_year is not None:
            dims.append(f"cy={int(climate_year)}")

        dim_part = ".".join(slugify(str(d)) for d in dims) if dims else "base"

        # IMPORTANT: this assumes your storage entity IDs follow the same pattern as in your importer
        # If your storage IDs differ, adjust this one line.

        if "pump_storage_open_loop" in slugify(type_name):
            storage_id = f"tech.{slugify('pump_storage_open_loop')}.{slugify(node_code)}"
        elif "pump_storage_closed_loop" in slugify(type_name):
            storage_id = f"tech.{slugify('pump_storage_closed_loop')}.{slugify(node_code)}"
        elif "battery_storage" in slugify(type_name):
            storage_id = f"tech.{slugify('battery_storage')}.{slugify(node_code)}"
        elif "reservoir" in slugify(type_name):
            storage_id = f"tech.{slugify('reservoir')}.{slugify(node_code)}"
        else:
            storage_id = f"tech.{slugify(type_name)}.{slugify(node_code)}"

        if storage_id in existing_ids:
            # Set energy capacity in MWh
            model.add_attribute(storage_id, "energy_storage_capacity", {"value": e_mwh, "unit": "MWh"})
            assigned += 1
        else:
            missing.append(storage_id)

    return {"assigned": assigned, "missing_count": len(missing), "missing_examples": missing[:20]}

def export_supply_demand_balance_by_region_csv(
    model,
    out_csv_path: str,
    *,
    hours_per_year: float = 8760.0,
):
    """
    Exportiert pro GeographicalRegion eine Supply-Demand-Balance als CSV.

    Regeln:
      - Demand = Sum(EnergyDemand.annual_energy_demand)
      - Conversion Supply:
          dispatchable    -> nominal_power_capacity * 8760
          nondispatchable -> annual_resource_potential
      - Storage Supply = annual_natural_inflow_volume

    Erwartete Verknüpfung:
      Entities sind über Nodes (EnergyNode) einer GeographicalRegion zugeordnet.
      Der Code versucht dafür mehrere Relationsnamen.
    """

    # -------- Build Node -> Region mapping --------
    # We assume: EnergyNode has relation to GeographicalRegion OR via Country/Region mapping.
    node_to_region = {}

    energy_nodes = model.entities.get("EnergyNode", {})
    geo_regions = model.entities.get("GeographicalRegion", {})

    # 1) Direct node->georegion relation (common)
    candidate_node_region_rels = [
        "isInGeographicalRegion",
        "isLocatedInGeographicalRegion",
        "isInRegion",
        "isLocatedInRegion",
        "hasGeographicalRegion",
    ]

    # for node_id, node_ent in energy_nodes.items():
    #     country_id = node_ent.data["isInGeographicalRegion"]
    #     import pdb
    #     pdb.set_trace()
    #     node_to_region[node_id] = geo_regions.data["isInGeographicalRegion"]


    #     targets = _get_relation_targets(node_ent, "isInGeographicalRegion")
    #     for t in targets:
    #         if t in geo_regions:
    #             node_to_region[node_id] = t
    #             break

    # # 2) If not found, try node->country->georegion (if your model uses that)
    # #    (optional best-effort)
    # country_entities = model.entities.get("Country", {})
    # candidate_node_country_rels = ["isInCountry", "isLocatedInCountry"]
    # candidate_country_region_rels = ["isInGeographicalRegion", "isInRegion", "isLocatedInRegion"]

    # for node_id, node_ent in energy_nodes.items():
    #     if node_id in node_to_region:
    #         continue
    #     c_targets = _get_relation_targets(node_ent, *candidate_node_country_rels)
    #     for c in c_targets:
    #         cent = country_entities.get(c)
    #         if not cent:
    #             continue
    #         r_targets = _get_relation_targets(cent, *candidate_country_region_rels)
    #         for r in r_targets:
    #             if r in geo_regions:
    #                 node_to_region[node_id] = r
    #                 break
    #         if node_id in node_to_region:
    #             break

    # # Region set: include all known regions, plus regions inferred from node_to_region
    # region_ids = set(geo_regions.keys()) | set(node_to_region.values())
    # if not region_ids:
    #     # fallback: single bucket if nothing is linked
    #     region_ids = {"region.unknown"}

    # # -------- Aggregation containers --------
    # agg = {
    #     rid: {
    #         "region_id": rid,
    #         "region_name": None,
    #         "demand_annual": 0.0,
    #         "supply_dispatchable": 0.0,
    #         "supply_nondispatchable": 0.0,
    #         "supply_storage_inflow": 0.0,
    #     }
    #     for rid in region_ids
    # }

    # # region names (if available)
    # for rid in list(region_ids):
    #     rent = geo_regions.get(rid)
    #     if rent:
    #         agg[rid]["region_name"] = _get_attr(rent, "name", "label")

    # # Helper: resolve entity -> region via node relation
    # def _region_from_entity_via_node(ent: dict):
    #     node_refs = _get_relation_targets(ent, "isLocatedAtNode", "isInEnergyNode", "isAtNode", "node")
    #     for n in node_refs:
    #         if n in node_to_region:
    #             return node_to_region[n]
    #     return None

    # # -------- Demand: sum annual_energy_demand by region --------
    # for dem_id, dem_ent in model.entities.get("EnergyDemand", {}).items():
    #     rid = _region_from_entity_via_node(dem_ent) or "region.unknown"
    #     if rid not in agg:
    #         agg[rid] = {
    #             "region_id": rid,
    #             "region_name": None,
    #             "demand_annual": 0.0,
    #             "supply_dispatchable": 0.0,
    #             "supply_nondispatchable": 0.0,
    #             "supply_storage_inflow": 0.0,
    #         }
    #     annual = _as_number(_get_attr(dem_ent, "annual_energy_demand", "annualEnergyDemand"))
    #     agg[rid]["demand_annual"] += annual

    # # -------- Conversion supply --------
    # # Note: your classes may be named differently; adjust if needed.
    # for conv_id, conv_ent in model.entities.get("EnergyConversionTechnology", {}).items():
    #     rid = _region_from_entity_via_node(conv_ent) or "region.unknown"
    #     if rid not in agg:
    #         agg[rid] = {
    #             "region_id": rid,
    #             "region_name": None,
    #             "demand_annual": 0.0,
    #             "supply_dispatchable": 0.0,
    #             "supply_nondispatchable": 0.0,
    #             "supply_storage_inflow": 0.0,
    #         }

    #     dt = _get_dispatch_type(conv_ent)

    #     if dt == "dispatchable":
    #         cap = _as_number(_get_attr(conv_ent, "nominal_power_capacity", "nominalPowerCapacity"))
    #         agg[rid]["supply_dispatchable"] += cap * float(hours_per_year)
    #     elif dt == "nondispatchable":
    #         pot = _as_number(_get_attr(conv_ent, "annual_resource_potential", "annualResourcePotential"))
    #         agg[rid]["supply_nondispatchable"] += pot
    #     else:
    #         # wenn unklar, lass es weg (oder du kannst default=dispatchable setzen)
    #         pass

    # # -------- Storage inflow supply --------
    # for st_id, st_ent in model.entities.get("EnergyStorageTechnology", {}).items():
    #     rid = _region_from_entity_via_node(st_ent) or "region.unknown"
    #     if rid not in agg:
    #         agg[rid] = {
    #             "region_id": rid,
    #             "region_name": None,
    #             "demand_annual": 0.0,
    #             "supply_dispatchable": 0.0,
    #             "supply_nondispatchable": 0.0,
    #             "supply_storage_inflow": 0.0,
    #         }

    #     inflow = _as_number(_get_attr(st_ent, "annual_natural_inflow_volume", "annualNaturalInflowVolume"))
    #     agg[rid]["supply_storage_inflow"] += inflow

    # # -------- Finalize + export --------
    # rows = []
    # for rid, rec in agg.items():
    #     supply_total = (
    #         rec["supply_dispatchable"]
    #         + rec["supply_nondispatchable"]
    #         + rec["supply_storage_inflow"]
    #     )
    #     balance = supply_total - rec["demand_annual"]

    #     rows.append({
    #         "GeographicalRegion_ID": rec["region_id"],
    #         "GeographicalRegion_Name": rec["region_name"] or "",
    #         "Demand_Annual": rec["demand_annual"],
    #         "Supply_Dispatchable": rec["supply_dispatchable"],
    #         "Supply_NonDispatchable": rec["supply_nondispatchable"],
    #         "Supply_StorageInflow": rec["supply_storage_inflow"],
    #         "Supply_Total": supply_total,
    #         "Balance_SupplyMinusDemand": balance,
    #     })

    # df_out = pd.DataFrame(rows).sort_values("GeographicalRegion_ID")
    # df_out.to_csv(out_csv_path, index=False)
    # return {"rows": int(df_out.shape[0]), "out_csv_path": out_csv_path}

def assign_nodes_and_countries_from_tyndp_nodes_csv(
    model,
    nodes_csv_path: str,
    *,
    node_country_relation: str | None = "isInCountry",
):
    """
    Reads TYNDP24_Nodes.csv and creates/updates:
      - Country entities (country.<cc>)
      - EnergyNode entities (node.<nodecode>)

    Expected columns:
      - Node, Country, Country_spelledOut

    Also:
      - assigns nodes to the Electricity EnergyDomain (same domain logic as NTC)
      - optionally relates node -> country with `node_country_relation`
    """

    df = pd.read_csv(nodes_csv_path)

    # Domain resolution (copy of NTC logic)
    model.add_entity("EnergyDomain", domain_id)
    model.add_attribute(domain_id, "name", "Electricity Domain")

    model.add_entity("EnergyCarrier", electricity_carrier_id)
    model.add_attribute(electricity_carrier_id, "name", "electricity")
    model.add_relation(domain_id, "hasEnergyCarrier", electricity_carrier_id)

    created_nodes = 0
    updated_nodes = 0
    created_countries = 0
    updated_countries = 0

    for _, row in df.iterrows():
        node_code = str(row["Node"]).strip()
        cc = str(row["Country"]).strip()
        cc_name = str(row["Country_spelledOut"]).strip() if "Country_spelledOut" in df.columns else cc

        country_id = f"country.{_slug(cc)}"
        node_id = f"node.{_slug(node_code)}"

        # --- Country ---
        if country_id not in model.entities.get("GeographicalRegion", {}):
            model.add_entity("GeographicalRegion", country_id)
            created_countries += 1
        else:
            updated_countries += 1

        model.add_attribute(country_id, "name", cc_name)

        # --- Node ---
        if node_id not in model.entities.get("EnergyNode", {}):
            model.add_entity("EnergyNode", node_id)
            created_nodes += 1
        else:
            updated_nodes += 1

        model.add_attribute(node_id, "name", node_code)
        model.add_relation(node_id, "isInEnergyDomain", domain_id)
        model.add_relation(node_id, "isInGeographicalRegion", country_id)
    return {
        "countries_created": created_countries,
        "countries_updated": updated_countries,
        "nodes_created": created_nodes,
        "nodes_updated": updated_nodes,
        "rows": int(df.shape[0]),
    }

import pandas as pd

def assign_ntc_from_tyndp_ntc_types_base_csv(
    model,
    ntc_csv_path: str,
    *,
    scenario_year: int,
    base_type: str = "Base",
    real_types: tuple[str, ...] = ("Real 1", "Real 2"),
    # Welche YEARS werden als Inkremente je scenario_year addiert?
    real_years_by_scenario_year: dict[int, list[int]] | None = None,
    # Base-Year: wenn None, dann "best effort": erst scenario_year versuchen, sonst fallback
    base_year: int | None = None,
    base_year_fallback: int = 2025,   # in deiner Datei existiert Base nur 2025
    drop_zero: bool = True,
    # True = nur auf Base-Verbindungen addieren (wie du es beschrieben hast)
    add_real_only_where_base_link_exists: bool = True,
):
    """
    Original-CSV Logik:
      - Nimm Base (YEAR=base_year falls vorhanden, sonst YEAR=base_year_fallback)
      - Je nach scenario_year addiere Real 1 + Real 2 aus den definierten Jahren
      - Addiere standardmäßig NUR für gleiche (FROM,TO), d.h. auf Base-Verbindungen.

    Beispiel-Default:
      scenario_year=2030 -> Base only
      scenario_year=2040 -> Base + Real(2030,2035)
      scenario_year=2050 -> Base + Real(2030,2035,2040)
    """

    if real_years_by_scenario_year is None:
        real_years_by_scenario_year = {
            2030: [],                 # nur Base
            2040: [2030, 2035],       # addiere Real 1/2 aus 2030+2035
            2050: [2030, 2035, 2040], # addiere Real 1/2 aus 2030+2035+2040
        }

    df = pd.read_csv(ntc_csv_path)

    # Numeric
    for c in ("P12", "P21"):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # ---- Base bestimmen ----
    base_year_try = base_year if base_year is not None else scenario_year
    base = df[(df["TYPE"].astype(str).str.strip() == str(base_type)) & (df["YEAR"] == base_year_try)].copy()
    base_source_year = base_year_try

    if base.empty:
        base = df[(df["TYPE"].astype(str).str.strip() == str(base_type)) & (df["YEAR"] == base_year_fallback)].copy()
        base_source_year = base_year_fallback

    base = base[["FROM", "TO", "P12", "P21"]].copy()
    base = base.groupby(["FROM", "TO"], as_index=False)[["P12", "P21"]].sum()

    # ---- Inkremente bestimmen ----
    inc_years = real_years_by_scenario_year.get(int(scenario_year), [])
    inc = df[
        (df["TYPE"].astype(str).str.strip().isin([t.strip() for t in real_types]))
        & (df["YEAR"].isin(inc_years))
    ][["FROM", "TO", "P12", "P21"]].copy()

    if not inc.empty:
        inc = inc.groupby(["FROM", "TO"], as_index=False)[["P12", "P21"]].sum()
    else:
        inc = pd.DataFrame(columns=["FROM", "TO", "P12", "P21"])

    # ---- Addieren: Real auf Base ----
    if add_real_only_where_base_link_exists:
        # addiere nur dort, wo Base-Verbindung existiert
        merged = base.merge(inc, on=["FROM", "TO"], how="left", suffixes=("", "_inc"))
        merged["P12_inc"] = merged["P12_inc"].fillna(0.0)
        merged["P21_inc"] = merged["P21_inc"].fillna(0.0)

        merged["P12"] = merged["P12"] + merged["P12_inc"]
        merged["P21"] = merged["P21"] + merged["P21_inc"]

        df_final = merged[["FROM", "TO", "P12", "P21"]].copy()
    else:
        # union: neue Links aus Real auch übernehmen
        df_final = pd.concat([base, inc], ignore_index=True) \
                     .groupby(["FROM", "TO"], as_index=False)[["P12", "P21"]].sum()

    # ---- Zero drop ----
    if drop_zero:
        v1 = df_final["P12"].fillna(0.0)
        v2 = df_final["P21"].fillna(0.0)
        df_final = df_final[(v1 != 0.0) | (v2 != 0.0)]

    # # ---- Domain resolution (wie bei dir) ----
    # domain_id = None
    # for cand in ("domain.electricitydomain", "domain.electricity", "EnergyDomain", "ElectricityDomain"):
    #     if "EnergyDomain" in model.entities and cand in model.entities["EnergyDomain"]:
    #         domain_id = cand
    #         break
    # if domain_id is None and "EnergyDomain" in model.entities and model.entities["EnergyDomain"]:
    #     domain_id = next(iter(model.entities["EnergyDomain"].keys()))
    # if domain_id is None:
    #     domain_id = "domain.electricitydomain"
    #     model.add_entity("EnergyDomain", domain_id)
    #     model.add_attribute(domain_id, "name", "ElectricityDomain")

    created = 0
    updated = 0

    # ---- Schreiben ----
    for _, row in df_final.iterrows():
        frm = str(row["FROM"]).strip()
        to = str(row["TO"]).strip()

        ntc_id = f"ntc.{_slug(frm)}_{_slug(to)}"

        if ntc_id not in model.entities.get("NetTransferCapacity", {}):
            model.add_entity("NetTransferCapacity", ntc_id)
            model.add_attribute(
                ntc_id,
                "name",
                f"NTC {frm}->{to}",
            )
            created += 1
        else:
            updated += 1

        from_node_id = f"node.{_slug(frm)}"
        to_node_id = f"node.{_slug(to)}"

        model.add_relation(ntc_id, "isFromNodeOf", from_node_id)
        model.add_relation(ntc_id, "isToNodeOf", to_node_id)
        model.add_relation(ntc_id, "isInEnergyDomain", domain_id)

        p12 = float(row["P12"]) if pd.notna(row["P12"]) else 0.0
        p21 = float(row["P21"]) if pd.notna(row["P21"]) else 0.0

        model.add_attribute(ntc_id, "maximum_power_flow_1_to_2", {"value": p12, "unit": "MW"})
        model.add_attribute(ntc_id, "maximum_power_flow_2_to_1", {"value": p21, "unit": "MW"})

        try:
            model.add_attribute(ntc_id, "scenario_year", int(scenario_year))
            model.add_attribute(ntc_id, "base_source_year", int(base_source_year))
        except Exception:
            pass

    return {
        "created": created,
        "updated": updated,
        "rows": int(df_final.shape[0]),
        "scenario_year": int(scenario_year),
        "base_source_year": int(base_source_year),
        "real_years_added": list(inc_years),
        "add_real_only_where_base_link_exists": bool(add_real_only_where_base_link_exists),
    }


def assign_demand_from_tyndp_timeseries_csv(
    model,
    profiles:dict,
    demand_csv_path: str,
    *,
    policy: str | None = None,
    year: int | None = None,
    climate_year: int | None = None,
    drop_zero: bool = True,
):
    """
    Reads demand timeseries CSV and creates/updates EnergyDemand entities.

    Expected columns:
      - ID, Node, Policy, Year, Climate, 1..8760

    Mapping:
      - annual_energy_demand <- sum(1..8760)
      - isLocatedAtNode -> node.<Node>
      - isInEnergyDomain -> ElectricityDomain

    Notes:
      - Aggregates duplicate rows by (ID, Node, Policy, Year, Climate)
      - Blind add like NTC (model handles overwrite)
    """

    df = pd.read_csv(demand_csv_path)

    # Optional filters (same logic as NTC)
    if policy is not None and "Policy" in df.columns:
        df = df[df["Policy"].fillna(policy) == policy]
    if year is not None and "Year" in df.columns:
        # Choose group columns that define a unique profile in your file
        group_cols = ["Node","Type"]  # extend depending on the routine
        df = carry_forward_year_per_group(
            df,
            year_col="Year",
            requested_year=int(year),
            group_cols=group_cols,
        )
    if climate_year is not None and "Climate" in df.columns:
        df = df[df["Climate"].fillna(climate_year) == climate_year]

    # Detect timeseries columns
    ts_cols = [c for c in df.columns if c.isdigit()]

    # # Domain resolution (copy-paste from NTC)
    # domain_id = None
    # for cand in ("domain.electricitydomain", "domain.electricity", "EnergyDomain", "ElectricityDomain"):
    #     if "EnergyDomain" in model.entities and cand in model.entities["EnergyDomain"]:
    #         domain_id = cand
    #         break
    # if domain_id is None and "EnergyDomain" in model.entities and model.entities["EnergyDomain"]:
    #     domain_id = next(iter(model.entities["EnergyDomain"].keys()))
    # if domain_id is None:
    #     domain_id = "domain.electricitydomain"
    #     model.add_entity("EnergyDomain", domain_id)
    #     model.add_attribute(domain_id, "name", "ElectricityDomain")

    # # Node helper (same as NTC)
    # def ensure_node(n: str) -> str:
    #     n = str(n).strip()
    #     nid = f"node.{_slug(n)}"
    #     if nid not in model.entities.get("EnergyNode", {}):
    #         model.add_entity("EnergyNode", nid)
    #         model.add_attribute(nid, "name", n)
    #         model.add_relation(nid, "isInEnergyDomain", domain_id)
    #     return nid

    # Aggregate duplicates
    group_cols = [c for c in ["ID", "Type", "Node", "Policy", "Year", "Climate"] if c in df.columns]
    df[ts_cols] = df[ts_cols].apply(pd.to_numeric, errors="coerce")
    df_agg = df.groupby(group_cols, dropna=False, as_index=False)[ts_cols].sum()

    created = 0
    updated = 0

    for _, row in df_agg.iterrows():

        # node_code = str(row["Node"]).strip()
        node_code = str(row["Node"]).strip()[0:4]
        load_type = str(row["Node"]).strip()[4:]

        node_id = f"node.{_slug(node_code)}"
        load_type = f"{_slug(load_type)}"

        if node_id not in model.entities["EnergyNode"]:
            # print(node_id)
            continue

        annual = float(row[ts_cols].sum(skipna=True))
        if drop_zero and annual == 0:
            continue

        dims = []
        if "Policy" in df_agg.columns and pd.notna(row.get("Policy", None)):
            dims.append(f"pol={row['Policy']}")
        if "Year" in df_agg.columns and pd.notna(row.get("Year", None)):
            dims.append(f"y={int(row['Year'])}")
        if "Climate" in df_agg.columns and pd.notna(row.get("Climate", None)):
            dims.append(f"cy={int(row['Climate'])}")

        typ = str(row["Type"]).strip() if "Type" in df_agg.columns else "renewable"
        subtype = "electricity"
        if "Demand" in typ:
            subtype = "electricity"
        elif "Electrolyser" in typ:
            subtype = "electrolyse"
        else:
            # print(str(row["Node"]).strip(),str(row["Type"]).strip())
            continue

        demand_type = subtype
        if load_type != "":
            dem_id = f"demand.{_slug(subtype)}.{_slug(load_type)}.{_slug(node_code)}"
            prof_id = f"profile.{"demand"}.{_slug(subtype)}.{_slug(load_type)}.{_slug(node_code)}"
            demand_type = f"{_slug(subtype)}.{_slug(load_type)}"
        else:
            dem_id = f"demand.{_slug(subtype)}.{_slug(node_code)}"
            prof_id = f"profile.{"demand"}.{_slug(subtype)}.{_slug(node_code)}"

        # if dims:
        #     dem_id += "." + ".".join(dims)

        ts = [float(x) if pd.notna(x) else 0.0 for x in row[ts_cols]]
        ts = np.array(ts)
        ts = np.concatenate([ts, ts[-24:]])
        annual = float(ts.sum())

        has_negative = np.any(ts < 0)

        if has_negative:
            ts = np.abs(ts)


        profiles[prof_id] = -np.array(ts)/annual

        if dem_id not in model.entities.get("EnergyDemand", {}):
            model.add_entity("EnergyDemand", dem_id)
            model.add_attribute(dem_id, "name", f"Demand {_slug(subtype)} {_slug(load_type)} {node_code}")
            created += 1
        else:
            updated += 1

        node_id = f"node.{_slug(node_code)}"

        model.add_relation(dem_id, "isConnectedToNode", node_id)

        model.add_attribute(
            dem_id,
            "annual_energy_demand",
            {"value": annual, "unit": "MWh/year"}  # or GWh if you prefer
        )
        model.add_attribute(
            dem_id,
            "demand_profile_reference",
            {"value": prof_id}  # or GWh if you prefer
        )
        model.add_attribute(
            dem_id,
            "demand_type",
            {"value": demand_type}  # or GWh if you prefer
        )

        if subtype == "electrolyse":
            model.add_attribute(dem_id, "is_demand_flexible",{"value": True})
            model.add_attribute(dem_id, "flexibility_window_time_end",{"value": 0})
            model.add_attribute(dem_id, "flexibility_window_time_end",{"value": 8760})
            model.add_attribute(dem_id, "flexibility_time_resolution",{"value": 8760})
            model.add_attribute(dem_id, "value_of_lost_load",{"value": 50.0})

    return {"created": created, "updated": updated, "rows": int(df_agg.shape[0])}

def assign_renewable_timeseries_from_csv(
    model,
    profiles: dict,
    renewable_csv_path: str,
    *,
    renewable_type: str | None = None,   # filter by Type if desired
    year: int | None = None,
    climate_year: int | None = None,
    store_timeseries: bool = True,       # set False if you only want annual sum
    drop_zero: bool = True,
):
    """
    Reads renewable 8760 time series CSV and creates/updates renewable profile entities.

    Expected columns:
      - ID, Node, Country, Type, Year, Climate Year, Unit, 1..8760

    Mapping:
      - annual_energy <- sum(1..8760)
      - optional time_series <- list(1..8760)
      - isLocatedAtNode -> node.<Node>
      - isInEnergyDomain -> ElectricityDomain

    Notes:
      - Aggregates duplicate rows by (ID, Node, Country, Type, Year, Climate Year, Unit) by summing 8760 cols.
      - Creates missing EnergyNode entities if needed.
    """

    df = pd.read_csv(renewable_csv_path)

    # Optional filters
    if renewable_type is not None and "Type" in df.columns:
        df = df[df["Type"].fillna(renewable_type) == renewable_type]
    if year is not None and "Year" in df.columns:
        # Choose group columns that define a unique profile in your file
        group_cols = ["Node","Type"]  # extend depending on the routine
        df = carry_forward_year_per_group(
            df,
            year_col="Year",
            requested_year=int(year),
            group_cols=group_cols,
        )

    if climate_year is not None and "Climate Year" in df.columns:
        df = df[df["Climate Year"].fillna(climate_year) == climate_year]

    # Detect timeseries columns
    ts_cols = [c for c in df.columns if c.isdigit()]

    # Ensure numeric
    df[ts_cols] = df[ts_cols].apply(pd.to_numeric, errors="coerce")

    # Drop zero rows if requested
    if drop_zero:
        annual = df[ts_cols].sum(axis=1, skipna=True)
        df = df[annual != 0.0]

    # # Domain resolution (same as NTC)
    # domain_id = None
    # for cand in ("domain.electricitydomain", "domain.electricity", "EnergyDomain", "ElectricityDomain"):
    #     if "EnergyDomain" in model.entities and cand in model.entities["EnergyDomain"]:
    #         domain_id = cand
    #         break
    # if domain_id is None and "EnergyDomain" in model.entities and model.entities["EnergyDomain"]:
    #     domain_id = next(iter(model.entities["EnergyDomain"].keys()))
    # if domain_id is None:
    #     domain_id = "domain.electricitydomain"
    #     model.add_entity("EnergyDomain", domain_id)
    #     model.add_attribute(domain_id, "name", "ElectricityDomain")

    # # Ensure node helper
    # def ensure_node(n: str) -> str:
    #     n = str(n).strip()
    #     nid = f"node.{_slug(n)}"
    #     if nid not in model.entities.get("EnergyNode", {}):
    #         model.add_entity("EnergyNode", nid)
    #         model.add_attribute(nid, "name", n)
    #         model.add_relation(nid, "isInEnergyDomain", domain_id)
    #     return nid

    # Aggregate duplicates
    group_cols = [c for c in ["ID", "Node", "Country", "Type", "Year", "Climate Year", "Unit"] if c in df.columns]
    df_agg = df.groupby(group_cols, dropna=False, as_index=False)[ts_cols].sum()

    created = 0
    updated = 0

    for _, row in df_agg.iterrows():
        rid = str(row["ID"]).strip()
        node_code = str(row["Node"]).strip()
        typ = str(row["Type"]).strip() if "Type" in df_agg.columns else "renewable"
        unit = str(row["Unit"]).strip() if "Unit" in df_agg.columns and pd.notna(row["Unit"]) else ""

        # Dimensions suffix (same style as NTC)
        dims = []
        if "Year" in df_agg.columns and pd.notna(row.get("Year", None)):
            dims.append(f"y={int(row['Year'])}")
        if "Climate Year" in df_agg.columns and pd.notna(row.get("Climate Year", None)):
            dims.append(f"cy={int(row['Climate Year'])}")

        # tech_id = f"tech.{_slug(type_name)}.{_slug(node_code)}"
        if "SolarPV" in typ:
            tech_id = f"tech.{_slug("solar_photovoltaic")}.{_slug(node_code)}"
            prof_id = f"profile.{_slug("solar_photovoltaic")}.{_slug(node_code)}"
        elif "CSP_noStorage" in typ:
            tech_id = f"tech.{_slug("solar_thermal")}.{_slug(node_code)}"
            prof_id = f"profile.{_slug("solar_thermal")}.{_slug(node_code)}"
        elif "Wind_Offshore" in typ:
            tech_id = f"tech.{_slug("wind_offshore")}.{_slug(node_code)}"
            prof_id = f"profile.{_slug("wind_offshore")}.{_slug(node_code)}"
        elif "Wind_Onshore" in typ:
            tech_id = f"tech.{_slug("wind_onshore")}.{_slug(node_code)}"
            prof_id = f"profile.{_slug("wind_onshore")}.{_slug(node_code)}"
        else:
            continue

        ts = [float(x) if pd.notna(x) else 0.0 for x in row[ts_cols]]
        annual = sum(ts)


        # Create/update
        if tech_id in model.entities.get("EnergyConversionTechnology1x1", {}):
            # Annual sum
            capacity_factor_sum = float(row[ts_cols].sum(skipna=True))
            nominal_power_capacity = model.entities["EnergyConversionTechnology1x1"][tech_id].data["nominal_power_capacity"]["value"]

            # store external profile
            profiles[prof_id] = np.array(ts)/annual

            model.add_attribute(
                tech_id,
                "annual_resource_potential",
                {"value": capacity_factor_sum*nominal_power_capacity}
            )

            model.add_attribute(
                tech_id,
                "resource_potential_profile_reference",
                {"value": prof_id}
            )

            


        # # Relations
        # node_id = ensure_node(node_code)
        # model.add_relation(prof_id, "isLocatedAtNode", node_id)
        # model.add_relation(prof_id, "isInEnergyDomain", domain_id)


        # # Optional timeseries storage (8760 list)
        # if store_timeseries:
        #     ts_list = [float(x) if pd.notna(x) else 0.0 for x in row[ts_cols].tolist()]
        #     model.add_attribute(
        #         prof_id,
        #         "time_series",
        #         {"values": ts_list, "unit": unit} if unit else {"values": ts_list}
        #     )

    return {"created": created, "updated": updated, "rows": int(df_agg.shape[0])}

def assign_inflow_timeseries_from_csv(
    model,
    profiles: dict,
    inflow_csv_path: str,
    *,
    renewable_type: str | None = None,   # filter by Type if desired
    year: int | None = None,
    climate_year: int | None = None,
    store_timeseries: bool = True,       # set False if you only want annual sum
    drop_zero: bool = True,
):
    """
    Reads renewable 8760 time series CSV and creates/updates renewable profile entities.

    Expected columns:
      - ID, Node, Country, Type, Year, Climate Year, Unit, 1..8760

    Mapping:
      - annual_energy <- sum(1..8760)
      - optional time_series <- list(1..8760)
      - isLocatedAtNode -> node.<Node>
      - isInEnergyDomain -> ElectricityDomain

    Notes:
      - Aggregates duplicate rows by (ID, Node, Country, Type, Year, Climate Year, Unit) by summing 8760 cols.
      - Creates missing EnergyNode entities if needed.
    """

    df = pd.read_csv(inflow_csv_path)

    # Optional filters
    if renewable_type is not None and "Type" in df.columns:
        df = df[df["Type"].fillna(renewable_type) == renewable_type]
    if year is not None and "Year" in df.columns:
        # Choose group columns that define a unique profile in your file
        group_cols = ["Node","Type"]  # extend depending on the routine
        df = carry_forward_year_per_group(
            df,
            year_col="Year",
            requested_year=int(year),
            group_cols=group_cols,
        )
    if climate_year is not None and "Climate Year" in df.columns:
        df = df[df["Climate Year"].fillna(climate_year) == climate_year]

    # Detect timeseries columns
    ts_cols = [c for c in df.columns if c.isdigit()]

    # Ensure numeric
    df[ts_cols] = df[ts_cols].apply(pd.to_numeric, errors="coerce")

    # Drop zero rows if requested
    if drop_zero:
        annual = df[ts_cols].sum(axis=1, skipna=True)
        df = df[annual != 0.0]

    # # Domain resolution (same as NTC)
    # domain_id = None
    # for cand in ("domain.electricitydomain", "domain.electricity", "EnergyDomain", "ElectricityDomain"):
    #     if "EnergyDomain" in model.entities and cand in model.entities["EnergyDomain"]:
    #         domain_id = cand
    #         break
    # if domain_id is None and "EnergyDomain" in model.entities and model.entities["EnergyDomain"]:
    #     domain_id = next(iter(model.entities["EnergyDomain"].keys()))
    # if domain_id is None:
    #     domain_id = "domain.electricitydomain"
    #     model.add_entity("EnergyDomain", domain_id)
    #     model.add_attribute(domain_id, "name", "ElectricityDomain")

    # # Ensure node helper
    # def ensure_node(n: str) -> str:
    #     n = str(n).strip()
    #     nid = f"node.{_slug(n)}"
    #     if nid not in model.entities.get("EnergyNode", {}):
    #         model.add_entity("EnergyNode", nid)
    #         model.add_attribute(nid, "name", n)
    #         model.add_relation(nid, "isInEnergyDomain", domain_id)
    #     return nid

    # Aggregate duplicates
    group_cols = [c for c in ["ID", "Node", "Country", "Type", "Year", "Climate Year", "Variable"] if c in df.columns]
    df_agg = df.groupby(group_cols, dropna=False, as_index=False)[ts_cols].sum()

    created = 0
    updated = 0

    for _, row in df_agg.iterrows():
        rid = str(row["ID"]).strip()
        node_code = str(row["Node"]).strip()
        typ = str(row["Type"]).strip() if "Type" in df_agg.columns else "renewable"
        variable = str(row["Variable"]).strip() if "Variable" in df_agg.columns and pd.notna(row["Variable"]) else ""

        # Dimensions suffix (same style as NTC)
        dims = []
        if "Year" in df_agg.columns and pd.notna(row.get("Year", None)):
            dims.append(f"y={int(row['Year'])}")
        if "Climate Year" in df_agg.columns and pd.notna(row.get("Climate Year", None)):
            dims.append(f"cy={int(row['Climate Year'])}")

        # tech_id = f"tech.{_slug(type_name)}.{_slug(node_code)}"
        if "Reservoir" in typ:
            tech_id = f"tech.{_slug("reservoir")}.{_slug(node_code)}"
            prof_id = f"profile.{_slug("reservoir")}.{_slug(node_code)}"
        elif "PS Open" in typ:
            tech_id = f"tech.{_slug("pump_storage_open_loop")}.{_slug(node_code)}"
            prof_id = f"profile.{_slug("pump_storage_open_loop")}.{_slug(node_code)}"
        elif "PS Cloase" in typ:
            tech_id = f"tech.{_slug("pump_storage_closed_loop")}.{_slug(node_code)}"
            prof_id = f"profile.{_slug("pump_storage_closed_loop")}.{_slug(node_code)}"
        elif "Pondage" in typ:
            tech_id = f"tech.{_slug("pondage")}.{_slug(node_code)}"
            prof_id = f"profile.{_slug("pondage")}.{_slug(node_code)}"
        elif "Run of River" in typ:
            tech_id = f"tech.{_slug("run_of_river")}.{_slug(node_code)}"
            prof_id = f"profile.{_slug("run_of_river")}.{_slug(node_code)}"
        else:
            continue


        # Create/update
        if tech_id in model.entities.get("EnergyConversionTechnology1x1", {}):
            # Annual sum
            annual_resource_potential = float(row[ts_cols].sum(skipna=True))

            ts = [float(x) if pd.notna(x) else 0.0 for x in row[ts_cols]]

            model.add_attribute(
                tech_id,
                "annual_resource_potential",
                {"value": annual_resource_potential}
            )

            model.add_attribute(
                tech_id,
                "resource_potential_profile_reference",
                {"value": prof_id}
            )

            profiles[prof_id] = np.array(ts)/annual_resource_potential

        # Create/update
        elif tech_id in model.entities.get("EnergyStorageTechnology", {}):
            # Annual sum
            annual_natural_inflow_volume = float(row[ts_cols].sum(skipna=True))

            ts = [float(x) if pd.notna(x) else 0.0 for x in row[ts_cols]]

            model.add_attribute(
                tech_id,
                "annual_natural_inflow_volume",
                {"value": annual_natural_inflow_volume}
            )
            model.add_attribute(
                tech_id,
                "natural_inflow_profile_reference",
                {"value": prof_id}
            )



            profiles[prof_id] = np.array(ts)/annual_natural_inflow_volume
        else:
            continue

        # # Relations
        # node_id = ensure_node(node_code)
        # model.add_relation(prof_id, "isLocatedAtNode", node_id)
        # model.add_relation(prof_id, "isInEnergyDomain", domain_id)


        # # Optional timeseries storage (8760 list)
        # if store_timeseries:
        #     ts_list = [float(x) if pd.notna(x) else 0.0 for x in row[ts_cols].tolist()]
        #     model.add_attribute(
        #         prof_id,
        #         "time_series",
        #         {"values": ts_list, "unit": unit} if unit else {"values": ts_list}
        #     )

    return {"created": created, "updated": updated, "rows": int(df_agg.shape[0])}

def build_cesdm_model_from_tyndp_installed_capacities(
    schema_path: str | os.PathLike,
    data_folder = "../data/",
    output_folder: str | os.PathLike = "../output/",
    *,
    policy: str | None = None,
    year: int | None = None,
    climate_year: int | None = None,
    drop_zero: bool = True,
) -> None:
    """
    Build a CESDM model using CESDM schemas + TYNDP Installed Capacities CSV.

    Creates:
      - EnergyDomain: 'ElectricityDomain'
      - EnergyCarriers: electricity + inferred input carriers
      - ElectricityNode entities for each TYNDP Node
      - Generator/Converter entities (EnergyConversionTechnology1x1) for each (Type, Node, Year, Policy, Climate Year)
      - Storage entities (EnergyStorageTechnology) for storage-like Types

    Exports:
      - JSON grouped by class via Model.export_json(out_json_path)
    """
    schema_path = Path(schema_path)

    # 1) Extract schemas
    schema_dir = Path("../")
    schema_dir.mkdir(parents=True, exist_ok=True)

    # build_model_from_yaml expects the folder containing YAMLs; in your zip it is "schemas/"
    yaml_schema_root = schema_dir / "schemas"

    # 2) Build model from schemas
    model = build_model_from_yaml(yaml_schema_root)

    profiles = {}


    assign_nodes_and_countries_from_tyndp_nodes_csv(model,nodes_csv_path=data_folder+"TYNDP24_Nodes.csv")

    assign_installed_capacity_from_tyndp_csv(
        model=model,
        installed_capacity_csv_path=data_folder+"TYNDP24_InstalledCapacities.csv",
        policy=policy,
        year=year,
        climate_year=climate_year,
    )

    assign_demand_from_tyndp_timeseries_csv(
        model=model,
        profiles=profiles,
        demand_csv_path=data_folder+"TYNDP24_DemandProfiles.csv",
        policy=policy,
        year=year,
        climate_year=climate_year,
    )

    assign_renewable_timeseries_from_csv(
        model=model,
        profiles=profiles,
        renewable_csv_path=data_folder+"TYNDP24_GenProfiles.csv",
        year=year,
        climate_year=climate_year,
    )


    assign_inflow_timeseries_from_csv(
        model=model,
        profiles=profiles,
        inflow_csv_path=data_folder+"TYNDP24_HydroInflows.csv",
        year=year,
        climate_year=climate_year,
    )

    # Optional validation (may raise if something is inconsistent)
    result = assign_energy_storage_capacity_from_tyndp_csv(
    model=model,
    storage_cap_csv_path=data_folder+"TYNDP24_StorageCapacitites.csv",
    policy=policy,
    year=year,
    drop_zero=True)



    # 5b) Create NTC entities (country-to-country interconnections)
    try:
        ntc_res = assign_ntc_from_tyndp_ntc_types_base_csv(
            model=model,
            ntc_csv_path=data_folder+"TYNDP24_NTC_types.csv",
            scenario_year=year
        )
        print(f"NTC import: {ntc_res}")
    except FileNotFoundError:
        print("NTC CSV not found; skipping NTC import.")

    errors = model.validate()
    if errors:
        print("Model has validation issues:")
        for e in errors:
            print("  -", e)
    else:
        print("Model validated successfully.")

    # 6) Export
    Path(output_folder).parent.mkdir(parents=True, exist_ok=True)
    scenario_output_folder = output_folder + f"SC_{policy}_SY_{year}_WY_{climate_year}/"
    Path(scenario_output_folder).parent.mkdir(parents=True, exist_ok=True)
    yaml_file_name = f"tyndp_{policy}_{year}_{climate_year}".lower()

    model.export_yaml(scenario_output_folder + "/cesdm/" + yaml_file_name + ".yaml")
    model.export_csv_by_class_wide(scenario_output_folder + "/cesdm/tablewide/")
    model.export_long_csv(scenario_output_folder + "/cesdm/tyndp_rowbased.csv")

    save_timeseries_to_hdf5(filename=str(scenario_output_folder + "/cesdm/profile_data.h5"), timestamps=None, data_dict=profiles)

    export_to_flexeco(model, Path(scenario_output_folder + "/flexeco/" + yaml_file_name + ".jpn"))
    save_timeseries_to_hdf5(filename=str(scenario_output_folder + "/flexeco/profiles/profiles.h5"), timestamps=None, data_dict=profiles)

    # scenario_output_folder = "../output/" + f"SC_{sc}_SY_{sy}_WY_{wy}/cesdm/"

    # export_supply_demand_balance_by_region_csv(model=model,out_csv_path=scenario_output_folder+"summary.csv")

def import_cesdm_model_from_tyndp_installed_capacities(
    schema_path: str | os.PathLike,
    data_folder = "../data/",
    output_folder: str | os.PathLike = "../output/",
    *,
    policy: str | None = None,
    year: int | None = None,
    climate_year: int | None = None,
    drop_zero: bool = True,
) -> None:
    """
    Build a CESDM model using CESDM schemas + TYNDP Installed Capacities CSV.

    Creates:
      - EnergyDomain: 'ElectricityDomain'
      - EnergyCarriers: electricity + inferred input carriers
      - ElectricityNode entities for each TYNDP Node
      - Generator/Converter entities (EnergyConversionTechnology1x1) for each (Type, Node, Year, Policy, Climate Year)
      - Storage entities (EnergyStorageTechnology) for storage-like Types

    Exports:
      - JSON grouped by class via Model.export_json(out_json_path)
    """
    schema_path = Path(schema_path)

    # 1) Extract schemas
    schema_dir = Path("../")
    schema_dir.mkdir(parents=True, exist_ok=True)

    # build_model_from_yaml expects the folder containing YAMLs; in your zip it is "schemas/"
    yaml_schema_root = schema_dir / "schemas"

    # 2) Build model from schemas
    model = build_model_from_yaml(yaml_schema_root)

    profiles = {}


    # 6) Export
    Path(output_folder).parent.mkdir(parents=True, exist_ok=True)
    scenario_output_folder = output_folder + f"SC_{policy}_SY_{year}_WY_{climate_year}/"
    Path(scenario_output_folder).parent.mkdir(parents=True, exist_ok=True)
    yaml_file_name = f"tyndp_{policy}_{year}_{climate_year}".lower()

    # model.import_yaml(scenario_output_folder + "/cesdm/" + yaml_file_name + ".yaml")
    # model.import_csv_by_class_wide(scenario_output_folder + "/cesdm/tablewide/")
    model.import_long_csv(scenario_output_folder + "/cesdm/tyndp_rowbased.csv")
    errors = model.validate()
    if errors:
        print("Model has validation issues:")
        for e in errors:
            print("  -", e)
    else:
        print("Model validated successfully.")

    # save_timeseries_to_hdf5(filename=str(scenario_output_folder + "/cesdm/profile_data.h5"), timestamps=None, data_dict=profiles)

    export_to_flexeco(model, Path(scenario_output_folder + "/flexeco/" + yaml_file_name + "_v2.jpn"))
    # save_timeseries_to_hdf5(filename=str(scenario_output_folder + "/flexeco/profiles/profiles.h5"), timestamps=None, data_dict=profiles)

# -------------------
# Example usage (paths as provided in your environment)
# -------------------
if __name__ == "__main__":
    # for sc in ["NT"]:
    #     for sy in [2030,2040]:
    #         for wy in [2009]:
    #             build_cesdm_model_from_tyndp_installed_capacities(
    #                 schema_path="schemas",
    #                 data_folder="../data/",
    #                 output_folder ="../output/",
    #                 policy=sc,   # optional
    #                 year=sy,     # optional
    #                 climate_year=wy,  # optional
    #                 drop_zero=True,
    #             )
                
    # for sc in ["DE","GA"]:
    #     for sy in [2030,2040,2050]:
    #         for wy in [2009]:
    #             build_cesdm_model_from_tyndp_installed_capacities(
    #                 schema_path="schemas",
    #                 data_folder="../data/",
    #                 output_folder ="../output/",
    #                 policy=sc,   # optional
    #                 year=sy,     # optional
    #                 climate_year=wy,  # optional
    #                 drop_zero=True,
    #             )


    for sc in ["GA"]:
        for sy in [2050]:
            for wy in [2009]:
                build_cesdm_model_from_tyndp_installed_capacities(
                    schema_path="schemas",
                    data_folder="../data/",
                    output_folder ="../output/",
                    policy=sc,   # optional
                    year=sy,     # optional
                    climate_year=wy,  # optional
                    drop_zero=True,
                )


    # print("Wrote: tyndp_cesdm_model.yaml")
