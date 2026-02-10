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


def load_timeseries_from_hdf5(filename):
    import numpy as np
    import h5py

    with h5py.File(filename, "r") as f:
        data_matrix = f["values"][:]              # shape: (T, N)
        series_names = [s.decode("utf-8") for s in f["series_names"][:]]

        # Optional time dataset (if you later enable it)
        if "time" in f:
            timestamps = [t.decode("utf-8") for t in f["time"][:]]
        else:
            timestamps = None

    # Rebuild data_dict: {series_name: 1D array}
    data_dict = {
        series_names[i]: data_matrix[:, i]
        for i in range(len(series_names))
    }

    return timestamps, data_dict

import pandas as pd

def import_cesdm_model_from_tyndp_installed_capacities(
    schema_path: str | os.PathLike,
    output_folder: str | os.PathLike = "../output/TYNDP2024/",
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

    model.import_yaml(scenario_output_folder + "/cesdm/yaml/" + yaml_file_name + ".yaml")
    errors = model.validate()
    if errors:
        print("Model has validation issues:")
        for e in errors:
            print("  -", e)
    else:
        print("Model validated successfully.")

    timestamps, profiles = load_timeseries_from_hdf5(scenario_output_folder + "/cesdm/yaml/profile_data.h5")

    export_to_flexeco(model, Path(scenario_output_folder + "/flexeco/" + yaml_file_name + ".jpn"))
    save_timeseries_to_hdf5(filename=str(scenario_output_folder + "/flexeco/profiles/profiles.h5"), timestamps=None, data_dict=profiles)

# -------------------
# Example usage (paths as provided in your environment)
# -------------------
if __name__ == "__main__":
    for sc in ["NT"]:
        for sy in [2030,2040]:
            for wy in [2009]:
                import_cesdm_model_from_tyndp_installed_capacities(
                    schema_path="schemas",
                    output_folder ="../output/TYNDP2024/",
                    policy=sc,   # optional
                    year=sy,     # optional
                    climate_year=wy,  # optional
                    drop_zero=True,
                )
                
    for sc in ["DE","GA"]:
        for sy in [2030,2040,2050]:
            for wy in [2009]:
                import_cesdm_model_from_tyndp_installed_capacities(
                    schema_path="schemas",
                    output_folder ="../output/TYNDP2024/",
                    policy=sc,   # optional
                    year=sy,     # optional
                    climate_year=wy,  # optional
                    drop_zero=True,
                )

