# PyPSA network import

CESDM can import complete [PyPSA](https://pypsa.org/) network models
directly from NetCDF files, via `examples/example_import_pypsa.py`
(a thin CLI wrapper around `tools/import_pypsa.py`).

## External reference data

The example needs a PyPSA network file distributed separately from
this repository — see
[the TYNDP import doc](tyndp.md#external-reference-data) for the same
archive (it includes both datasets):

```text
sweet-cosi-cesdm/
│
├── external_data/
│   └── pypsa/
│       └── elec.nc
└── ...
```

Run the example:

```bash
python ./examples/example_import_pypsa.py \
    --nc-path ./external_data/PYPSA/elec.nc \
    --schema-dir schemas \
    --nuts-shapefile external_data/PYPSA/NUTS_RG_20M_2021_4326.shp \
    --output-dir ./output/pypsa_nodal_model/nodal/
```

## Workflow

```text
PyPSA Network
(NetCDF)
        │
        ▼
PyPSA Importer
        │
        ▼
CESDM Model
        │
        ├── Schema validation
        ├── Model statistics
        ├── YAML export
        ├── Frictionless export
        ├── MATPOWER export
        └── pandapower export
```

The importer creates the corresponding CESDM entities and
representation views, including:

- Electrical buses
- Transmission lines
- Transformers
- Loads
- Generators
- Storage units
- Shunt compensators
- Carrier domains
- Topology views
- Dispatch views
- Power-flow views

## Unified representation

Both the TYNDP and PyPSA importers map their very different source
formats to the *same* CESDM representation — once imported, validation,
exploration, statistics, and export are completely independent of the
original data source:

```text
       TYNDP 2024                 PyPSA
            │                       │
            └──────────┬────────────┘
                       │
                       ▼
             Common Energy System
               Domain Model
                   (CESDM)
                       │
┌──────────────────────┼──────────────────────┐
▼                      ▼                      ▼
Validation         Exploration            Statistics
```
