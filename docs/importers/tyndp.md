# ENTSO-E TYNDP 2024 import

The TYNDP importer builds a complete CESDM representation from the
official **ENTSO-E Ten-Year Network Development Plan (TYNDP) 2024**
reference datasets.

Two versions exist:

- `examples/example_import_tyndp_proxy_api.py` — the recommended one,
  built on the object-oriented proxy API. Ships with small synthetic
  fixtures (`examples/sample_data/tyndp_sample_*.csv`), so it runs
  standalone without the external dataset below. See the
  [Examples table](https://github.com/cesdm/cesdm-toolbox#examples) for both its minimal
  single-CSV mode and its full-pipeline mode.
- `examples/example_import_tyndp.py` — the original, pre-proxy-API
  version. Kept (unlike the other pre-proxy-API examples) because the
  proxy-API version above actually imports its technology
  classification functions and constants directly, to stay faithful to
  the original's real-world business rules rather than re-deriving
  them — see the proxy-API version's own docstring for exactly which
  functions. Requires the external reference dataset below to run its
  own full pipeline.

## External reference data

Running the full pipeline against the real TYNDP dataset (rather than
the small synthetic fixtures) needs a dataset distributed separately
from this repository:

```bash
python download_external_data.py
```

This downloads and extracts

> https://ethz.ch/content/dam/ethz/special-interest/mavt/ctr-energy-networks-fen-dam/data/cesdm_external_data.zip

into the repository root for you. If it fails with a TLS certificate
error (`CERTIFICATE_VERIFY_FAILED`) — common on corporate/institutional
networks that intercept HTTPS traffic for security scanning, or after
installing Python from python.org on macOS without running its
certificate-install step — the script prints a detailed explanation of
both cases and how to fix them, plus a `--insecure` flag to skip
verification for this one download if you've checked both and still
trust the network you're on.

To do it manually instead, download that URL and extract the archive
into the repository root. The directory structure
should then look like:

```text
sweet-cosi-cesdm/
│
├── examples/
├── tools/
├── schemas/
├── external_data/
│   └── tyndp2024/
│       ├── buses.csv
│       ├── lines.csv
│       ├── generators.csv
│       ├── loads.csv
│       └── ...
└── ...
```

Run the original pre-proxy-API example against it:

```bash
python examples/example_import_tyndp.py
```

## Workflow

```text
ENTSO-E TYNDP 2024
CSV reference data
        │
        ▼
TYNDP Importer
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

The imported CESDM model typically contains:

- Geographical regions
- Electrical buses
- Transmission lines
- Transformers
- Shunt compensators
- Generation units
- Demand units
- Energy carriers
- Carrier domains
- Topology representation views
- Dispatch representation views
- Power-flow representation views
