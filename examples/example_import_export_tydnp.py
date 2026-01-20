import os
import sys
from pathlib import Path

# Add the project root (one level up from docs/) to the Python path
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../tools/"))

from cesdm_toolbox import build_model_from_yaml, Model, Entity
from pathlib import Path
import json
import numpy as np
import pandas as pd 
from typing import Optional
from scipy.io import loadmat

from import_flexeco import export_to_flexeco, import_from_flexeco, save_timeseries_to_hdf5

if __name__ == "__main__":
	# Adjust these paths to your local layout
	schema_dir = Path("../schemas/")      # folder containing the YAMLs

	m = build_model_from_yaml("../schemas/")  # or an empty Model()
	data_timeseries,m = import_from_flexeco(schema_dir,"../data/tyndp_2024.jpn")

	errors = m.validate()
	if errors:
	    print("Model has validation issues:")
	    for e in errors:
	        print("  -", e)
	else:
	    print("Model validated successfully.")

	# export in cesdm format (yaml,json)
	# import pdb
	# pdb.set_trace()
	m.export_json("../output/tyndp/cesdm/tyndp_data_cesdm.json")
	m.export_yaml("../output/tyndp/cesdm/tyndp_data_cesdm.yaml")
	save_timeseries_to_hdf5("../output/tyndp/cesdm/tyndp_data_cesdm.h5",None,data_timeseries)
	# export data tables per entity
	# will be frictionless as well
	m.export_csv_by_class_wide("../output/tyndp/cesdm/tablewide/")
	m.export_long_csv("../output/tyndp/cesdm/tablelong/tyndp_data_long.csv")
	export_to_flexeco(m, Path("../output/tyndp/flexeco/tyndp_to_flexeco_export.jpn"))
