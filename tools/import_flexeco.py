from pathlib import Path
import json
from cesdm_toolbox import build_model_from_yaml, Model, Entity
import json
import os

import h5py

def save_timeseries_to_hdf5(filename, timestamps, data_dict):
    """Save CESDM time series data to an HDF5 file using a hierarchical layout.

    This implements the CESDM time series convention described in the docs:

        <EntityType>/<EntityID>/<timeseries_name>

    Practical note:
    - Some importers (e.g. FlexEco) may deliver profile keys that are not yet
      CESDM paths (e.g. "xi_123"). In that case we store them under:

        profiles/<profile_key>

      and the CESDM model can reference them via the same string
      (e.g. "profiles/xi_123").

    Parameters
    ----------
    filename : str
        Output .h5 filename (directories will be created).
    timestamps : array-like | None
        Optional time index. If provided, written to /time/index.
        If None, no time index is written.
    data_dict : dict[str, array-like]
        Mapping from dataset key/path -> 1D array of values.
        If the key contains '/', it is treated as an HDF5 dataset path.
        Otherwise it is stored under profiles/<key>.
    """
    import os
    import numpy as np
    import h5py

    # Ensure output directory exists
    directory = os.path.dirname(filename)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with h5py.File(filename, "w") as f:
        # Optional shared time index
        if timestamps is not None:
            ts = np.asarray(timestamps)
            # Store timestamps as strings if not purely numeric
            if ts.dtype.kind in {"U", "S", "O"}:
                ts = ts.astype("S64")
            f.create_dataset("time/index", data=ts)

        # Store each series as its own dataset
        for key, values in (data_dict or {}).items():
            if key is None:
                continue

            # Determine dataset path
            if isinstance(key, bytes):
                key = key.decode("utf-8")

            is_path = ("/" in str(key))
            ds_path = str(key).lstrip("/") if is_path else str(key).lstrip("/")
            # alias_path = None if is_path else f"profiles/{ds_path}"
            ds_path = str(ds_path).lstrip("/")

            arr = np.asarray(values)

            # Ensure parent groups exist
            parent = os.path.dirname(ds_path)
            if parent:
                f.require_group(parent)

            # Overwrite-safe behavior: delete existing dataset if present
            if ds_path in f:
                del f[ds_path]
            f.create_dataset(ds_path, data=arr)

            # # Optional alias under profiles/<key> for non-path keys
            # if alias_path:
            #     parent2 = os.path.dirname(alias_path)
            #     if parent2:
            #         f.require_group(parent2)
            #     if alias_path in f:
            #         del f[alias_path]
            #     f[alias_path] = f[ds_path]

def export_to_flexeco(model, output_path: str | Path):
    """
    Reverse of import_from_flexeco:
    Take a CESDM Model instance (from cesdm_toolbox) and export it back
    to a european_data.jpn-like JSON with a "PowerSystemElements" list.

    Assumes import_from_flexeco() naming conventions:
      - ElectricityNode ids:            "node_<uid>"
      - EnergyDemand ids:                "load_<uid>"
      - Generators:              "gen_<uid>"
      - EnergyStorageTechnology (pumped):        "storage_pump_<uid>"
      - EnergyStorageTechnology (reservoir dam): "storage_dam_<uid>"
      - NetTransferCapacity:
          * "line_<uid>"  -> PN_Line
          * "tr2_<uid>"   -> PN_TR2
          * "hvdc_<uid>"  -> PN_HVDC
          * "ntc_<uid>"   -> PN_NTC
    """

    # only folder part:
    directory = os.path.dirname(output_path)   # -> "./path/folder"
    # create the folder if does not exist
    os.makedirs(directory, exist_ok=True)

    output_path = Path(output_path)
    elements = []

    # ------------------------------------------------------------------
    # Helpers (note: we always go through ent.data)
    # ------------------------------------------------------------------

    # Global mapping from CESDM IDs to Flexeco UIDs (ints)
    used_uids: set[int] = set()
    id_to_uid: dict[str, int] = {}

    def uid_from_prefixed_id(ent_id: str, prefix: str) -> int:
        """
        Map a CESDM entity id (string) to a Flexeco UID (int).

        - If we've already assigned a UID to this ent_id, reuse it.
        - Else, if ent_id starts with the expected prefix and the suffix is numeric,
          reuse that numeric suffix as UID (for round-trips).
        - Otherwise, assign a new integer UID that is not yet used.
        """
        # Reuse existing assignment
        if ent_id in id_to_uid:
            return id_to_uid[ent_id]

        uid: int | None = None

        # Try to reuse numeric suffix if it matches the prefix
        if ent_id.startswith(prefix):
            suffix = ent_id[len(prefix):]
            if suffix.isdigit():
                uid = int(suffix)

        # If no usable suffix: assign a fresh UID
        if uid is None:
            uid = max(used_uids) + 1 if used_uids else 1

        # Guarantee global uniqueness
        while uid in used_uids:
            uid += 1

        used_uids.add(uid)
        id_to_uid[ent_id] = uid
        return uid


    def get_attr_value(entity, name, default=None):
        """Return the 'value' part of an attribute (handles AttributeValue and legacy scalars)."""
        raw = getattr(entity, "data", {}).get(name, default)

        if isinstance(raw, dict) and "value" in raw:
            return raw["value"]

        if isinstance(entity, dict) and name in entity:
            return entity[name]
        return raw

    def get_attr_value_unit_prov(entity, name, default=None):
        """Return (value, unit, provenance_ref) for an attribute."""
        raw = getattr(entity, "data", {}).get(name, default)
        if isinstance(raw, dict) and "value" in raw:
            return raw.get("value"), raw.get("unit"), raw.get("provenance_ref")
        if isinstance(entity, dict) and name in entity:
            return entity[name], None, None
        # legacy scalar case
        return raw, None, None

    node_entities = model.entities.get("ElectricityNode", {})
    node_entities = node_entities | (model.entities.get("EnergyNode", {}))
    carrier_entities = model.entities.get("EnergyCarrier", {})
    ntc_entities = model.entities.get("NetTransferCapacity", {})
    line_entities = model.entities.get("TransmissionLine", {})
    tr2_entities = model.entities.get("TwoWindingPowerTransformer", {})
    load_entities = model.entities.get("EnergyDemand", {})
    storage_entities = model.entities.get("EnergyStorageTechnology", {})
    conv1x1_entities = model.entities.get("EnergyConversionTechnology1x1", {})
    storagetype_entities = model.entities.get("StorageTechnologyType", {})
    techtype_entities = model.entities.get("TechnologyType", {})
    energysystemmodel_entities = model.entities.get("EnergySystemModel", {})

    # EnergyNode id -> bus uid (from "node_<uid>")
    node_id_to_uid = {}
    node_uid = 10000001
    for nid, ent in node_entities.items():
        node_id_to_uid[nid] = node_uid
        node_uid = node_uid + 1

    ntc_id_to_uid = {}
    ntc_uid = 20000001
    for nid, ent in ntc_entities.items():
        ntc_id_to_uid[nid] = ntc_uid
        ntc_uid = ntc_uid + 1

    line_id_to_uid = {}
    line_uid = 21000001
    for nid, ent in line_entities.items():
        line_id_to_uid[nid] = line_uid
        line_uid = line_uid + 1

    tr2_id_to_uid = {}
    tr2_uid = 22000001
    for nid, ent in tr2_entities.items():
        tr2_id_to_uid[nid] = tr2_uid
        tr2_uid = tr2_uid + 1

    load_id_to_uid = {}
    load_uid = 30000001
    for nid, ent in load_entities.items():
        load_id_to_uid[nid] = load_uid
        load_uid = load_uid + 1

    gen_id_to_uid = {}
    gen_uid = 40000001
    for nid, ent in conv1x1_entities.items():
        gen_id_to_uid[nid] = gen_uid
        gen_uid = gen_uid + 1

    storage_id_to_uid = {}
    storage_uid = 50000001
    for nid, ent in storage_entities.items():
        storage_id_to_uid[nid] = storage_uid
        storage_uid = storage_uid + 1

    def bus_uid_from_node_id(node_id: str | None) -> int | None:
        """
        Map CESDM ElectricityNode id (string) to Flexeco bus UID (int).

        Raises an error if the ElectricityNode is unknown, to avoid writing
        an inconsistent Flexeco file.
        """
        
        if node_id is None:
            return None
        try:
            if node_id in node_id_to_uid:
                return node_id_to_uid[node_id]
            else:
                return None

        except KeyError:
            raise KeyError(
                f"ElectricityNode id '{node_id}' has no assigned Flexeco bus uid. "
                "Make sure it exists in model.entities['ElectricityNode'] and follows the "
                "expected naming (e.g. 'node_<uid>') or adjust node_id_to_uid logic."
            )

    # EnergyCarrier helpers use ent.data
    def carrier_name_from_id(cid: str | None) -> str | None:
        if cid is None:
            return None
        if cid.startswith("c_"):
            return cid[2:]
        return cid

    def carrier_cost_from_id(cid: str | None) -> float | None:
        if cid is None:
            return None
        ent = carrier_entities.get(cid)
        if not ent:
            return None
        return get_attr_value(ent,"energy_carrier_cost", 0.0) 

    def carrier_co2_from_id(cid: str | None) -> float | None:
        if cid is None:
            return None
        ent = carrier_entities.get(cid)
        if not ent:
            return None
        return get_attr_value(ent,"co2_emission_intensity", 0.0)

    map_busses = {}
    # ------------------------------------------------------------------
    # 1) ElectricityNode → PN_Busbar
    # ------------------------------------------------------------------
    for nid, ent in node_entities.items():

        uid = node_id_to_uid[nid]

        bus_el = {
            "class": "PN_Busbar",
            "uid": uid,
            "name": get_attr_value(ent,"name", nid),
            "Un": get_attr_value(ent,"nominal_voltage",0.0),
        }

        isInGeographicalRegion = get_attr_value(ent,"isInGeographicalRegion","")
        if isInGeographicalRegion and isInGeographicalRegion != "region_europe":
            # if you want to distinguish zone/country, add logic here
            bus_el["zone_name"] = isInGeographicalRegion
            bus_el["country"] = isInGeographicalRegion

        map_busses[uid] = bus_el
        elements.append(bus_el)

    # ------------------------------------------------------------------
    # 2) NetTransferCapacity → PN_Line / PN_TR2 / PN_HVDC / PN_NTC
    # ------------------------------------------------------------------
    for eid, ent in line_entities.items():

        isFromNodeOf = get_attr_value(ent,"isFromNodeOf","")
        isToNodeOf = get_attr_value(ent,"isToNodeOf","")
        bus1_uid = bus_uid_from_node_id(isFromNodeOf)
        bus2_uid = bus_uid_from_node_id(isToNodeOf)

        uid = line_id_to_uid[lid]

        el = {
            "class": "PN_Line",
            "uid": uid,
            "name": get_attr_value(ent,"name", eid),
            "bus1_uid": bus1_uid,
            "bus2_uid": bus2_uid,
            "r": get_attr_value(ent,"series_resistance", 0.0),
            "x": get_attr_value(ent,"series_reactance", 0.1),
            "b": get_attr_value(ent,"shunt_susceptance", 0.1),
            "Length": get_attr_value(ent,"line_length", 1.0),
            "Smax": get_attr_value(ent,"thermal_capacity_rating", 0.0),
        }

        elements.append(el)

    for eid, ent in tr2_entities.items():

        isFromNodeOf = get_attr_value(ent,"isFromNodeOf","")
        isToNodeOf = get_attr_value(ent,"isToNodeOf","")
        bus1_uid = bus_uid_from_node_id(isFromNodeOf)
        bus2_uid = bus_uid_from_node_id(isToNodeOf)

        uid = tr2_id_to_uid[lid]

        el = {
            "class": "PN_TR2",
            "uid": uid,
            "name": get_attr_value(ent,"name", eid),
            "bus1_uid": bus1_uid,
            "bus2_uid": bus2_uid,
            "SR": get_attr_value(ent,"rated_apparent_power", 0.0),
            "UR1": get_attr_value(ent,"rated_primary_voltage", 0.0),
            "UR2": get_attr_value(ent,"rated_secondary_voltage", 0.0),
            "Smax": get_attr_value(ent,"rated_apparent_power", 0.0),
            "Usc": get_attr_value(ent,"short_circuit_voltage", 0.1),
        }

        elements.append(el)

    for eid, ent in ntc_entities.items():

        maximum_power_flow_1_to_2 = get_attr_value(ent,"maximum_power_flow_1_to_2",0.0)
        maximum_power_flow_2_to_1 = get_attr_value(ent,"maximum_power_flow_2_to_1", maximum_power_flow_1_to_2)

        isFromNodeOf = get_attr_value(ent,"isFromNodeOf","")
        isToNodeOf = get_attr_value(ent,"isToNodeOf","")
        bus1_uid = bus_uid_from_node_id(isFromNodeOf)
        bus2_uid = bus_uid_from_node_id(isToNodeOf)

        uid = ntc_id_to_uid[eid]
        P1max = maximum_power_flow_1_to_2
        P2max = maximum_power_flow_2_to_1
        Pmax = max(v for v in (P1max, P2max) if v is not None) if (P1max or P2max) else None
        el = {
            "class": "PN_NTC",
            "uid": uid,
            "name": get_attr_value(ent,"name", eid),
            "bus1_uid": bus1_uid,
            "bus2_uid": bus2_uid,
            "P1max": P1max,
            "P2max": P2max,
            "Pmax": Pmax,
        }

        el["technology"] = "NTC"
        elements.append(el)

    # ------------------------------------------------------------------
    # 3) EnergyDemand → PN_Load
    # ------------------------------------------------------------------
    for lid, ent in load_entities.items():

        uid = load_id_to_uid[lid]

        node_id = get_attr_value(ent,"isConnectedToNode","")
        busuid = bus_uid_from_node_id(node_id)

        is_demand_flexible = get_attr_value(ent,"is_demand_flexible",False)
        
        if is_demand_flexible == True:
            load_el = {
                "class": "PN_LoadFlexible",
                "uid": uid,
                "name": get_attr_value(ent,"name", lid),
                "busuid": busuid,
                "profile_factor": get_attr_value(ent,"annual_energy_demand", 0.0),
                "u_load_c1": get_attr_value(ent,"variable_operating_cost", 0.0),
                "w_c1": -get_attr_value(ent,"value_of_lost_load", 10000.0),
                "xi_ref_profile": get_attr_value(ent,"demand_profile_reference", ""),
                "T0": get_attr_value(ent,"flexibility_window_time_start", 0.0),
                "T1": get_attr_value(ent,"flexibility_window_time_end", 0.0),
                "TP": get_attr_value(ent,"flexibility_time_resolution", 0.0),
            }
        else:
            load_el = {
                "class": "PN_Load",
                "uid": uid,
                "name": get_attr_value(ent,"name", lid),
                "busuid": busuid,
                "w_c1": -get_attr_value(ent,"value_of_lost_load", 10000.0),
                "profile_factor": get_attr_value(ent,"annual_energy_demand", 0.0),
                "xi_ref_profile": get_attr_value(ent,"demand_profile_reference", ""),
            }

        load_el["country"] = map_busses[busuid]["country"]
        load_el["technology"] = get_attr_value(ent,"demand_type", "")
        elements.append(load_el)

    # ------------------------------------------------------------------
    # 4) EnergyStorageTechnology → PN_StoragePumpNoInfeed / PN_StorageDam
    # ------------------------------------------------------------------
    for sid, ent in storage_entities.items():

        node_id = get_attr_value(ent,"isConnectedToNode","")
        busuid = bus_uid_from_node_id(node_id)

        techtype_name = ent.data['instanceOf']
        techtype_entity = storagetype_entities[techtype_name]

        hasInputEnergyCarrier = get_attr_value(ent,"hasInputEnergyCarrier","")
        carrier_name = carrier_name_from_id(hasInputEnergyCarrier)
        cost = carrier_cost_from_id(hasInputEnergyCarrier)

        charging_efficiency = get_attr_value(techtype_entity,"charging_efficiency", None)
        discharging_efficiency = get_attr_value(techtype_entity,"discharging_efficiency", None)
        has_inflow = (get_attr_value(ent,"natural_inflow_profile_reference","") != "")

        du_gen_up_max = get_attr_value(ent,"maximum_ramp_rate_up", None)
        du_gen_down_max = get_attr_value(ent,"maximum_ramp_rate_up", None)
        du_gen_up_c1 = get_attr_value(ent,"ramping_cost_increase", None)
        du_gen_down_c1 = get_attr_value(ent,"ramping_cost_decrease", None)

        inflow = get_attr_value(ent,"annual_natural_inflow_volume", None)
        uid = storage_id_to_uid[sid]
        
        if inflow==None and charging_efficiency is not None:
            el = {
                "class": "PN_StoragePumpNoInfeed",
                "uid": uid,
                "name": get_attr_value(ent,"name", sid),
                "busuid": busuid,
                "eta_load": charging_efficiency,
                "eta_gen": discharging_efficiency,
                "u_gen_max": get_attr_value(ent,"nominal_power_capacity", 0.0),
                "u_load_max": get_attr_value(ent,"maximum_charging_power", 0.0),
                "u_gen_c1": get_attr_value(ent,"variable_operating_cost", 0.0),
                "u_load_c1": get_attr_value(ent,"charging_variable_operating_cost", 0.0),
                "Capacity": get_attr_value(ent,"energy_storage_capacity", 0.0),
                "xi_ref_profile": get_attr_value(ent,"natural_inflow_profile_reference","") or "",
                "profile_factor": get_attr_value(ent,"annual_natural_inflow_volume", 0.0),
                "has_inflow": has_inflow
            }

        if inflow and charging_efficiency is not None:
            el = {
                "class": "PN_StoragePump",
                "uid": uid,
                "name": get_attr_value(ent,"name", sid),
                "busuid": busuid,
                "eta_load": charging_efficiency,
                "eta_gen": discharging_efficiency,
                "u_gen_max": get_attr_value(ent,"nominal_power_capacity", 0.0),
                "u_load_max": get_attr_value(ent,"maximum_charging_power", 0.0),
                "u_gen_c1": get_attr_value(ent,"variable_operating_cost", 0.0),
                "u_load_c1": get_attr_value(ent,"charging_variable_operating_cost", 0.0),
                "Capacity": get_attr_value(ent,"energy_storage_capacity", 0.0),
                "xi_ref_profile": get_attr_value(ent,"natural_inflow_profile_reference","") or "",
                "profile_factor": get_attr_value(ent,"annual_natural_inflow_volume", 0.0),
                "has_inflow": has_inflow
            }

        elif inflow is not None:
            el = {
                "class": "PN_StorageDam",
                "uid": uid,
                "name": get_attr_value(ent,"name", sid),
                "busuid": busuid,
                "eta_load": charging_efficiency,
                "eta_gen": discharging_efficiency,
                "u_gen_max": get_attr_value(ent,"nominal_power_capacity", 0.0),
                "u_gen_c1": get_attr_value(ent,"variable_operating_cost", 0.0),
                "Capacity": get_attr_value(ent,"energy_storage_capacity", 0.0),
                "xi_ref_profile": get_attr_value(ent,"natural_inflow_profile_reference","") or "",
                "profile_factor": get_attr_value(ent,"annual_natural_inflow_volume", 0.0),
                "has_inflow": has_inflow
            }
        else:
            continue

        if carrier_name is not None:
            el["hasInputEnergyCarrier"] = carrier_name
        if cost is not None:
            el["xi_c1"] = cost

        if du_gen_up_max is not None:
            el["has_ramprate"] = True
            el["du_gen_up_max"] = du_gen_up_max
        if du_gen_up_c1 is not None:
            el["has_ramprate"] = True
            el["du_gen_up_c1"] = du_gen_up_c1
        if du_gen_down_max is not None:
            el["has_ramprate"] = True
            el["du_gen_down_max"] = du_gen_down_max
        if du_gen_down_c1 is not None:
            el["has_ramprate"] = True
            el["du_gen_down_c1"] = du_gen_down_c1

        el["country"] = map_busses[busuid]["country"]
        el["technology"] = techtype_name
        elements.append(el)

    # ------------------------------------------------------------------
    # 5) EnergyConversionTechnology1x1 → PN_GenDispatchable / PN_GenNonDispatchable
    # ------------------------------------------------------------------
    for gid, ent in conv1x1_entities.items():

        uid = gen_id_to_uid[gid]

        node_id = get_attr_value(ent,"isOutputNodeOf",uid)
        busuid = bus_uid_from_node_id(node_id)

        input_origin = get_attr_value(ent,"input_origin","exogenous")

        techtype_name = ent.data['instanceOf']
        techtype_entity = techtype_entities[techtype_name]

        hasInputEnergyCarrier = get_attr_value(techtype_entity,"hasInputEnergyCarrier","")
        carrier_name = carrier_name_from_id(hasInputEnergyCarrier)
        cost = carrier_cost_from_id(hasInputEnergyCarrier)
        co2 = carrier_co2_from_id(hasInputEnergyCarrier)

        nominal_power_capacity = get_attr_value(ent,"nominal_power_capacity", 0.0)
        # import pdb
        # pdb.set_trace()


        eff = get_attr_value(techtype_entity,"energy_conversion_efficiency", None)
        annual_available = get_attr_value(ent,"annual_resource_potential",None)
        has_profile = get_attr_value(ent,"resource_potential_profile_reference","")

        # heuristic: non-dispatchable if annual_available > 0
        is_has_annual_resource_potential = bool(annual_available is not None)

        is_nondisp = ("Wind" in techtype_name or "Solar" in techtype_name or "RunOfRiver" in techtype_name )

        if is_nondisp and is_has_annual_resource_potential==False:
            continue


        cls = "PN_GenDispatchable"
        if is_nondisp:
            cls = "PN_GenNonDispatchable"  

        du_gen_up_max = get_attr_value(ent,"maximum_ramp_rate_up", None)
        du_gen_down_max = get_attr_value(ent,"maximum_ramp_rate_up", None)
        du_gen_up_c1 = get_attr_value(ent,"ramping_cost_increase", None)
        du_gen_down_c1 = get_attr_value(ent,"ramping_cost_decrease", None)


        el = {
            "class": cls,
            "uid": uid,
            "name": get_attr_value(ent,"name", gid),
            "busuid": busuid,
            "eta_gen": eff,
            "u_gen_max": nominal_power_capacity,
            "u_gen_c1": get_attr_value(ent,"variable_operating_cost", 0.0),
        }

        if is_nondisp:
            el["profile_factor"] = annual_available or 0.0
            gen_profile = get_attr_value(ent,"resource_potential_profile_reference","")
            if gen_profile:
                el["xi_ref_profile"] = gen_profile

        if carrier_name is not None:
            el["carrier"] = carrier_name
        if cost is not None:
            el["xi_c1"] = cost
        if co2 is not None:
            el["has_co2"] = True
            el["MWh_to_tons_co2"] = co2
            for key, ent in energysystemmodel_entities.items():
                el["co2_c1"] = float(get_attr_value(ent,"co2_price", 0.0))

        if du_gen_up_max is not None:
            el["has_ramprate"] = True
            el["du_gen_up_max"] = du_gen_up_max
        if du_gen_up_c1 is not None:
            el["has_ramprate"] = True
            el["du_gen_up_c1"] = du_gen_up_c1
        if du_gen_down_max is not None:
            el["has_ramprate"] = True
            el["du_gen_down_max"] = du_gen_down_max
        if du_gen_down_c1 is not None:
            el["has_ramprate"] = True
            el["du_gen_down_c1"] = du_gen_down_c1

        el["country"] = map_busses[busuid]["country"]
        el["technology"] = techtype_name
        elements.append(el)

    # ------------------------------------------------------------------
    # 6) Write JSON
    # ------------------------------------------------------------------
    jpn = {"PowerSystemElements": elements}
    jpn["TIMEEND"] = 8760
    jpn["TIMESTART"] = 1
    jpn["ExportProblem"] = 0
    jpn["baseMVA"] = 1

    with output_path.open("w") as f:
        json.dump(jpn, f, indent=2, sort_keys=True)


from pathlib import Path
from typing import Optional
import numpy as np
from scipy.io import loadmat

import h5py
import numpy as np

# def save_timeseries_to_hdf5(filename, timestamps, data_dict):
#     series_names = list(data_dict.keys())
#     data_matrix = np.vstack([data_dict[k] for k in series_names]).T

#     with h5py.File(filename, "w") as f:
#         f.create_dataset("values", data=data_matrix)
#         # f.create_dataset("time", data=np.array(timestamps, dtype="S32"))
#         f.create_dataset("series_names", data=np.array(series_names, dtype="S64"))

def load_mat_variable(
    var_name: str,
    base_path: Path,
) -> (bool, np.ndarray):
    """
    EnergyDemand `var_name` from a .mat file and return it as a np.ndarray.

    Logic:
    1. If `mat_filename` is None:
         - look for <base_path>/<var_name>.mat
    2. If `mat_filename` is given:
         - if mat_filename is an absolute or contains a directory:
               use it directly if it exists
           else:
               - first try <base_path>/<mat_filename>
               - if not found and fallback_path is given: <fallback_path>/<mat_filename>

    Raises FileNotFoundError if no suitable .mat file is found.
    Raises KeyError if the variable is not found in the .mat file.
    """

    base_path = Path(base_path)
    candidate_files = []

    candidate_files.append(base_path / f"{var_name}.mat")

    mat_file_to_use = None
    for c in candidate_files:
        if c.is_file():
            mat_file_to_use = c
            break

    if mat_file_to_use is None:
        print(
            f"Could not find a .mat file for variable '{var_name}'. "
            f"Tried: {', '.join(str(c) for c in candidate_files)}"
        )
        return False, None

    data = loadmat(mat_file_to_use)
    ret_val = True
    if var_name not in data:
        # sometimes MATLAB stores variables with a different name (e.g. same as filename)
        # but per your description we require `var_name` to exist.
        print(
            f"Variable '{var_name}' not found in MAT file '{mat_file_to_use}'. "
        )
        ret_val = False
        # raise KeyError(
        #     f"Variable '{var_name}' not found in MAT file '{mat_file_to_use}'. "
        #     f"Available variables: {', '.join(k for k in data.keys() if not k.startswith('__'))}"
        # )
    if ret_val:
        return ret_val, np.asarray(data[var_name])
    return ret_val, None


def load_mat_file(
    var_name: str,
    mat_filename: Optional[str] = None,
    fallback_path: Optional[Path] = None,
    whole_data: Optional[dict] = None,
) -> (bool, np.ndarray, dict):
    """
    EnergyDemand `var_name` from a .mat file and return it as a np.ndarray.

    Logic:
    1. If `mat_filename` is None:
         - look for <base_path>/<var_name>.mat
    2. If `mat_filename` is given:
         - if mat_filename is an absolute or contains a directory:
               use it directly if it exists
           else:
               - first try <base_path>/<mat_filename>
               - if not found and fallback_path is given: <fallback_path>/<mat_filename>

    Raises FileNotFoundError if no suitable .mat file is found.
    Raises KeyError if the variable is not found in the .mat file.
    """


    candidate_files = []

    if fallback_path is not None:
        candidate_files.append(fallback_path / mat_filename)

    mat_file_to_use = None
    for c in candidate_files:
        if c.is_file():
            mat_file_to_use = c
            break

    if mat_file_to_use is None:
        print(
            f"Could not find a .mat file for variable '{var_name}'. "
            f"Tried: {', '.join(str(c) for c in candidate_files)}")
        return False, None, None

    if whole_data==None:
        data = loadmat(mat_file_to_use)
    else:
        data = whole_data 
    ret_val = True
    if var_name not in data:
        # sometimes MATLAB stores variables with a different name (e.g. same as filename)
        # but per your description we require `var_name` to exist.
        print(
            f"Variable '{var_name}' not found in MAT file '{mat_file_to_use}'. "
        )
        ret_val = False
        # raise KeyError(
        #     f"Variable '{var_name}' not found in MAT file '{mat_file_to_use}'. "
        #     f"Available variables: {', '.join(k for k in data.keys() if not k.startswith('__'))}"
        # )
    if ret_val:
        return ret_val, np.asarray(data[var_name]), data
    return ret_val, None, data

def add_profile(
    el: Entity,
    type: int,
    mat_data: dict
    ) -> (bool, np.ndarray, dict):
    
    profile_name = el.get("xi_ref_profile", "")
    if profile_name and profile_name!= "":
        if type==1:
            ret, arr = load_mat_variable(
                var_name=profile_name,
                base_path=Path("../data/profiles"),
            )
            return ret, np.transpose(arr), None
        elif type==2:
            ret, arr, mat_data = load_mat_file(
                var_name=profile_name,
                mat_filename="profiles.mat",
                fallback_path=Path("../data/profiles"),
                whole_data=mat_data)
            return ret, np.transpose(arr), mat_data
    return False, None, None



def import_from_flexeco(
    schema_dir: str | Path,
    european_json: str | Path,
) -> (dict, Model):
    """
    Build a CESDM Model instance from european_data.jpn using the
    schema_inherit YAMLs and cesdm_toolbox.

    Parameters
    ----------
    schema_dir : path to the 'schema_inherit' directory
    european_json : path to 'european_data.jpn'

    Returns
    -------
    cesdm_toolbox.Model with populated entities.
    """
    schema_dir = Path(schema_dir)
    european_json = Path(european_json)

    # 1) EnergyDemand schema into Model
    model = build_model_from_yaml(schema_dir)

    # ------------------------------------------------------------------
    # 2) Create base EnergyCarrier / EnergyDomain / GeographicalRegion entities
    # ------------------------------------------------------------------
    carrirers = ["electricity"]

    carrier_id = "c_electricity"
    isInEnergyDomain = "d_electricity"
    isInGeographicalRegion = "region_europe"

    # EnergyDomain
    model.add_entity(entity_class="EnergySystemModel", entity_id="EnergySystemModel")

    # EnergyDomain
    model.add_entity(entity_class="EnergyDomain", entity_id=isInEnergyDomain)
    model.add_attribute(entity_id=isInEnergyDomain, attribute_id="name", value=isInEnergyDomain[2:])
    # EnergyDomain.yaml has relation 'carrier'
    model.add_relation(entity_id=isInEnergyDomain, relation_id="hasEnergyCarrier", target_entity_id=carrier_id)

    # GeographicalRegion (single “Europe” region for now)

    # ------------------------------------------------------------------
    # 3) EnergyDemand raw European data
    # ------------------------------------------------------------------
    with european_json.open() as f:
        data = json.load(f)
    elements = data["PowerSystemElements"]

    map_technology_to_carrier = {}
    map_flexeco_carrier_to_carrier = {}
    data_profiles = {}
    mat_data = None

    map_flexeco_carrier_to_carrier["coal"] = "c_coal"
    map_flexeco_carrier_to_carrier["Gas"] = "c_gas"
    map_flexeco_carrier_to_carrier["lignite"] = "c_lignite"
    map_flexeco_carrier_to_carrier["nuclear"] = "c_nuclear"
    map_flexeco_carrier_to_carrier["oil"] = "c_oil"
    map_flexeco_carrier_to_carrier["PHS"] = "c_water"
    map_flexeco_carrier_to_carrier["hydro"] = "c_water"
    map_flexeco_carrier_to_carrier["load"] = "c_electricity"
    map_flexeco_carrier_to_carrier["ror"] = "c_water"
    map_flexeco_carrier_to_carrier["otherRES"] = "c_others_renewable"
    map_flexeco_carrier_to_carrier["battery"] = "c_electricity"
    map_flexeco_carrier_to_carrier["dsr"] = "c_electricity"
    map_flexeco_carrier_to_carrier["solar"] = "c_pv"
    map_flexeco_carrier_to_carrier["wind"] = "c_wind"

    for carrirer in carrirers:
        # EnergyCarrier
        carrier_id = ("c_%s" % carrirer)
        model.add_entity(entity_class="EnergyCarrier", entity_id=carrier_id)
        model.add_attribute(entity_id=carrier_id, attribute_id="name", value=carrier_id[2:])
        model.add_attribute(entity_id=carrier_id, attribute_id="energy_carrier_type", value="DOMAIN")
        model.add_attribute(entity_id=carrier_id, attribute_id="co2_emission_intensity", value=0.0)
        model.add_attribute(entity_id=carrier_id, attribute_id="energy_carrier_cost", value=0.0)

    for el in elements:
        if el.get("class") in ["PN_GenDispatchable","PN_GenNonDispatchable","PN_StorageDam","PN_StoragePump","PN_StoragePumpNoInfeed"] :
            uid = el["uid"]

            carrier_id = None

            if "carrier" in el and el["carrier"] in map_flexeco_carrier_to_carrier:
                carrier_id = map_flexeco_carrier_to_carrier[el["carrier"]]
                carrier_id = carrier_id.lower()

                if carrier_id not in model.entities["EnergyCarrier"]:
                    model.add_entity(entity_class="EnergyCarrier", entity_id=carrier_id)

                if carrier_id is not None:
                    model.add_attribute(entity_id=carrier_id, attribute_id="name", value=carrier_id[2:])
                    model.add_attribute(entity_id=carrier_id, attribute_id="energy_carrier_type", value="FUEL")
                    if "xi_c1" in el: 
                        model.add_attribute(entity_id=carrier_id, attribute_id="energy_carrier_cost", value=el["xi_c1"])
                    
                    if "MWh_to_tons_co2" in el: 
                        model.add_attribute(entity_id=carrier_id, attribute_id="co2_emission_intensity", value=el["MWh_to_tons_co2"])

                    if "has_co2" in el and el["has_co2"]==True:
                        model.add_attribute(entity_id="EnergySystemModel", attribute_id="co2_price", value=el["co2_c1"])

            elif "technology" in el:
                technology = el["technology"].lower()
                if "hard" in technology and "coal" in technology and "biofuel" not in technology:
                    carrier_id = ("c_hard_coal")
                    carrier_id = carrier_id.lower()
                elif "coal" in technology and "biofuel" not in technology:
                    carrier_id = ("c_coal")
                    carrier_id = carrier_id.lower()
                elif "lignite" in technology and "biofuel" not in technology:
                    carrier_id = ("c_lignite")
                    carrier_id = carrier_id.lower()
                elif "biofuel" in technology or "waste" in technology or "bioenergy" in technology:
                    carrier_id = ("c_biofuel")
                    carrier_id = carrier_id.lower()
                elif "heavy_oil" in technology and "biofuel" not in technology:
                    carrier_id = ("c_heavy_oil")
                    carrier_id = carrier_id.lower()
                elif "gas" in technology and "biofuel" not in technology:
                    carrier_id = ("c_gas")
                    carrier_id = carrier_id.lower()
                elif "oil" in technology:
                    carrier_id = ("c_oil")
                    carrier_id = carrier_id.lower()
                elif "pv" in technology:
                    carrier_id = ("c_pv")
                    carrier_id = carrier_id.lower()
                elif "wind" in technology:
                    carrier_id = ("c_wind")
                    carrier_id = carrier_id.lower()
                elif "nuclear" in technology:
                    carrier_id = ("c_nuclear")
                    carrier_id = carrier_id.lower()
                elif "oil_shale" in technology:
                    carrier_id = ("c_shale_oil")
                    carrier_id = carrier_id.lower()
                elif "light_oil" in technology:
                    carrier_id = ("c_light_oil")
                    carrier_id = carrier_id.lower()
                elif "reservoir" in technology:
                    carrier_id = ("c_water")
                    carrier_id = carrier_id.lower()
                elif "run_of_river" in technology:
                    carrier_id = ("c_water")
                    carrier_id = carrier_id.lower()
                elif "pump_storage" in technology:
                    carrier_id = ("c_water")
                    carrier_id = carrier_id.lower()
                elif "hydro" in technology:
                    carrier_id = ("c_water")
                    carrier_id = carrier_id.lower()
                elif "pondage" in technology:
                    carrier_id = ("c_water")
                    carrier_id = carrier_id.lower()
                elif "solar_photovoltaic" in technology or "solar" in technology:
                    carrier_id = ("c_pv")
                    carrier_id = carrier_id.lower()
                elif "solar_thermal" in technology:
                    carrier_id = ("c_pv")
                    carrier_id = carrier_id.lower()
                elif "others_renewable" in technology or "other_res" in technology:
                    carrier_id = ("c_others_renewable")
                    carrier_id = carrier_id.lower()
                elif "others_non_renewable" in technology or "other_non_res" in technology:
                    carrier_id = ("c_others_non_renewable")
                    carrier_id = carrier_id.lower()
                elif "battery_storage" in technology:
                    carrier_id = ("c_electricity")
                    carrier_id = carrier_id.lower()
                elif "hydrogen" in technology:
                    carrier_id = ("c_hydrogen")
                    carrier_id = carrier_id.lower()
                elif "demand_side_response" in technology:
                    carrier_id = ("c_electricity")
                    carrier_id = carrier_id.lower()
                elif "adequacy" in technology:
                    carrier_id = ("c_electricity")
                    carrier_id = carrier_id.lower()
                elif "axpo_hc_new" in technology:
                    carrier_id = ("c_others_renewable")
                    carrier_id = carrier_id.lower()
                elif "fossil" in technology:
                    carrier_id = ("c_gas")
                    carrier_id = carrier_id.lower()
                elif "geothermal" in technology:
                    carrier_id = ("c_geothermal")
                    carrier_id = carrier_id.lower()
                elif "other" == technology:
                    carrier_id = ("c_others_non_renewable")
                    carrier_id = carrier_id.lower()
                elif "marine" == technology or "tidal" == technology:
                    carrier_id = ("c_water")
                    carrier_id = carrier_id.lower()
                elif "lithium-ion" == technology or "battery" == technology:
                    carrier_id = ("c_electricity")
                    carrier_id = carrier_id.lower()

                if carrier_id not in model.entities["EnergyCarrier"]:
                    model.add_entity(entity_class="EnergyCarrier", entity_id=carrier_id)

                if carrier_id is not None:
                    map_technology_to_carrier[technology] = carrier_id

                    model.add_attribute(entity_id=carrier_id, attribute_id="name", value=carrier_id[2:])
                    model.add_attribute(entity_id=carrier_id, attribute_id="energy_carrier_type", value="FUEL")
                    if "xi_c1" in el: 
                        model.add_attribute(entity_id=carrier_id, attribute_id="energy_carrier_cost", value=el["xi_c1"])
                    
                    if "MWh_to_tons_co2" in el: 
                        model.add_attribute(entity_id=carrier_id, attribute_id="co2_emission_intensity", value=el["MWh_to_tons_co2"])

                    if "has_co2" in el and el["has_co2"]==True:
                        model.add_attribute(entity_id="EnergySystemModel", attribute_id="co2_price", value=el["co2_c1"])

                # else:
                #     model.entities["EnergyCarrier"][carrier]["energy_carrier_cost"] = 0



    # ------------------------------------------------------------------
    # 4a) First pass: Buses → Regions
    # ------------------------------------------------------------------
    for el in elements:
        if el.get("class") == "PN_Busbar":
            uid = el["uid"]
            isInGeographicalRegion = "region_europe"
            subregion_id = None
            if "zone_name" in el:
                isInGeographicalRegion = el["zone_name"]
            elif "country" in el:
                isInGeographicalRegion = el["country"]

            
            if "nuts2_id" in el:
                subregion_id = el["nuts2_id"]


            # EnergyNode (base class) references inherited by ElectricityNode
            if isInGeographicalRegion not in model.entities["GeographicalRegion"]:
                model.add_entity(entity_class="GeographicalRegion", entity_id=isInGeographicalRegion)
                model.add_attribute(entity_id=isInGeographicalRegion, attribute_id="name", value=isInGeographicalRegion)

            if subregion_id is not None and subregion_id not in model.entities["GeographicalRegion"]:
                model.add_entity(entity_class="GeographicalRegion", entity_id=subregion_id)
                model.add_attribute(entity_id=subregion_id, attribute_id="name", value=subregion_id)
                model.add_relation(entity_id=subregion_id, relation_id="parent_id", target_entity_id=isInGeographicalRegion)

    # ------------------------------------------------------------------
    # 4b) Second pass: Buses → ElectricityNode
    # ------------------------------------------------------------------
    for el in elements:
        if el.get("class") == "PN_Busbar":
            uid = el["uid"]
            nid = f"node_{uid}"

            isInGeographicalRegion = "region_europe"
            subregion_id = None
            if "zone_name" in el:
                isInGeographicalRegion = el["zone_name"]
            elif "country" in el:
                isInGeographicalRegion = el["country"]

            
            if "nuts2_id" in el:
                subregion_id = el["nuts2_id"]

            model.add_entity(entity_class="ElectricityNode", entity_id=nid)
            model.add_attribute(entity_id=nid, attribute_id="name", value=el.get("name"))
            model.add_attribute(entity_id=nid, attribute_id="nominal_voltage", value=el.get("Un"))

            # EnergyNode (base class) references inherited by ElectricityNode
            model.add_relation(entity_id=nid, relation_id="isInEnergyDomain", target_entity_id=isInEnergyDomain)
            if isInGeographicalRegion is not None:
                model.add_relation(entity_id=nid, relation_id="isInGeographicalRegion", target_entity_id=isInGeographicalRegion)
            elif subregion_id is not None:
                model.add_relation(entity_id=nid, relation_id="isInGeographicalRegion", target_entity_id=subregion_id)

    # Helper for mapping bus uids to node ids
    def node_id(bus_uid: int | str) -> str:
        return f"node_{bus_uid}"

    # ------------------------------------------------------------------
    # 5) Second pass: Lines / TR2 / HVDC → NetTransferCapacity, Loads → EnergyDemand
    # ------------------------------------------------------------------
    for el in elements:
        cls = el.get("class")

        # ------ Lines / transformers / HVDC → NetTransferCapacity ------
        if cls in ("PN_Line", "PN_TR2", "PN_HVDC", "PN_NTC"):
            uid = el["uid"]

            if cls == "PN_Line":
                eid = f"line_{uid}"
                series_resistance = el.get("r",0.0)
                series_reactance = el.get("x",0.0)
                shunt_susceptance = el.get("b",0.0)
                line_length = el.get("Length",1.0)
                thermal_capacity_rating = el.get("Smax",0.0)

                model.add_entity(entity_class="TransmissionLine", entity_id=eid)
                model.add_attribute(entity_id=eid, attribute_id="name", value=el.get("name"))

                model.add_attribute(entity_id=eid, attribute_id="series_resistance", value=series_resistance)
                model.add_attribute(entity_id=eid, attribute_id="series_reactance", value=series_reactance)
                model.add_attribute(entity_id=eid, attribute_id="shunt_susceptance", value=shunt_susceptance)
                model.add_attribute(entity_id=eid, attribute_id="line_length", value=line_length)
                model.add_attribute(entity_id=eid, attribute_id="thermal_capacity_rating", value=thermal_capacity_rating)

                # TwoPort references
                model.add_relation(entity_id=eid, relation_id="isFromNodeOf", target_entity_id=node_id(el["bus1_uid"]))
                model.add_relation(entity_id=eid, relation_id="isToNodeOf",   target_entity_id=node_id(el["bus2_uid"]))
                model.add_relation(entity_id=eid, relation_id="isInEnergyDomain",    target_entity_id=isInEnergyDomain)
            elif cls == "PN_TR2":
                eid = f"tr2_{uid}"
                model.add_entity(entity_class="TwoWindingPowerTransformer", entity_id=eid)
                model.add_attribute(entity_id=eid, attribute_id="name", value=el.get("name"))

                model.add_attribute(entity_id=eid, attribute_id="rated_apparent_power", value=el.get("SR"))
                model.add_attribute(entity_id=eid, attribute_id="rated_primary_voltage", value=el.get("UR1"))
                model.add_attribute(entity_id=eid, attribute_id="rated_secondary_voltage", value=el.get("UR2"))
                model.add_attribute(entity_id=eid, attribute_id="short_circuit_voltage", value=el.get("Usc"))

                # TwoPort references
                model.add_relation(entity_id=eid, relation_id="isFromNodeOf", target_entity_id=node_id(el["bus1_uid"]))
                model.add_relation(entity_id=eid, relation_id="isToNodeOf",   target_entity_id=node_id(el["bus2_uid"]))
                model.add_relation(entity_id=eid, relation_id="isInEnergyDomain",    target_entity_id=isInEnergyDomain)

            elif cls == "PN_HVDC":  # PN_HVDC
                eid = f"hvdc_{uid}"
                maximum_power_flow_1_to_2 = el.get("Smax")
                maximum_power_flow_2_to_1 = el.get("Smax")
            elif cls == "PN_NTC":  # PN_HVDC
                eid = f"ntc_{uid}"
                cap = el.get("Pmax")
                maximum_power_flow_1_to_2 = el.get("P1max")
                maximum_power_flow_2_to_1 = el.get("P2max")
                model.add_entity(entity_class="NetTransferCapacity", entity_id=eid)
                model.add_attribute(entity_id=eid, attribute_id="name", value=el.get("name"))

                # capacity → symmetric flow limits
                if maximum_power_flow_1_to_2 is not None:
                    model.add_attribute(entity_id=eid, attribute_id="maximum_power_flow_1_to_2", value=maximum_power_flow_1_to_2)
                    model.add_attribute(entity_id=eid, attribute_id="maximum_power_flow_2_to_1", value=maximum_power_flow_2_to_1)

                # TwoPort references
                model.add_relation(entity_id=eid, relation_id="isFromNodeOf", target_entity_id=node_id(el["bus1_uid"]))
                model.add_relation(entity_id=eid, relation_id="isToNodeOf",   target_entity_id=node_id(el["bus2_uid"]))
                model.add_relation(entity_id=eid, relation_id="isInEnergyDomain",    target_entity_id=isInEnergyDomain)
            else:
                assert(False)


        # ------ Loads → EnergyDemand ------
        elif cls == "PN_Load":
            uid = el["uid"]
            lid = f"load_{uid}"

            model.add_entity(entity_class="EnergyDemand", entity_id=lid)
            model.add_attribute(entity_id=lid, attribute_id="name", value=el.get("name"))
            model.add_attribute(entity_id=lid, attribute_id="annual_energy_demand", value=el.get("profile_factor", 0.0))
            ts_key = el.get("xi_ref_profile", "")
            ds_main = f"EnergyDemand/{lid}/profile"
            model.add_attribute(entity_id=lid, attribute_id="demand_profile_reference", value=el.get("xi_ref_profile", ""))
            model.add_attribute(entity_id=lid, attribute_id="value_of_lost_load", value=-el.get("w_c1", -10000.0))
            model.add_attribute(entity_id=lid, attribute_id="variable_operating_cost", value=el.get("u_load_c1", 0.0))


            # OnePort relation
            model.add_relation(entity_id=lid, relation_id="isConnectedToNode", target_entity_id=node_id(el["busuid"]))

            ret, arr, mat_data = add_profile(el,1,mat_data)
            if ret==True:
                data_profiles[ds_main] = arr
                if ts_key:
                    data_profiles[f"profiles/{ts_key}"] = arr

        # ------ Loads → EnergyDemand ------
        elif cls == "PN_LoadFlexible":
            uid = el["uid"]
            lid = f"load_{uid}"

            model.add_entity(entity_class="EnergyDemand", entity_id=lid)
            model.add_attribute(entity_id=lid, attribute_id="name", value=el.get("name"))
            model.add_attribute(entity_id=lid, attribute_id="annual_energy_demand", value=el.get("profile_factor", 0.0))
            ts_key = el.get("xi_ref_profile", "")
            ds_main = f"EnergyDemand/{lid}/profile"
            model.add_attribute(entity_id=lid, attribute_id="demand_profile_reference", value=el.get("xi_ref_profile", ""))
            model.add_attribute(entity_id=lid, attribute_id="value_of_lost_load", value=-el.get("w_c1", -10000.0))
            model.add_attribute(entity_id=lid, attribute_id="variable_operating_cost", value=el.get("u_load_c1", 0.0))
            model.add_attribute(entity_id=lid, attribute_id="is_demand_flexible", value=True)
            model.add_attribute(entity_id=lid, attribute_id="flexibility_window_time_start", value=el.get("T0", 0.0))
            model.add_attribute(entity_id=lid, attribute_id="flexibility_window_time_end", value=el.get("T1", 0.0))
            model.add_attribute(entity_id=lid, attribute_id="flexibility_time_resolution", value=el.get("TP", 0.0))

            # OnePort relation
            model.add_relation(entity_id=lid, relation_id="isConnectedToNode", target_entity_id=node_id(el["busuid"]))

            ret, arr, mat_data = add_profile(el,1,mat_data)
            if ret==True:
                data_profiles[ds_main] = arr
                if ts_key:
                    data_profiles[f"profiles/{ts_key}"] = arr


        # --------------------------------------------------------------
        # EnergyStorageTechnology (pumped hydro) → EnergyStorageTechnology
        # PN_StoragePumpNoInfeed: pumped storage with no natural inflow
        # --------------------------------------------------------------
        elif cls in ["PN_StoragePumpNoInfeed","PN_StoragePump"]:
            uid = el["uid"]
            sid = f"storage_pump_{uid}"

            model.add_entity(entity_class="EnergyStorageTechnology", entity_id=sid)
            model.add_attribute(entity_id=sid, attribute_id="name", value=el.get("name"))
            model.add_attribute(entity_id=sid, attribute_id="storage_technology_type", value="pumped hydro")

            # efficiencies
            model.add_attribute(entity_id=sid, attribute_id="charging_efficiency", value=el.get("eta_load", 1.0))
            model.add_attribute(entity_id=sid, attribute_id="discharging_efficiency", value=el.get("eta_gen",  1.0))

            # power and energy capacity
            model.add_attribute(entity_id=sid, attribute_id="nominal_power_capacity", value=el.get("u_gen_max", 0.0))
            model.add_attribute(entity_id=sid, attribute_id="maximum_charging_power", value=el.get("u_load_max", 0.0))

            model.add_attribute(entity_id=sid, attribute_id="variable_operating_cost", value=el.get("u_gen_c1", 0.0))
            model.add_attribute(entity_id=sid, attribute_id="charging_variable_operating_cost", value=el.get("u_load_c1", 0.0))

            model.add_attribute(entity_id=sid, attribute_id="energy_storage_capacity", value=el.get("Capacity", 0.0))

            # no natural inflow
            if "has_inflow" in el and el["has_inflow"]==True:
                ts_key = el.get("xi_ref_profile", "")
                ds_main = f"EnergyStorageTechnology/{sid}/inflow"
                model.add_attribute(entity_id=sid, attribute_id="natural_inflow_profile_reference", value=el["xi_ref_profile"])
                model.add_attribute(entity_id=sid, attribute_id="annual_natural_inflow_volume", value=el["profile_factor"])

                ret, arr, mat_data = add_profile(el,1,mat_data)
                if ret==True:
                    data_profiles[ds_main] = arr
                    if ts_key:
                        data_profiles[f"profiles/{ts_key}"] = arr

            input_energy_carrier_id = None
            if "carrier" in el and el["carrier"] in map_flexeco_carrier_to_carrier:
                input_energy_carrier_id = map_flexeco_carrier_to_carrier[el["carrier"]]
            elif "technology" in el and el["technology"].lower() in map_technology_to_carrier:
                input_energy_carrier_id = map_technology_to_carrier[el["technology"].lower()]
                
            if el.get("du_gen_up_max", None)!=None:
                model.add_attribute(entity_id=sid, attribute_id="maximum_ramp_rate_up", value=el.get("du_gen_up_max", None))
                model.add_attribute(entity_id=sid, attribute_id="maximum_ramp_rate_down", value=el.get("du_gen_down_max", None))
                model.add_attribute(entity_id=sid, attribute_id="ramping_cost_increase", value=el.get("du_gen_up_c1", None))
                model.add_attribute(entity_id=sid, attribute_id="ramping_cost_decrease", value=el.get("du_gen_down_c1", None))

            # references
            model.add_relation(entity_id=sid, relation_id="isConnectedToNode",       target_entity_id=node_id(el["busuid"]))
            model.add_relation(entity_id=sid, relation_id="hasInputEnergyCarrier",  target_entity_id=input_energy_carrier_id)
            model.add_relation(entity_id=sid, relation_id="hasOutputEnergyCarrier", target_entity_id="c_electricity")

        # --------------------------------------------------------------
        # EnergyStorageTechnology (reservoir) → EnergyStorageTechnology
        # PN_StorageDam: reservoir hydro with natural inflow
        # --------------------------------------------------------------
        elif cls == "PN_StorageDam":
            uid = el["uid"]
            sid = f"storage_dam_{uid}"

            model.add_entity(entity_class="EnergyStorageTechnology", entity_id=sid)
            model.add_attribute(entity_id=sid, attribute_id="name", value=el.get("name"))
            model.add_attribute(entity_id=sid, attribute_id="storage_technology_type", value="reservoir hydro")

            # efficiencies
            model.add_attribute(entity_id=sid, attribute_id="charging_efficiency", value=el.get("eta_load", 1.0))
            model.add_attribute(entity_id=sid, attribute_id="discharging_efficiency", value=el.get("eta_gen",  1.0))

            # power and energy capacity
            model.add_attribute(entity_id=sid, attribute_id="nominal_power_capacity", value=el.get("u_gen_max", 0.0))
            model.add_attribute(entity_id=sid, attribute_id="energy_storage_capacity", value=el.get("Capacity", 0.0))

            # natural inflow: use annual_energy_mwh as annual inflow
            ts_key = el.get("xi_ref_profile", "")
            ds_main = f"EnergyStorageTechnology/{sid}/inflow"
            model.add_attribute(entity_id=sid, attribute_id="natural_inflow_profile_reference", value=el.get("xi_ref_profile", ""))
            model.add_attribute(entity_id=sid, attribute_id="annual_natural_inflow_volume", value=el.get("profile_factor", 0.0))

            ret, arr, mat_data = add_profile(el,1,mat_data)
            if ret==True:
                data_profiles[ds_main] = arr
                if ts_key:
                    data_profiles[f"profiles/{ts_key}"] = arr

            input_energy_carrier_id = None
            if "carrier" in el and el["carrier"] in map_flexeco_carrier_to_carrier:
                input_energy_carrier_id = map_flexeco_carrier_to_carrier[el["carrier"]]
            elif "technology" in el and el["technology"].lower() in map_technology_to_carrier:
                input_energy_carrier_id = map_technology_to_carrier[el["technology"].lower()]
                
            if el.get("du_gen_up_max", None)!=None:
                model.add_attribute(entity_id=sid, attribute_id="maximum_ramp_rate_up", value=el.get("du_gen_up_max", None))
                model.add_attribute(entity_id=sid, attribute_id="maximum_ramp_rate_down", value=el.get("du_gen_down_max", None))
                model.add_attribute(entity_id=sid, attribute_id="ramping_cost_increase", value=el.get("du_gen_up_c1", None))
                model.add_attribute(entity_id=sid, attribute_id="ramping_cost_decrease", value=el.get("du_gen_down_c1", None))

            # references
            model.add_relation(entity_id=sid, relation_id="isConnectedToNode",       target_entity_id=node_id(el["busuid"]))
            model.add_relation(entity_id=sid, relation_id="hasInputEnergyCarrier",  target_entity_id=input_energy_carrier_id)
            model.add_relation(entity_id=sid, relation_id="hasOutputEnergyCarrier", target_entity_id="c_electricity")

        # --------------------------------------------------------------
        # Generators → EnergyConversionTechnology1x1
        # - PN_GenDispatchable
        # - PN_GenNonDispatchable
        # --------------------------------------------------------------
        elif cls in ("PN_GenDispatchable", "PN_GenNonDispatchable"):
            uid = el["uid"]
            gid = f"gen_{uid}"

            model.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id=gid)
            model.add_attribute(entity_id=gid, attribute_id="name", value=el.get("name"))

            # basic attributes
            model.add_attribute(entity_id=gid, attribute_id="energy_conversion_efficiency", value=el.get("eta_gen", 1.0))
            model.add_attribute(entity_id=gid, attribute_id="nominal_power_capacity", value=el.get("u_gen_max", 0.0))
            model.add_attribute(entity_id=gid, attribute_id="variable_operating_cost", value=el.get("u_gen_c1", 0.0))
            if el.get("du_gen_up_max", None)!=None:
                model.add_attribute(entity_id=gid, attribute_id="maximum_ramp_rate_up", value=el.get("du_gen_up_max", None))
                model.add_attribute(entity_id=gid, attribute_id="maximum_ramp_rate_down", value=el.get("du_gen_down_max", None))
                model.add_attribute(entity_id=gid, attribute_id="ramping_cost_increase", value=el.get("du_gen_up_c1", None))
                model.add_attribute(entity_id=gid, attribute_id="ramping_cost_decrease", value=el.get("du_gen_down_c1", None))


            # time-series related fields (optional)
            model.add_attribute(entity_id=gid, attribute_id="resource_potential_profile_reference", value=None)

            # Non-dispatchable: we have an annual energy -> map to annual_resource_potential
            if cls == "PN_GenNonDispatchable":
                model.add_attribute(entity_id=gid, attribute_id="annual_resource_potential", value=el.get("profile_factor", 0.0))
                ts_key = el.get("xi_ref_profile", "")
                ds_main = f"EnergyConversionTechnology1x1/{gid}/availability"
                model.add_attribute(entity_id=gid, attribute_id="resource_potential_profile_reference", value=el.get("xi_ref_profile", ""))
                ret, arr, mat_data = add_profile(el,1,mat_data)
                if ret==True:
                    data_profiles[ds_main] = arr
                    if ts_key:
                        data_profiles[f"profiles/{ts_key}"] = arr
            else:
                # dispatchable plants: leave as None (no explicit resource limit here)
                model.add_attribute(entity_id=gid, attribute_id="annual_resource_potential", value=0.0)

            # references
            input_energy_carrier_id = None
            if "carrier" in el and el["carrier"] in map_flexeco_carrier_to_carrier:
                input_energy_carrier_id = map_flexeco_carrier_to_carrier[el["carrier"]]
            elif "technology" in el and el["technology"].lower() in map_technology_to_carrier:
                input_energy_carrier_id = map_technology_to_carrier[el["technology"].lower()]
                

            # references
            model.add_attribute(entity_id=gid, attribute_id="input_origin", value="exogenous")
            model.add_relation(entity_id=gid, relation_id="isOutputNodeOf",       target_entity_id=node_id(el["busuid"]))
            model.add_relation(entity_id=gid, relation_id="hasInputEnergyCarrier",  target_entity_id=input_energy_carrier_id)
            model.add_relation(entity_id=gid, relation_id="hasOutputEnergyCarrier", target_entity_id="c_electricity")

            # Optional: you could also create GenerationType entities and link
            # via 'generation_type_id' based on parsing el["name"].
    return data_profiles, model


if __name__ == "__main__":
    # Adjust these paths to your local layout
    schema_dir = Path("schema_inherit")      # folder containing the YAMLs
    # european_json = Path("european_data.jpn")
    european_json = Path("RRE_EU_with_profiles.jpn")


    data_timeseries,m = import_from_flexeco(schema_dir, european_json)

    # Optional: run toolbox validation (may warn about references
    # expecting base class EnergyNode vs concrete ElectricityNode, depending on toolbox version)
    errors = m.validate()
    print(f"Validation errors: {len(errors)}")
    for e in errors: print(" -", e)

    # Optional: export to JSON/YAML using cesdm_toolbox’s exporter
    m.export_json("european_system.json")
    print("Exported nested JSON + YAML to european_system.json / .yaml")
    
    save_timeseries_to_hdf5("european_system.h5",None,data_timeseries)

    # Optional: export to JSON/YAML using cesdm_toolbox’s exporter
    m2 = build_model_from_yaml("schema_inherit")  # or an empty Model()
    m2.import_json("european_system.json")

    errors = m.validate()
    print(f"Validation errors: {len(errors)}")
    for e in errors: print(" -", e)

    export_to_flexeco(m2, "european_system_flexeco.jpn")

    # Export one CSV per class
    m2.export_csv_by_class_wide("outputs/by_class_wide")

    # # Optional: export to JSON/YAML using cesdm_toolbox’s exporter
    # m3 = build_model_from_yaml("schema_inherit")  # or an empty Model()
    # m3.import_csv_by_class_wide("outputs/by_class_wide")

    # errors = m3.validate()
    # print(f"Validation errors: {len(errors)}")
    # for e in errors: print(" -", e)

    export_to_flexeco(m2, "european_system_flexeco.jpn")
    
