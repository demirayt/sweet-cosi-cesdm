"""example_import_pypsa_nc.py

Import a PyPSA NetCDF network into CESDM
========================================

What this example demonstrates
------------------------------
- How to convert a PyPSA network saved as NetCDF (``*.nc``) into a CESDM model
- How to validate the model against the CESDM YAML schemas
- How to export the resulting CESDM model to YAML and per-class CSV tables
- Optionally: how to extract time series from the PyPSA network and store them in HDF5

Prerequisites
-------------
- Optional dependency: ``pypsa`` (and its NetCDF stack)
- The repository's converter utilities in ``./tools/import_pypsa_nc.py``

Run
---
    python examples/example_import_pypsa_nc.py path/to/network.nc \
        --timeseries-hdf5 output/pypsa_import/timeseries.h5

Notes
-----
This script is a *thin wrapper* around the converter functions in ``tools/import_pypsa_nc.py``.
If you want to customise the mapping (e.g., bus-to-region rules, technology naming, carrier mapping),
start by editing those converter functions.
"""

from __future__ import annotations

from pathlib import Path
import sys


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


sys.path.insert(0, str(_repo_root()))
sys.path.insert(0, str(_repo_root() / "tools"))


def _optional_imports():
    """Import optional dependencies with a helpful error message."""
    try:
        import pypsa  # type: ignore
    except Exception as e:  # pragma: no cover
        raise SystemExit(
            "This example requires the optional dependency 'pypsa'.\n"
            "Install it (and any NetCDF dependencies) first, e.g.:\n\n"
            "    pip install pypsa\n\n"
            f"Original error: {e}"
        )

    try:
        from import_pypsa_nc import (
            build_cesdm_from_pypsa_nc,
            collect_timeseries_from_pypsa,
            save_timeseries_to_hdf5,
        )
    except Exception as e:  # pragma: no cover
        raise SystemExit(
            "Could not import the PyPSA->CESDM converter utilities.\n"
            "Make sure the repository's ./tools folder is present and on PYTHONPATH.\n\n"
            f"Original error: {e}"
        )

    return pypsa, build_cesdm_from_pypsa_nc, collect_timeseries_from_pypsa, save_timeseries_to_hdf5


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Convert a PyPSA NetCDF network (*.nc) to a CESDM model (YAML/CSV) and optionally export time series to HDF5."
        )
    )
    parser.add_argument(
        "--nc_path",
        nargs="?",
        default=str(_repo_root() / "data" / "elec.nc"),
        help="Path to the PyPSA NetCDF file (*.nc).",
    )
    parser.add_argument(
        "--schema-dir",
        default=str(_repo_root() / "schemas"),
        help="Path to the CESDM schema directory.",
    )
    parser.add_argument(
        "--default-region-name",
        default="DefaultRegion",
        help="Geographical region name used when the PyPSA network does not provide country/region info.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(_repo_root() / "output" / "pypsa_import"),
        help="Directory to write CESDM outputs.",
    )
    parser.add_argument(
        "--timeseries-hdf5",
        default=None,
        help="If set, write extracted time series to this HDF5 file.",
    )

    args = parser.parse_args()

    nc_path = Path(args.nc_path)
    schema_dir = Path(args.schema_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not nc_path.exists():
        raise SystemExit(f"NetCDF file not found: {nc_path}")
    if not schema_dir.exists():
        raise SystemExit(f"Schema directory not found: {schema_dir}")

    pypsa, build_cesdm_from_pypsa_nc, collect_timeseries_from_pypsa, save_timeseries_to_hdf5 = _optional_imports()

    # ------------------------------------------------------------------
    # 1) Convert PyPSA network -> CESDM model
    # ------------------------------------------------------------------
    model = build_cesdm_from_pypsa_nc(
        nc_path=str(nc_path),
        schema_dir=str(schema_dir),
        region_name=args.default_region_name,
    )
    model.resolve_inheritance()

    errors = model.validate()
    if errors:
        print("Model has validation issues:")
        for e in errors:
            print("  -", e)
        raise SystemExit(1)
    print("Model validated successfully.")

    # ------------------------------------------------------------------
    # 2) Export
    # ------------------------------------------------------------------
    yaml_path = out_dir / "pypsa_network.yaml"
    model.export_yaml(str(yaml_path))
    model.export_csv_by_class_wide(str(out_dir / "csv_wide"))
    print(f"Wrote CESDM YAML to: {yaml_path}")

    # ------------------------------------------------------------------
    # 3) Optional time series export
    # ------------------------------------------------------------------
    if args.timeseries_hdf5:
        h5_path = Path(args.timeseries_hdf5)
        h5_path.parent.mkdir(parents=True, exist_ok=True)

        net = pypsa.Network(str(nc_path))
        timestamps, ts_data = collect_timeseries_from_pypsa(net)
        save_timeseries_to_hdf5(str(h5_path), timestamps, ts_data)
        print(f"Exported {len(ts_data)} time series with {len(timestamps)} timesteps to: {h5_path}")


if __name__ == "__main__":
    main()
