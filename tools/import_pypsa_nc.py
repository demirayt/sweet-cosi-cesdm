"""
import_pypsa_nc
===============

Convert a PyPSA network stored in NetCDF (*.nc) format to a CESDM model,
plus optional export of time series to an HDF5 file.

Features:
- Multi-carrier: one CESDM EnergyCarrier + EnergyDomain per (true) energy carrier.
- Separates technology names (CCGT, OCGT, PHS, battery, ...) from carriers (gas, electricity, hydro, H2, ...).
- Creates GeographicalRegion entities from bus_country / country.
- Adds bus coordinates (latitude / longitude).
- Uses line_types (if available) for per-km r,x,b, with robust fallback to lines.r/x/b.
- Uses:
    - thermal_capacity_rating instead of apparent_power_thermal_limit
    - maximum_charging_power instead of charging_power_capacity
    - nominal_power_capacity instead of discharging_power_capacity
- Fills resource_potential_profile_reference and annual_resource_potential for:
    - EnergyConversionTechnology1x1 (from generators_t.p_max_pu)
    - EnergyStorageTechnology (from storage_units_t.inflow, stores_t.e_in)
- Exports relevant time series to HDF5 with datasets:
    - "values"       (T x N)
    - "series_names" (N)
    - "time"         (T)
"""

import os
import re
from typing import Dict, Optional, Tuple, List, Set

import sys
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../tools/"))

import numpy as np
import h5py
import pypsa  # type: ignore

from cesdm_toolbox import Model, build_model_from_yaml
from pathlib import Path

# Map PyPSA carrier names to CESDM EnergyCarrier IDs
_CARRIER_ALIASES = {
    "AC": "Electricity",
    "electricity": "Electricity",
    "Electricity": "Electricity",

    "gas": "Gas",
    "Gas": "Gas",

    "heat": "Heat",
    "Heat": "Heat",

    "H2": "Hydrogen",
    "hydrogen": "Hydrogen",

    "water": "Water",
    "Water": "Water",
}


# Map technology types to their fuel (input EnergyCarrier)
_TECH_TO_FUEL = {
    # Fossil
    "gas": "Gas",
    "gas_cc": "Gas",
    "gas_ct": "Gas",
    "OCGT": "Gas",
    "CCGT": "Gas",

    "coal": "Coal",
    "lignite": "Coal",
    "oil": "Oil",

    # Nuclear
    "nuclear": "Uranium",

    # Renewables (treated as exogenous resources)
    "wind": "Wind",
    "onwind": "Wind",
    "offwind": "Wind",

    "solar": "Solar",
    "solar_pv": "Solar",
    "pv": "Solar",

    "hydro": "Water",
    "ror": "Water",
    "run_of_river": "Water",

    # Biomass
    "biomass": "Biomass",
}


# ---------------------------------------------------------------------------
# Helpers: safe attribute/relation setting
# ---------------------------------------------------------------------------

def safe_set_attr(model: Model, entity_id: str, attr: str, value):
    """Set attribute only if value is not None."""
    if value is None:
        return
    model.add_attribute(entity_id, attr, value)


def safe_add_ref(model: Model, entity_id: str, ref_name: str, target_id: Optional[str]):
    """Add relation only if target_id is not empty."""
    if not target_id:
        return
    model.add_relation(entity_id, ref_name, target_id)


def _snapshot_weights(network: pypsa.Network) -> np.ndarray:
    """
    Return snapshot weights (typically hours) as 1D numpy array of length = snapshots.
    Falls back to all-ones if nothing useful found.
    """
    n_ts = len(network.snapshots)
    if hasattr(network, "snapshot_weightings"):
        sw = network.snapshot_weightings
        for field in ("generators", "objective"):
            if hasattr(sw, field):
                arr = np.asarray(getattr(sw, field), dtype=float)
                if arr.size == n_ts:
                    return arr
    return np.ones(n_ts, dtype=float)


# ---------------------------------------------------------------------------
# HDF5 time series export
# ---------------------------------------------------------------------------

def save_timeseries_to_hdf5(
    filename: str,
    timestamps,
    data_dict: Dict[str, np.ndarray],
):
    """Save time series to an HDF5 file using hierarchical dataset names.

    CESDM convention
    ---------------
    Each dataset is stored under a path that mirrors the CESDM entity structure:

        <EntityType>/<EntityID>/<timeseries_name>

    Examples:
        EnergyDemand/LOAD_CH/profile
        EnergyConversionTechnology1x1/GEN_CH_CCGT/availability
        EnergyStorageTechnology/STORU_CH_BATTERY/inflow

    The shared time index is stored once at:
        /time/index
    """
    directory = os.path.dirname(filename)
    if directory:
        os.makedirs(directory, exist_ok=True)

    # Store time index as fixed-length ASCII strings (portable across tools)
    ts_str = np.array([str(t) for t in timestamps], dtype="S32")

    with h5py.File(filename, "w") as f:
        time_grp = f.require_group("time")
        time_grp.create_dataset("index", data=ts_str)

        # Create each series as its own dataset (supports hierarchical paths)
        for series_path, values in data_dict.items():
            if values is None:
                continue
            arr = np.asarray(values, dtype=float)
            # allow e.g. "EnergyDemand/ID/profile" to create intermediate groups
            grp_path, ds_name = os.path.split(series_path)
            grp = f.require_group(grp_path) if grp_path else f
            if ds_name in grp:
                del grp[ds_name]
            grp.create_dataset(ds_name, data=arr)


def collect_timeseries_from_pypsa(network: pypsa.Network) -> Tuple[List, Dict[str, np.ndarray]]:
    """Extract a set of time series from a PyPSA network using CESDM HDF5 paths.

    Returns
    -------
    timestamps : list
        The network snapshots.
    data_dict : dict[str, np.ndarray]
        Mapping '<EntityType>/<EntityID>/<timeseries_name>' -> 1D array.

    Notes
    -----
    The entity IDs follow the same conventions used in the CESDM converter:
        - Loads:      EnergyDemand / _make_id('LOAD_', <load_id>)
        - Generators: EnergyConversionTechnology1x1 / _make_id('GEN_', <gen_id>)
        - Storage:    EnergyStorageTechnology / _make_id('STORU_', <storage_unit_id>)
                     and EnergyStorageTechnology / _make_id('STORE_', <store_id>)
    """
    timestamps = list(network.snapshots)
    n_ts = len(timestamps)
    data_dict: Dict[str, np.ndarray] = {}

    # Helper to safely get a series or return ones/zeros fallback
    def _get_series(df, col, default=0.0):
        try:
            if df is None:
                return np.full(n_ts, default, dtype=float)
            if col not in df.columns:
                return np.full(n_ts, default, dtype=float)
            return np.asarray(df[col], dtype=float)
        except Exception:
            return np.full(n_ts, default, dtype=float)

    # ------------------------------------------------------------------
    # Loads: demand profile (MW)
    # Stored as: EnergyDemand/<LOAD_ID>/profile
    # ------------------------------------------------------------------
    if hasattr(network, "loads_t") and hasattr(network.loads_t, "p_set"):
        for load_id in network.loads.index:
            eid = _make_id("LOAD_", str(load_id))
            path = f"EnergyDemand/{eid}/profile"
            data_dict[path] = _get_series(network.loads_t.p_set, load_id, default=0.0)

    # ------------------------------------------------------------------
    # Generators: availability / resource potential profile (p_max_pu)
    # Stored as: EnergyConversionTechnology1x1/<GEN_ID>/availability
    # ------------------------------------------------------------------
    if hasattr(network, "generators_t") and hasattr(network.generators_t, "p_max_pu"):
        for gen_id in network.generators.index:
            eid = _make_id("GEN_", str(gen_id))
            path = f"EnergyConversionTechnology1x1/{eid}/availability"
            data_dict[path] = _get_series(network.generators_t.p_max_pu, gen_id, default=1.0)

    # ------------------------------------------------------------------
    # Storage units: natural inflow profile (if present)
    # Stored as: EnergyStorageTechnology/<STORU_ID>/inflow
    # ------------------------------------------------------------------
    if hasattr(network, "storage_units_t") and hasattr(network.storage_units_t, "inflow"):
        for su_id in network.storage_units.index:
            eid = _make_id("STORU_", str(su_id))
            path = f"EnergyStorageTechnology/{eid}/inflow"
            data_dict[path] = _get_series(network.storage_units_t.inflow, su_id, default=0.0)

    # ------------------------------------------------------------------
    # Stores: inflow / e_in profile (if present)
    # Stored as: EnergyStorageTechnology/<STORE_ID>/inflow
    # ------------------------------------------------------------------
    if hasattr(network, "stores_t") and hasattr(network.stores_t, "e_in"):
        for store_id in network.stores.index:
            eid = _make_id("STORE_", str(store_id))
            path = f"EnergyStorageTechnology/{eid}/inflow"
            data_dict[path] = _get_series(network.stores_t.e_in, store_id, default=0.0)

    return timestamps, data_dict



def canonicalize_carrier_name(name: str) -> Optional[str]:
    """Return canonical carrier name if `name` represents a true carrier, else None."""
    if name is None:
        return None
    s = str(name).strip().lower()
    if s == "" or s == "nan":
        return None
    if s in _CARRIER_ALIASES:
        return _CARRIER_ALIASES[s]
    # also allow direct canonical names
    if s in set(_CARRIER_ALIASES.values()):
        return s
    return None


def classify_carrier_or_technology(name: str) -> Tuple[str, str]:
    """
    Classify a PyPSA 'carrier' string as either ('carrier', canonical_carrier)
    or ('technology', original_string).
    """
    canonical = canonicalize_carrier_name(name)
    if canonical is not None:
        return "carrier", canonical
    return "technology", str(name)


def guess_fuel_from_technology(tech_name: str) -> Optional[str]:
    """
    Given a technology-like string (e.g. 'CCGT', 'PHS'), guess the fuel / carrier
    (e.g. 'gas', 'hydro', 'electricity').
    """
    if tech_name is None:
        return None
    # maybe it's actually a carrier in disguise
    canonical = canonicalize_carrier_name(tech_name)
    if canonical is not None:
        return canonical
    s = str(tech_name).strip().lower()
    return _TECH_TO_FUEL.get(s)


def _make_id(prefix: str, name: str) -> str:
    """
    Sanitize a string to be used as an entity id: only letters, digits, underscore.
    """
    s = re.sub(r"[^0-9a-zA-Z_]+", "_", str(name))
    if not s:
        s = "X"
    if s[0].isdigit():
        s = "_" + s
    return f"{prefix}{s}"


def collect_all_carrier_strings(network: pypsa.Network) -> Set[str]:
    """Collect all distinct strings that appear as 'carrier' in the network."""
    names: Set[str] = set()

    if hasattr(network, "carriers") and not network.carriers.empty:
        names.update(network.carriers.index.astype(str))

    def add_from_df(df):
        if df is None or df.empty or "carrier" not in df.columns:
            return
        names.update(df.carrier.dropna().astype(str).unique())

    for df in [
        getattr(network, "generators", None),
        getattr(network, "storage_units", None),
        getattr(network, "stores", None),
        getattr(network, "loads", None),
        getattr(network, "links", None),
    ]:
        add_from_df(df)

    return names


def build_carrier_domain_entities(
    network: pypsa.Network,
    model: Model,
) -> Tuple[Dict[str, str], Dict[str, str], str, str]:
    """
    Create EnergyCarrier and EnergyDomain entities for all *true* energy carriers.

    Returns
    -------
    carrier_to_ec : dict[canonical_carrier -> EnergyCarrier id]
    carrier_to_ed : dict[canonical_carrier -> EnergyDomain id]
    default_ec : EnergyCarrier id to use as fallback (typically electricity)
    default_ed : EnergyDomain id to use as fallback
    """
    carrier_strings = collect_all_carrier_strings(network)

    energy_carriers: Set[str] = set()

    # 1st pass: direct carriers
    for name in carrier_strings:
        kind, val = classify_carrier_or_technology(name)
        if kind == "carrier":
            energy_carriers.add(val)

    # 2nd pass: fuels implied by technologies
    for name in carrier_strings:
        kind, _ = classify_carrier_or_technology(name)
        if kind == "technology":
            fuel = guess_fuel_from_technology(name)
            if fuel is not None:
                energy_carriers.add(fuel)

    # Ensure we at least have 'electricity' as a carrier
    if "electricity" not in energy_carriers:
        energy_carriers.add("electricity")

    carrier_to_ec: Dict[str, str] = {}
    carrier_to_ed: Dict[str, str] = {}

    for c in sorted(energy_carriers):
        ec_id = _make_id("EC_", c)
        ed_id = _make_id("ED_", c)

        model.add_entity("EnergyCarrier", ec_id)
        safe_set_attr(model, ec_id, "name", c)
        safe_set_attr(model, ec_id, "energy_carrier_type", c)
        safe_set_attr(model, ec_id, "co2_emission_intensity", 0.0)
        safe_set_attr(model, ec_id, "energy_carrier_cost", 0.0)

        model.add_entity("EnergyDomain", ed_id)
        safe_set_attr(model, ed_id, "name", f"{c}_domain")
        safe_add_ref(model, ed_id, "hasEnergyCarrier", ec_id)

        carrier_to_ec[c] = ec_id
        carrier_to_ed[c] = ed_id

    # Choose defaults
    if "electricity" in carrier_to_ec:
        default_ec = carrier_to_ec["electricity"]
        default_ed = carrier_to_ed["electricity"]
    else:
        # fall back to first key (deterministic: sorted above)
        first_key = sorted(energy_carriers)[0]
        default_ec = carrier_to_ec[first_key]
        default_ed = carrier_to_ed[first_key]

    return carrier_to_ec, carrier_to_ed, default_ec, default_ed


# ---------------------------------------------------------------------------
# Main builder: PyPSA NC -> CESDM Model
# ---------------------------------------------------------------------------

def build_cesdm_from_pypsa_nc(
    nc_path: str,
    schema_dir: str,
    region_name: str = "DefaultRegion",
) -> Model:
    """
    Build a CESDM Model from a PyPSA NetCDF file.

    Parameters
    ----------
    nc_path : str
        Path to the PyPSA *.nc file.
    schema_dir : str
        Path to CESDM schema directory (folder with *.yaml files).
    region_name : str
        Default region name if no bus_country/country is provided.

    Returns
    -------
    Model
        Populated CESDM Model instance.
    """
    network = pypsa.Network(nc_path)
    model = build_model_from_yaml(schema_dir)

    # -----------------------------------------------------------------------
    # EnergySystemModel
    # -----------------------------------------------------------------------
    esm_id = "PyPSA_Model"
    model.add_entity("EnergySystemModel", esm_id)
    safe_set_attr(
        model,
        esm_id,
        "long_name",
        f"PyPSA import from {os.path.basename(nc_path)}",
    )
    # co2_price is required as string; default 0
    safe_set_attr(model, esm_id, "co2_price", "0")

    # -----------------------------------------------------------------------
    # EnergyCarriers and EnergyDomains (multi-carrier, Option B)
    # -----------------------------------------------------------------------
    carrier_to_ec, carrier_to_ed, default_ec, default_ed = build_carrier_domain_entities(
        network, model
    )

    # -----------------------------------------------------------------------
    # GeographicalRegion from bus_country / country
    # -----------------------------------------------------------------------
    region_by_code: Dict[str, str] = {}
    bus_country_col = None
    if "bus_country" in network.buses.columns:
        bus_country_col = "bus_country"
    elif "country" in network.buses.columns:
        bus_country_col = "country"

    default_region_id = None
    if bus_country_col is None:
        default_region_id = _make_id("GR_", region_name)
        model.add_entity("GeographicalRegion", default_region_id)
        safe_set_attr(model, default_region_id, "name", region_name)

    # -----------------------------------------------------------------------
    # ElectricityNode (buses) with geographical regions, coordinates, and domains
    # -----------------------------------------------------------------------
    bus_to_node: Dict[str, str] = {}
    bus_to_domain: Dict[str, str] = {}
    bus_to_carrier: Dict[str, str] = {}

    weights = _snapshot_weights(network)

    for bus_id, bus in network.buses.iterrows():
        node_id = _make_id("GN_", bus_id)
        bus_to_node[bus_id] = node_id

        model.add_entity("ElectricityNode", node_id)
        safe_set_attr(model, node_id, "name", str(bus_id))

        # nominal voltage
        v_nom = getattr(bus, "v_nom", None)
        if v_nom is None:
            v_nom = 0.0
        safe_set_attr(model, node_id, "nominal_voltage", float(v_nom))

        # determine bus carrier (usually electricity, but may be heat, H2, gas, ...)
        bus_canonical_carrier = None
        if "carrier" in network.buses.columns:
            bc = getattr(bus, "carrier", None)
            if bc is not None and str(bc) != "nan":
                kind, val = classify_carrier_or_technology(bc)
                if kind == "carrier":
                    bus_canonical_carrier = val
                else:
                    # try fuel guess from tech-like value
                    guessed = guess_fuel_from_technology(bc)
                    if guessed is not None:
                        bus_canonical_carrier = guessed

        if bus_canonical_carrier is None:
            bus_canonical_carrier = "electricity"

        bus_to_carrier[bus_id] = bus_canonical_carrier
        ed_id = carrier_to_ed.get(bus_canonical_carrier, default_ed)
        bus_to_domain[bus_id] = ed_id
        safe_add_ref(model, node_id, "isInEnergyDomain", ed_id)

        # Geographical region for the bus
        if bus_country_col is not None:
            ccode = getattr(bus, bus_country_col, None)
            if ccode is not None and str(ccode) != "" and str(ccode) != "nan":
                ccode = str(ccode)
                if ccode not in region_by_code:
                    gr_id = _make_id("GR_", ccode)
                    region_by_code[ccode] = gr_id
                    model.add_entity("GeographicalRegion", gr_id)
                    safe_set_attr(model, gr_id, "name", ccode)
                safe_add_ref(
                    model,
                    node_id,
                    "isInGeographicalRegion",
                    region_by_code[ccode],
                )
            else:
                if default_region_id is None:
                    default_region_id = _make_id("GR_", region_name)
                    model.add_entity("GeographicalRegion", default_region_id)
                    safe_set_attr(model, default_region_id, "name", region_name)
                safe_add_ref(model, node_id, "isInGeographicalRegion", default_region_id)
        else:
            safe_add_ref(model, node_id, "isInGeographicalRegion", default_region_id)

        # Coordinates (lat/lon) if present
        if "x" in network.buses.columns:
            lat = getattr(bus, "x", None)
            if lat is not None and str(lat) != "nan":
                try:
                    safe_set_attr(model, node_id, "latitude", float(lat))
                except (TypeError, ValueError):
                    pass
        if "y" in network.buses.columns:
            lon = getattr(bus, "y", None)
            if lon is not None and str(lon) != "nan":
                try:
                    safe_set_attr(model, node_id, "longitude", float(lon))
                except (TypeError, ValueError):
                    pass

    map_line_types = {}
    map_line_types['Al/St 240/40 2-bundle 220.0'] = {"r": 0.059, "x": 0.300, "b": 3.6}
    map_line_types['Al/St 240/40 3-bundle 300.0'] = {"r": 0.040, "x": 0.270, "b": 4.1}
    map_line_types['Al/St 240/40 4-bundle 380.0'] = {"r": 0.030, "x": 0.260, "b": 4.2}

    # -----------------------------------------------------------------------
    # TransmissionLine (AC lines) with per-km r,x,b if available
    # -----------------------------------------------------------------------
    for line_id, line in network.lines.iterrows():
        eid = _make_id("TL_", line_id)

        length = getattr(line, "length", None)
        n_par = getattr(line, "num_parallel", None)
        s_nom = getattr(line, "s_nom", None)

        if n_par < 1:
            continue

        model.add_entity("TransmissionLine", eid)
        safe_set_attr(model, eid, "name", str(line_id))

        r_per_km = x_per_km = b_per_km = None
        line_type_name = getattr(line, "type", None)

        # Try line_types table if available
        if line_type_name and hasattr(network, "line_types"):
            lt = network.line_types
            if line_type_name in lt.index:
                cols = lt.columns

                # direct r/x/c columns
                if "r" in cols:
                    r_per_km = float(lt.at[line_type_name, "r"])
                if "x" in cols:
                    x_per_km = float(lt.at[line_type_name, "x"])

                # typical PyPSA-Eur names
                if "r_ohm_per_km" in cols and r_per_km is None:
                    r_per_km = float(lt.at[line_type_name, "r_ohm_per_km"])
                if "x_ohm_per_km" in cols and x_per_km is None:
                    x_per_km = float(lt.at[line_type_name, "x_ohm_per_km"])

                # capacitance to susceptance
                c_per_km = None
                if "c" in cols:
                    c_per_km = float(lt.at[line_type_name, "c"])
                elif "c_nf_per_km" in cols:
                    c_per_km = float(lt.at[line_type_name, "c_nf_per_km"]) * 1e-9
                if c_per_km is not None:
                    freq = getattr(network, "frequency", 50.0)
                    b_per_km = 2.0 * np.pi * float(freq) * c_per_km

        if line_type_name in map_line_types:
            r_per_km = map_line_types[line_type_name]['r']
            x_per_km = map_line_types[line_type_name]['x']
            b_per_km = map_line_types[line_type_name]['b']
        else:
            print(line_type_name)

        safe_set_attr(model, eid, "series_resistance", r_per_km)
        safe_set_attr(model, eid, "series_reactance", x_per_km)
        safe_set_attr(model, eid, "shunt_susceptance", b_per_km)
        safe_set_attr(model, eid, "line_length", float(length) if length is not None else None)

        # CHANGED: thermal_capacity_rating instead of apparent_power_thermal_limit
        safe_set_attr(
            model,
            eid,
            "thermal_capacity_rating",
            float(s_nom) if s_nom is not None else None,
        )
        safe_set_attr(
            model,
            eid,
            "parallel_circuit_count",
            int(n_par) if n_par is not None else None,
        )

        isFromNodeOf = bus_to_node.get(str(line.bus0))
        isToNodeOf = bus_to_node.get(str(line.bus1))
        safe_add_ref(model, eid, "isFromNodeOf", isFromNodeOf)
        safe_add_ref(model, eid, "isToNodeOf", isToNodeOf)

        # energy domain from from-bus
        ed_id = None
        if str(line.bus0) in bus_to_domain:
            ed_id = bus_to_domain[str(line.bus0)]
        safe_add_ref(model, eid, "isInEnergyDomain", ed_id)

    # -----------------------------------------------------------------------
    # TwoWindingPowerTransformer (transformers)
    # -----------------------------------------------------------------------
    for trafo_id, trafo in network.transformers.iterrows():
        eid = _make_id("TR_", trafo_id)
        model.add_entity("TwoWindingPowerTransformer", eid)
        safe_set_attr(model, eid, "name", str(trafo_id))

        s_nom = getattr(trafo, "s_nom", None)
        safe_set_attr(
            model,
            eid,
            "rated_apparent_power",
            float(s_nom) if s_nom is not None else None,
        )

        bus0 = str(trafo.bus0)
        bus1 = str(trafo.bus1)
        v0 = float(network.buses.at[bus0, "v_nom"]) if bus0 in network.buses.index else 0.0
        v1 = float(network.buses.at[bus1, "v_nom"]) if bus1 in network.buses.index else 0.0

        safe_set_attr(model, eid, "rated_primary_voltage", v0)
        safe_set_attr(model, eid, "rated_secondary_voltage", v1)

        x_pu = getattr(trafo, "x_pu", None)
        r_pu = getattr(trafo, "r_pu", None)
        z_pu = None
        if x_pu is not None or r_pu is not None:
            x_val = float(x_pu) if x_pu is not None else 0.0
            r_val = float(r_pu) if r_pu is not None else 0.0
            z_pu = (x_val**2 + r_val**2) ** 0.5

        if z_pu is not None:
            safe_set_attr(model, eid, "short_circuit_voltage", 100.0 * z_pu)
        else:
            safe_set_attr(model, eid, "short_circuit_voltage", 0.0)

        isFromNodeOf = bus_to_node.get(bus0)
        isToNodeOf = bus_to_node.get(bus1)
        safe_add_ref(model, eid, "isFromNodeOf", isFromNodeOf)
        safe_add_ref(model, eid, "isToNodeOf", isToNodeOf)

        ed_id = bus_to_domain.get(bus0, default_ed)
        safe_add_ref(model, eid, "isInEnergyDomain", ed_id)

    # -----------------------------------------------------------------------
    # EnergyDemand (loads) – aggregate annual energy
    # -----------------------------------------------------------------------
    for load_id, load in network.loads.iterrows():
        eid = _make_id("LOAD_", load_id)
        model.add_entity("EnergyDemand", eid)
        safe_set_attr(model, eid, "name", str(load_id))

        bus = str(load.bus)
        node_id = bus_to_node.get(bus)
        safe_add_ref(model, eid, "isConnectedToNode", node_id)

        # Time series reference (stored in HDF5 if exported)
        safe_set_attr(model, eid, "demand_profile_reference", f"EnergyDemand/{eid}/profile")

        annual_energy = 0.0
        try:
            if hasattr(network, "loads_t") and hasattr(network.loads_t, "p_set"):
                if load_id in network.loads_t.p_set.columns:
                    p_series = np.asarray(network.loads_t.p_set[load_id], dtype=float)  # MW
                    annual_energy = float((p_series * weights).sum())
        except Exception:
            annual_energy = 0.0

        # Fallback if no time series
        if annual_energy == 0.0:
            p_set = getattr(load, "p_set", None)
            if p_set is not None and len(network.snapshots) > 0:
                annual_energy = float(p_set) * float(len(network.snapshots))

        safe_set_attr(model, eid, "annual_energy_demand", annual_energy)

    # -----------------------------------------------------------------------
    # EnergyConversionTechnology1x1 (generators)
    # -----------------------------------------------------------------------
    for gen_id, gen in network.generators.iterrows():
        eid = _make_id("GEN_", gen_id)
        model.add_entity("EnergyConversionTechnology1x1", eid)
        safe_set_attr(model, eid, "name", str(gen_id))

        bus = str(gen.bus)
        node_id = bus_to_node.get(bus)
        safe_set_attr(model, eid, "input_origin", "exogenous")
        safe_add_ref(model, eid, "isOutputNodeOf", node_id)

        # Technology vs carrier
        carrier_str = getattr(gen, "carrier", None)
        tech_str = None
        hasFuelCarrier = None

        if carrier_str is not None and str(carrier_str) != "nan":
            kind, val = classify_carrier_or_technology(carrier_str)
            if kind == "carrier":
                hasFuelCarrier = val  # e.g. 'wind', 'solar', 'gas'
                tech_str = getattr(gen, "type", None) or str(carrier_str)
            else:
                tech_str = str(carrier_str)
                hasFuelCarrier = guess_fuel_from_technology(carrier_str)
        else:
            tech_str = getattr(gen, "type", None)

        if tech_str is not None:
            safe_set_attr(model, eid, "generator_technology_type", str(tech_str))

        eff = getattr(gen, "efficiency", None)
        if eff is None:
            eff = 1.0
        safe_set_attr(model, eid, "energy_conversion_efficiency", float(eff))

        p_nom = getattr(gen, "p_nom", None)
        safe_set_attr(
            model,
            eid,
            "nominal_power_capacity",
            float(p_nom) if p_nom is not None else None,
        )

        mc = getattr(gen, "marginal_cost", None)
        safe_set_attr(
            model,
            eid,
            "variable_operating_cost",
            float(mc) if mc is not None else None,
        )

        # Output carrier = bus carrier
        bus_carrier = bus_to_carrier.get(bus, "electricity")
        out_ec = carrier_to_ec.get(bus_carrier, default_ec)

        # Input carrier = hasFuelCarrier if known, otherwise bus_carrier
        in_carrier = hasFuelCarrier or bus_carrier
        in_ec = carrier_to_ec.get(in_carrier, out_ec)

        safe_add_ref(model, eid, "hasInputEnergyCarrier", in_ec)
        safe_add_ref(model, eid, "hasOutputEnergyCarrier", out_ec)

        # Resource potential (profile + annual) from p_max_pu if present
        profile_name = None
        annual_resource = 0.0
        try:
            if hasattr(network, "generators_t") and hasattr(network.generators_t, "p_max_pu"):
                if gen_id in network.generators_t.p_max_pu.columns:
                    profile_name = f"EnergyConversionTechnology1x1/{eid}/availability"
                    p_max_pu = np.asarray(network.generators_t.p_max_pu[gen_id], dtype=float)
                    p_nom_val = float(p_nom) if p_nom is not None else 0.0
                    annual_resource = float((p_max_pu * p_nom_val * weights).sum())
        except Exception:
            profile_name = None
            annual_resource = 0.0

        if profile_name:
            safe_set_attr(
                model,
                eid,
                "resource_potential_profile_reference",
                profile_name,
            )
        if annual_resource > 0.0:
            safe_set_attr(
                model,
                eid,
                "annual_resource_potential",
                annual_resource,
            )

    # -----------------------------------------------------------------------
    # EnergyStorageTechnology (storage_units + stores)
    # -----------------------------------------------------------------------

    # storage_units
    for su_id, su in network.storage_units.iterrows():
        eid = _make_id("STORU_", su_id)
        model.add_entity("EnergyStorageTechnology", eid)
        safe_set_attr(model, eid, "name", str(su_id))

        bus = str(su.bus)
        node_id = bus_to_node.get(bus)
        safe_add_ref(model, eid, "isConnectedToNode", node_id)

        p_nom = getattr(su, "p_nom", None)
        e_nom = getattr(su, "energy_nom", None)
        max_hours = getattr(su, "max_hours", None)

        if e_nom is None and p_nom is not None and max_hours is not None:
            e_nom = float(p_nom) * float(max_hours)

        # CHANGED:
        #   maximum_charging_power instead of charging_power_capacity
        #   nominal_power_capacity instead of discharging_power_capacity
        safe_set_attr(
            model,
            eid,
            "maximum_charging_power",
            float(p_nom) if p_nom is not None else None,
        )
        safe_set_attr(
            model,
            eid,
            "nominal_power_capacity",
            float(p_nom) if p_nom is not None else None,
        )
        safe_set_attr(
            model,
            eid,
            "energy_storage_capacity",
            float(e_nom) if e_nom is not None else None,
        )

        eta_store = getattr(su, "efficiency_store", None)
        eta_dispatch = getattr(su, "efficiency_dispatch", None)
        safe_set_attr(
            model,
            eid,
            "charging_efficiency",
            float(eta_store) if eta_store is not None else 1.0,
        )
        safe_set_attr(
            model,
            eid,
            "discharging_efficiency",
            float(eta_dispatch) if eta_dispatch is not None else 1.0,
        )

        # Storage in PyPSA usually stores the same carrier as the bus
        bus_carrier = bus_to_carrier.get(bus, "electricity")
        ec_id = carrier_to_ec.get(bus_carrier, default_ec)
        safe_add_ref(model, eid, "hasInputEnergyCarrier", ec_id)
        safe_add_ref(model, eid, "hasOutputEnergyCarrier", ec_id)

        # Resource potential from inflow (e.g. hydro inflow)
        profile_name = None
        annual_resource = 0.0
        try:
            if hasattr(network, "storage_units_t") and hasattr(network.storage_units_t, "inflow"):
                if su_id in network.storage_units_t.inflow.columns:
                    profile_name = f"EnergyStorageTechnology/{eid}/inflow"
                    inflow = np.asarray(network.storage_units_t.inflow[su_id], dtype=float)
                    annual_resource = float((inflow * weights).sum())
        except Exception:
            profile_name = None
            annual_resource = 0.0

        if profile_name:
            safe_set_attr(
                model,
                eid,
                "natural_inflow_profile_reference",
                profile_name,
            )
        if annual_resource > 0.0:
            safe_set_attr(
                model,
                eid,
                "annual_natural_inflow_volume",
                annual_resource,
            )

    # stores
    for st_id, st in network.stores.iterrows():
        eid = _make_id("STORS_", st_id)
        model.add_entity("EnergyStorageTechnology", eid)
        safe_set_attr(model, eid, "name", str(st_id))

        bus = str(st.bus)
        node_id = bus_to_node.get(bus)
        safe_set_attr(model, eid, "input_origin", "exogenous")
        safe_add_ref(model, eid, "isOutputNodeOf", node_id)

        e_nom = getattr(st, "e_nom", None)
        safe_set_attr(
            model,
            eid,
            "energy_storage_capacity",
            float(e_nom) if e_nom is not None else None,
        )

        bus_carrier = bus_to_carrier.get(bus, "electricity")
        ec_id = carrier_to_ec.get(bus_carrier, default_ec)
        safe_add_ref(model, eid, "hasInputEnergyCarrier", ec_id)
        safe_add_ref(model, eid, "hasOutputEnergyCarrier", ec_id)

        # Resource potential from inflow e_in (e.g. reservoir inflow)
        profile_name = None
        annual_resource = 0.0
        try:
            if hasattr(network, "stores_t") and hasattr(network.stores_t, "e_in"):
                if st_id in network.stores_t.e_in.columns:
                    profile_name = f"EnergyStorageTechnology/{eid}/inflow"
                    e_in = np.asarray(network.stores_t.e_in[st_id], dtype=float)
                    annual_resource = float((e_in * weights).sum())
        except Exception:
            profile_name = None
            annual_resource = 0.0

        if profile_name:
            safe_set_attr(
                model,
                eid,
                "natural_inflow_profile_reference",
                profile_name,
            )
        if annual_resource > 0.0:
            safe_set_attr(
                model,
                eid,
                "annual_natural_inflow_volume",
                annual_resource,
            )

    return model



