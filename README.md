# CESDM Toolbox

[![Docs](https://img.shields.io/badge/docs-latest-blue.svg)](https://demirayt.github.io/sweet-cosi-cesdm/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

The **Common Energy System Domain Model (CESDM) Toolbox** provides a **schema-driven modelling framework**
to describe energy systems in terms of **entities, attributes, and relations**.

⚠️ **Important notice**  
This repository currently provides a **demonstration and methodology prototype** of CESDM.
It is **not a finalized standard**. See the disclaimer below.

---

## Project Context

The development of this CESDM prototype is carried out **within the framework of the SWEET‑CoSi project**  
(**SWEET – Co‑evolution of the Swiss Energy System and Society**).

- Project website: https://sweet-cosi.ch  
- Funding framework: SWEET (Swiss Energy Research for the Energy Transition)

Within SWEET‑CoSi, CESDM is being developed as part of **Task 1.9**, which focuses on:
- conceptual and methodological foundations for **common energy system representations**
- shared domain models to support **interoperability across tools and research tasks**

The CESDM toolbox presented here serves as a **methodology demonstrator** for this task.

---

## What CESDM Is

CESDM is designed to:

- Provide a **generic, domain-driven structure** for energy system models
- Enable **explicit, machine-readable semantics** via schemas
- Support **model interoperability** across tools and use cases
- Separate **domain knowledge (schemas)** from **model instances (systems)**

At its core, CESDM is built around:

- **Schema-driven modelling** (YAML schemas defining entities, attributes, relations)
- **Entity–Attribute–Relation (EAR)** patterns
- **Inheritance** between schema types
- **Strong validation** (types, constraints, required fields, relations)
- **Explicit construction APIs** (`add_entity`, `add_attribute`, `add_relation`)
- **Import / export** (YAML, JSON, CSV, Frictionless Data Package)

---

## Demonstration Status (Read This First)

This version of CESDM is provided **for demonstration purposes only**.

- The schemas are **provisional**
- Naming, structure, and constraints **may change**
- The toolbox API is **not guaranteed to be stable**
- This version is meant to help users:
  - understand the **methodology**
  - explore **schema-driven energy modelling**
  - get a **hands-on feel** for CESDM capabilities

A future version of CESDM will be explicitly grounded in a **formal Common Energy System Domain Ontology**.

➡️ See **`docs/00_disclaimer.md`** for details.

---

## Documentation

The full documentation is hosted on GitHub Pages:

➡️ **https://github.com/demirayt/sweet-cosi-cesdm/**

The documentation explains:

- The **schema-driven modelling concept**
- Core CESDM entities (nodes, carriers, technologies, storage, networks)
- How to **build models programmatically and declaratively**
- Fully worked **energy system examples**
- Validation rules and common pitfalls

The docs are built with:
- [Sphinx](https://www.sphinx-doc.org/)
- [MyST Markdown](https://myst-parser.readthedocs.io/)

---

## Installation & Quick Start

```bash
git clone https://github.com/demirayt/sweet-cosi-cesdm.git
cd sweet-cosi-cesdm
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run an example:

```bash
cd examples
python example_ch_and_neighbours.py
```

Other examples include:

- `example_simple.py` – minimal system using all core entity types
- `example_multienergy.py` – electricity, gas, and heat coupling


---

## Advanced Examples

To run more advanced examples, some additional input files are required:

<https://ethz.ch/content/dam/ethz/special-interest/mavt/ctr-energy-networks-fen-dam/data/CESDM_example_data.zip>

The downloaded zip file needs to be extracted in the main cesdm folder


These examples include:

- `example_import_export_tydnp.py` – TYNDP2022 dataset interfaced with FEN's in-house energy system analysis tool FLEXECO 
- `example_import_pypsa_nc.py` – detailed pypsa electicity model (elec.nc) derived from <https://zenodo.org/records/7646728>

To run an example_import_export_tydnp.py:

```bash
cd examples
python example_import_export_tydnp.py
```

To run an example_import_pypsa_nc.py:

```bash
cd examples
python example_import_pypsa_nc.py --nc_path ../data/elec.nc --schema-dir ../schemas/ --output-dir ../output/pypsa/ --timeseries-hdf5 ../output/pypsa/elec_timeseries.h5
```

## Building the HTML Documentation Locally

CESDM documentation is built using **Sphinx** with **MyST Markdown** support.
You can generate a local HTML version of the documentation and browse it in your web browser.

---

### Prerequisites

Make sure you have installed the documentation dependencies:

```bash
pip install -r docs/requirements.txt
```

(If `docs/requirements.txt` does not exist, install Sphinx and MyST manually.)

---

### Build the HTML documentation

From the repository root, run:

```bash
cd docs
make html
```

This command will:

- Parse all Markdown and reStructuredText files in `./docs/`
- Resolve cross-references and table of contents
- Build a static HTML documentation site

---

### View the documentation

After the build finishes, open the generated HTML index file in your browser:

```text
./docs/_build/html/index.html
```

You can open this file directly, for example:

```bash
xdg-open docs/_build/html/index.html   # Linux
open docs/_build/html/index.html       # macOS
```

or by double-clicking it in your file explorer.

---

### Notes

- Re-run `make html` whenever documentation files are updated
- If you encounter build errors, run:

```bash
make clean
make html
```

to rebuild from scratch
- The generated `_build/` directory can be safely deleted at any time

--


## Who This Is For

This CESDM version is intended for:

- Researchers exploring **energy system semantics**
- Developers interested in **interoperable modelling frameworks**
- Users who want to understand **schema-driven system modelling**
- Contributors interested in shaping a future CESDM ontology

---

## Summary

**CESDM today**:
- A methodological prototype
- A learning and experimentation platform
- A concrete demonstration of schema-driven energy modelling

**CESDM tomorrow**:
- Ontology-based
- Semantically rigorous
- Interoperable by design

Feedback and experimentation are strongly encouraged.
