# CESDM – Common Energy System Domain Model

[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue.svg)](https://cesdm.github.io/cesdm-toolbox/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**CESDM** is a schema-driven toolbox for creating, exploring, validating, transforming, and exchanging interoperable energy-system models — a common semantic representation that's independent of any specific optimisation, simulation, or planning tool.

> **Project status**
> CESDM is currently a research prototype and methodology demonstrator. The schemas and Python API are evolving and may change as the model matures.

## Installation

```bash
git clone https://github.com/cesdm/cesdm-toolbox.git
cd cesdm-toolbox
python3 -m venv .sweet-cosi-cesdm
source .sweet-cosi-cesdm/bin/activate   # Windows: .sweet-cosi-cesdm\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install -e .
```

Verify it:

```python
from cesdm_toolbox import build_model_from_yaml
model = build_model_from_yaml("schemas")
print(model.summary())
```

Install only what you need beyond the core (default install already covers building, validating, exploring, and exchanging models):

| Feature | Command |
|---|---|
| PyPSA importer | `pip install -e ".[pypsa]"` |
| pandapower import/export | `pip install -e ".[pandapower]"` |
| MATPOWER import/export | `pip install -e ".[matpower]"` |
| Excel support | `pip install -e ".[excel]"` |
| Parquet support | `pip install -e ".[parquet]"` |
| Development tools | `pip install -e ".[dev]"` |
| Everything | `pip install -e ".[all]"` |


## Documentation website

The documentation is built from the Markdown files in [`docs/`](docs/) with MkDocs Material and published automatically through GitHub Actions.

To preview it locally:

```bash
pip install -e ".[docs]"
mkdocs serve
```

Then open `http://127.0.0.1:8000/` in your browser. Every push to `main` triggers the workflow in [`.github/workflows/docs.yml`](.github/workflows/docs.yml). In the GitHub repository, select **Settings → Pages → Source: GitHub Actions** once to activate publishing.

## What is CESDM?

Energy-system studies often use different tools — each with its own
data model, terminology, and conventions — to describe the same
physical system. CESDM addresses that by building on a simple,
general-purpose idea and applying it specifically to energy systems.

### Entity–Attribute–Relation (EAR): describe any system with three building blocks

**Almost any structured system — not just an energy system — can be
described with three building blocks.**

- An **entity** is a thing that exists — a power plant, a household, a
  book, a person, ...
- An **attribute** is a value on an entity — `nominal_power_capacity`,
  `occupant_count`, `page_count`, ...
- A **relation** links two entities — `atNode`, `locatedIn`,
  `authoredBy`, ...

`ear_toolbox` implements exactly this, and nothing more — it has no
built-in notion of "generator" or "bus" at all. See
[`examples/example_ear_generic_domain.py`](examples/README_EAR_GENERIC_DOMAIN_EXAMPLE.md)
for the same three primitives describing households and energy
communities instead, with zero energy-specific code anywhere.

### CESDM: EAR applied to energy systems

**CESDM is what you get from applying that idea to energy systems.**
`cesdm_toolbox` builds on `ear_toolbox` and adds the energy-specific
parts: a schema defining which entity classes exist (`GenerationUnit`,
`ElectricalBus`, `DemandUnit`, `TransmissionLine`, ...) and their
attributes/relations (`nominal_voltage`, `atNode`, `hasTechnology`,
...); helper builder functions for the energy domain (`add_bus`,
`add_generator`, `create_demand_unit`, ...); and **representation
views**, which separate an asset's *identity* from how it's
*modelled* — the same `GenerationUnit` can carry a topology view
(where it's connected), a dispatch view (its capacity and operational
limits), and a power-flow view side by side, instead of cramming every
tool's fields onto one object. CESDM is the shared way to describe a
system once, independent of any specific tool — it's not a solver and
doesn't prescribe an optimisation formulation, it's the common layer
between data, models, and tools. Importers/exporters translate to and
from PyPSA, TYNDP, MATPOWER, pandapower, and several file formats.

All of this — which entity classes exist, which attributes and
relations they can have, what's required — is defined in YAML schema
files under `schemas/`, not hard-coded into Python. `model.validate()`
checks any model against them.

### The object-oriented proxy API: the same system, more conveniently

**The proxy API describes the same system, just more conveniently.**
Everything above can be built with the low-level
`add_entity`/`add_attribute`/`add_relation` calls EAR provides
directly — but everyday code should reach for the proxy API instead:
`model.add_generator(...)` returns a live object
(`gen.dispatch.nominal_power_capacity = 400`, `gen.connect(bus)`) so
you're not writing out entity/attribute/relation calls by hand. It's a
convenience layer, not a different model — every style here builds
the identical underlying data. See
[`docs/getting_started.md`](docs/getting_started.md) for the exact
same model built all three ways.

![CESDM layered architecture: your code sits on the optional proxy API, which builds on the CESDM domain layer (representation views, composite builders, import/export adapters, analysis validation), which builds on the generic EAR engine and is driven by the YAML schema.](docs/illustrations/cesdm_architecture.svg)

## A first example, two ways

The same small system — two buses, a gas and a wind generator, a
demand, a transmission line — built two different ways. Both produce
byte-for-byte the same underlying model; the difference is only how
much CESDM does for you along the way.

### The easy way: CESDM builder functions + the object-oriented proxy API

This is what everyday code should look like. `add_bus`, `add_generator`,
`create_demand_unit`, ... are CESDM's own builder functions — each one
creates an entity *and* wires up the views/relations that go with it in
one call. The objects they return (`gas`, `wind`, `demand`, ...) are
live handles back into the model: `gas.dispatch.x = y` sets an
attribute on the right view, `gas.connect(bus)` wires a topology
relation, and a typo is caught immediately instead of silently doing
nothing.

```python
from pathlib import Path
from cesdm_toolbox import build_model_from_yaml

model = build_model_from_yaml("schemas")
model.import_library("library/default_library")

model.add_entity("EnergySystemModel", "ch_example")

bus_1 = model.add_bus("bus.ch.1", nominal_voltage=380)
bus_2 = model.add_bus("bus.ch.2", nominal_voltage=380)

gas = model.add_generator(
    id="gas.ch.1",
    technology="Generation.Thermal.Gas.CCGT.Present2",
    bus=bus_1,
)
gas.name = "Gas turbine CH-1"
gas.dispatch.nominal_power_capacity = 400
gas.connect(bus_1)

wind = model.add_generator(
    id="wind.ch.1",
    technology="Generation.Renewable.Wind.Onshore",
    bus=bus_1,
)
wind.dispatch.nominal_power_capacity = 120

demand = model.create_demand_unit("demand.ch.1", bus_id=bus_2)
demand.dispatch.maximum_energy_demand = 250

model.create_transmission_line("line.ch.1", bus_1, bus_2)

# energy_conversion_efficiency was never set explicitly -- it resolves
# automatically from the CCGT technology template (library/default_library).
print("gas efficiency (from technology template):", gas.dispatch.energy_conversion_efficiency)
# -> 0.58

model.validate_or_raise()
print(model.summary())
# GenerationUnit            2
# DemandUnit                1
# TransmissionElement       1

output_dir = Path("output/readme_quickstart")
output_dir.mkdir(parents=True, exist_ok=True)
model.export_yaml_model(output_dir / "quickstart.yaml")
```

### The same model, with just the core EAR API

Underneath every builder call above is CESDM's generic
Entity–Attribute–Relation (EAR) engine — the same three primitives,
`add_entity`, `add_attribute`, `add_relation`, for *any* schema-defined
class. This is what `add_generator(...)` and `gas.dispatch.x = y`
actually do on your behalf. Seeing it written out once is the fastest
way to understand what a builder call really means — and it's the
right tool when you need something a builder doesn't cover yet.

```python
from pathlib import Path
from cesdm_toolbox import build_model_from_yaml

model = build_model_from_yaml("schemas")
model.import_library("library/default_library")

model.add_entity("EnergySystemModel", "ch_example")

# Buses
model.add_entity("ElectricalBus", "bus.ch.1")
model.add_attribute("bus.ch.1", "nominal_voltage", 380, unit="kV")
model.add_entity("ElectricalBus", "bus.ch.2")
model.add_attribute("bus.ch.2", "nominal_voltage", 380, unit="kV")

# Gas generator: entity, technology + carrier relations, topology, dispatch
model.add_entity("GenerationUnit", "gas.ch.1")
model.add_attribute("gas.ch.1", "name", "Gas turbine CH-1")
model.add_relation("gas.ch.1", "hasTechnology", "Generation.Thermal.Gas.CCGT.Present2")
model.add_relation("gas.ch.1", "hasInputCarrier", "carrier.fuel.fossil.gas.natural_gas")
model.add_relation("gas.ch.1", "hasOutputCarrier", "carrier.electricity")

model.add_entity("SinglePort.TopologyView", "single_port_topology_view.gas.ch.1")
model.add_relation("single_port_topology_view.gas.ch.1", "representsAsset", "gas.ch.1")
model.add_relation("single_port_topology_view.gas.ch.1", "atNode", "bus.ch.1")

model.add_entity("Generation.DispatchView", "generation_dispatch_view.gas.ch.1")
model.add_relation("generation_dispatch_view.gas.ch.1", "representsAsset", "gas.ch.1")
model.add_attribute("generation_dispatch_view.gas.ch.1", "nominal_power_capacity", 400, unit="MW")
# energy_conversion_efficiency is still not set here -- the technology-
# default cascade only depends on hasTechnology, set above.

# Wind generator: same pattern, different technology/resource/capacity
model.add_entity("GenerationUnit", "wind.ch.1")
model.add_relation("wind.ch.1", "hasTechnology", "Generation.Renewable.Wind.Onshore")
model.add_relation("wind.ch.1", "hasInputResource", "resource.renewable.wind")
model.add_relation("wind.ch.1", "hasOutputCarrier", "carrier.electricity")

model.add_entity("SinglePort.TopologyView", "single_port_topology_view.wind.ch.1")
model.add_relation("single_port_topology_view.wind.ch.1", "representsAsset", "wind.ch.1")
model.add_relation("single_port_topology_view.wind.ch.1", "atNode", "bus.ch.1")

model.add_entity("Generation.DispatchView", "generation_dispatch_view.wind.ch.1")
model.add_relation("generation_dispatch_view.wind.ch.1", "representsAsset", "wind.ch.1")
model.add_attribute("generation_dispatch_view.wind.ch.1", "nominal_power_capacity", 120, unit="MW")

# Demand: entity, topology, dispatch
model.add_entity("DemandUnit", "demand.ch.1")

model.add_entity("SinglePort.TopologyView", "single_port_topology_view.demand.ch.1")
model.add_relation("single_port_topology_view.demand.ch.1", "representsAsset", "demand.ch.1")
model.add_relation("single_port_topology_view.demand.ch.1", "atNode", "bus.ch.2")

model.add_entity("Demand.DispatchView", "demand_dispatch_view.demand.ch.1")
model.add_relation("demand_dispatch_view.demand.ch.1", "representsAsset", "demand.ch.1")
model.add_attribute("demand_dispatch_view.demand.ch.1", "maximum_energy_demand", 250, unit="MW")

# Transmission line: entity, two-port topology
model.add_entity("TransmissionLine", "line.ch.1")

model.add_entity("TwoPort.TopologyView", "two_port_topology_view.line.ch.1")
model.add_relation("two_port_topology_view.line.ch.1", "representsAsset", "line.ch.1")
model.add_relation("two_port_topology_view.line.ch.1", "fromNode", "bus.ch.1")
model.add_relation("two_port_topology_view.line.ch.1", "toNode", "bus.ch.2")

print("gas efficiency (from technology template):", model.get_effective_attribute_value(
    "generation_dispatch_view.gas.ch.1", "energy_conversion_efficiency"))
# -> 0.58, same as above -- it's the same underlying model

model.validate_or_raise()
print(model.summary())
# GenerationUnit            2
# DemandUnit                1
# TransmissionElement       1
```

Neither version is "more correct" — a builder function is just a
shortcut for a fixed sequence of `add_entity`/`add_attribute`/
`add_relation` calls, wired up once so you don't have to know the
exact view-class names and id conventions every time. Reach for the
object-oriented API for everyday model-building, and drop to the EAR
primitives directly for anything a builder doesn't cover, or when
writing an importer that needs full control over exactly what gets
created.

### Keeping generated code in sync with the schema

Builder methods (`add_bus`, `add_generation_unit`, ...) and editor
type stubs are concrete generated Python, not computed on the fly —
regenerate both after any schema change:

```bash
cesdm-update-generated
```

## Exploring, validating, importing, exporting

Continuing with the `model` from above:

```python
print(model.summary())                       # one-line overview of what's in the model
model.validate_or_raise()                     # validate against the schema
model.get_dispatch_view("gas.ch.1")            # look up a specific representation view
model.total_capacity()                        # simple built-in statistics
```

Models are stored by class in `model.entities`, each entity holding a
`.data` dict of attributes/relations — see
[`examples/example_explore_cesdm_model.py`](examples/example_explore_cesdm_model.py)
for a deeper, generic exploration example.

`model.validate()` checks structural completeness against the schema —
it doesn't know whether the model has what a *specific analysis*
needs. `model.validate_for_analysis("optimal_dispatch")` checks that
too, against requirements declared in a YAML profile
(`analysis_profiles/*.yaml`) rather than hard-coded in Python — see
[`docs/architecture/analysis_validation.md`](docs/architecture/analysis_validation.md).

**Importers:**

| Source | Entry point |
|---|---|
| PyPSA | `examples/example_import_pypsa.py` — see [`docs/importers/pypsa.md`](docs/importers/pypsa.md) |
| TYNDP 2024 | `examples/example_import_tyndp_proxy_api.py` — see [`docs/importers/tyndp.md`](docs/importers/tyndp.md) |
| pandapower | `tools/import_pandapower.py` — see [`docs/importers/pandapower.md`](docs/importers/pandapower.md) |
| MATPOWER | `tools/import_matpower.py` — see [`docs/importers/matpower.md`](docs/importers/matpower.md) |

**Export formats**, all `CesdmModel` methods:

| Format | Method |
|---|---|
| Hierarchical / flat YAML | `export_yaml_hierarchical(...)`, `export_yaml(...)` |
| CSV | `export_csv_by_class(...)`, `export_long_csv(...)` |
| Excel / HDF5 / Parquet | `export_excel(...)`, `export_hdf5(...)`, `export_parquet(...)` |
| Frictionless Data Package | `export_frictionless(...)` |
| MATPOWER / pandapower | [`docs/exporters/matpower.md`](docs/exporters/matpower.md), [`docs/exporters/pandapower.md`](docs/exporters/pandapower.md) |
| JSON Schema / RDF-OWL | `export_json_schema(...)`, `export_rdf_schema(...)` |

## Editor typings

`.pyi` stubs under `typings/` give IDE autocomplete and type-checking
for `gen.dispatch.nominal_power_capacity`, `model.add_generator(...)`'s
return type, and every other public method — regenerated by
`cesdm-update-generated` after any schema change.

All of it runs on [Pyright](https://microsoft.github.io/pyright/) —
VS Code's Pylance extension and Sublime's LSP-pyright package are both
built directly on it — configured once, for every editor, in
`pyproject.toml`'s `[tool.pyright]` section (`stubPath = "typings"`).

**VS Code** — install the **Pylance** extension (bundled with the
official Python extension) and open the repository root as the
workspace folder. Nothing else to configure; `stubPath` is picked up
automatically.

**Sublime Text** — install the **LSP** and **LSP-pyright** packages
via Package Control, then open the repository root as your project
folder. LSP-pyright runs the same Pyright engine as Pylance and reads
the same `[tool.pyright]` config the same way.

**PyCharm** — its built-in inspector doesn't read `pyproject.toml`'s
`[tool.pyright]` section, so `stubPath` alone isn't enough. Right-click
`typings/` in the Project pane → **Mark Directory as → Sources Root**.
This is the mechanism JetBrains itself documents for custom stub
directories — PyCharm then prioritizes each `.pyi` stub over the
matching runtime `.py` module.

See [`docs/architecture/proxy_api.md`](docs/architecture/proxy_api.md)
for what the stubs describe.

## Examples

Every example is written on the object-oriented proxy API; see [`docs/getting_started.md`](docs/getting_started.md) for the same style of model built with lower-level EAR calls instead. Each example has a companion walkthrough doc explaining the code step by step — linked below.

| Example | Why it matters | Walkthrough |
|---|---|---|
| `examples/example_in_readme.py` | The complete lifecycle in one place — build, validate, export, reload, explore, get statistics — the shape every real project follows | [`README_IN_README_EXAMPLE.md`](examples/README_IN_README_EXAMPLE.md) |
| `examples/example_simple.py` | One example touching every core entity/view type — the fastest way to see how much of the schema fits together | [`README_SIMPLE_EXAMPLE.md`](examples/README_SIMPLE_EXAMPLE.md) |
| `examples/example_multienergy.py` | Real systems aren't electricity-only — shows electricity+heat+gas coupled through conversion units, the pattern for any sector-coupling study | [`README_MULTIENERGY_EXAMPLE.md`](examples/README_MULTIENERGY_EXAMPLE.md) |
| `examples/example_hydro_reservoir_plant.py` | Hydro storage is a composite of two linked assets (reservoir + turbine), not one entity — the pattern for any multi-asset physical system | [`README_HYDRO_RESERVOIR_EXAMPLE.md`](examples/README_HYDRO_RESERVOIR_EXAMPLE.md) |
| `examples/example_kundur_two_area.py` | The only example reaching into dynamic/stability modelling (machine, AVR, governor, PSS) — needed the moment a study goes beyond steady-state dispatch | [`README_KUNDUR_TWO_AREA_EXAMPLE.md`](examples/README_KUNDUR_TWO_AREA_EXAMPLE.md) |
| `examples/tutorial_ch_neighbours.py` | The longest, most narrated example — builds one system three ways (proxy API, CESDM builders, raw EAR) so the relationship between all three layers is visible side by side | [`README_CH_NEIGHBOURS_TUTORIAL.md`](examples/README_CH_NEIGHBOURS_TUTORIAL.md) |
| `examples/example_explore_cesdm_model.py` | Building a model is half the story — this is the other half: querying capacity, generation mix, and demand out of a model you didn't build yourself | [`README_EXPLORE_MODEL_EXAMPLE.md`](examples/README_EXPLORE_MODEL_EXAMPLE.md) |
| `examples/example_import_pypsa.py` | The on-ramp from an existing PyPSA study into CESDM — see [`docs/importers/pypsa.md`](docs/importers/pypsa.md) | [`README_PYPSA_IMPORT_LOGIC.md`](examples/README_PYPSA_IMPORT_LOGIC.md) |
| `examples/example_import_tyndp_proxy_api.py` | The on-ramp from the official ENTSO-E TYNDP 2024 dataset into CESDM — see [`docs/importers/tyndp.md`](docs/importers/tyndp.md) | [`README_TYNDP_IMPORT_LOGIC.md`](examples/README_TYNDP_IMPORT_LOGIC.md) |
| `examples/example_cesdm_to_pandapower_and_matpower.py` | Proves CESDM isn't a dead end — the same model verifiably round-trips to two established power-flow tools with a converged AC load flow | [`README_POWERFLOW_EXPORT_EXAMPLE.md`](examples/README_POWERFLOW_EXPORT_EXAMPLE.md) |
| `examples/example_agent_based_prosumer_model.py` | Shows CESDM extended with a second schema tree (households, energy communities, agent decisions) layered on the same physical system, without touching the core schema | [`README_AGENT_BASED_EXAMPLE.md`](examples/README_AGENT_BASED_EXAMPLE.md) |
| `examples/example_analysis_validation.py` | `model.validate()` passing doesn't mean a model is ready for *your* study — shows the separate, analysis-specific check and what a constraint violation actually looks like | [`README_ANALYSIS_VALIDATION_EXAMPLE.md`](examples/README_ANALYSIS_VALIDATION_EXAMPLE.md) |
| `examples/example_ear_generic_domain.py` | Proof that the EAR engine is genuinely domain-agnostic — the exact same primitives used for every energy-system example above, applied to households and energy communities instead | [`README_EAR_GENERIC_DOMAIN_EXAMPLE.md`](examples/README_EAR_GENERIC_DOMAIN_EXAMPLE.md) |
| `examples/example_schema_extension.py` | Shows how to add a genuinely new asset type without touching the core schema or writing any Python — the extension mechanism every custom deployment eventually needs | [`README_SCHEMA_EXTENSION_EXAMPLE.md`](examples/README_SCHEMA_EXTENSION_EXAMPLE.md) |

## Documentation

- [`docs/getting_started.md`](docs/getting_started.md) — the CESDM convenience API layer, and more on how the three layers relate
- [`docs/architecture/proxy_api.md`](docs/architecture/proxy_api.md) — the object-oriented `AssetProxy`/`ViewProxy` API
- [`docs/architecture/analysis_validation.md`](docs/architecture/analysis_validation.md) — checking fitness for a specific analysis, not just schema completeness
- [`docs/architecture/package_layout.md`](docs/architecture/package_layout.md) — how `ear`/`cesdm` are organized
- [`docs/architecture/schema_governance.md`](docs/architecture/schema_governance.md) — schema versioning & stability tiers
- [`docs/schema_layout.md`](docs/schema_layout.md) — how the schema tree under `schemas/` is organized
- [`docs/importers/`](docs/importers/) and [`docs/exporters/`](docs/exporters/) — per-format import/export notes
- [`docs/guide/01_what_is_cesdm.md`](docs/guide/01_what_is_cesdm.md) — plain-language introduction, no code
- [`docs/guide/`](docs/guide/) — the full written guide: core concepts, schemas, asset hierarchy, representation views, energy domain, time series, spatial aggregation, and both API layers

## Repository structure

```text
.
├── ear/                           # Generic Entity–Attribute–Relation engine (package)
├── cesdm/                         # CESDM domain layer: model class, import/export (package)
├── ear_toolbox.py                 # Backward-compatible shim -> re-exports `ear`
├── cesdm_toolbox.py               # Backward-compatible shim -> re-exports `cesdm`
├── schemas/                       # Main CESDM schema files (+ SCHEMA_MANIFEST.yaml)
├── schemas_agentbased/            # Agent-based schema extension (+ SCHEMA_MANIFEST.yaml)
├── library/                       # Default library data
├── tools/                         # Importer/exporter/codegen utilities
├── examples/                      # Runnable examples
├── typings/                       # Generated editor type stubs (see "Editor typings" above)
├── docs/                          # All documentation (guides, architecture notes, import/export notes)
└── CHANGELOG.md                   # Project changelog
```

New code should import from `ear` / `cesdm` directly rather than the
top-level shim modules — see
[`docs/architecture/package_layout.md`](docs/architecture/package_layout.md).

## Project status and roadmap

Current: schema-driven construction, validation, high-level builders,
YAML/CSV/Excel/HDF5/Parquet/JSON-Schema/Frictionless export, PyPSA and
TYNDP import, model exploration examples.

Planned: stronger scenario/assumption-set management, additional
importers (Calliope, oemof, TIMES, ...), formal ontology alignment,
RDF/OWL representations, automated documentation-example tests.

## Project context

CESDM is developed in the context of the **SWEET-CoSi** project as a
common semantic framework for interoperable energy-system modelling —
a methodology demonstrator and implementation platform for
experimenting with schema-driven energy-system representations.

## Contributing

Contributions, issue reports, examples, schema extensions, and
documentation improvements are welcome — new importers, schema
extensions, validation tests, and scenario-management workflows are
all good starting points.

## License

See `LICENSE` for licensing information.
