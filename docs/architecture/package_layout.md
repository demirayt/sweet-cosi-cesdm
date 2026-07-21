# Package layout

`ear_toolbox.py` (generic EAR engine) and `cesdm_toolbox.py` (energy-system
domain layer) were originally single files of ~3,700 and ~5,400 lines.
They have been split into two packages, `ear/` and `cesdm/`, organized
by responsibility. **Behavior is unchanged** — this was a pure
module-boundary refactor, verified by running the full example suite
and test suite before and after and diffing output (see "Verification"
below).

## Why

A 5,400-line single file is hard for anyone outside the original
authors to safely contribute to or review — you can't tell from a diff
whether a change to, say, the Excel exporter risks touching the CSV
importer, because they're in the same file. Splitting by concern makes
the blast radius of a change visible from the file path alone, which
matters more as soon as more than one organization is contributing.

## Structure

```
ear/                              # generic EAR engine — domain-agnostic
├── constraint.py                 # Constraint
├── relation_def.py               # RelationDef
├── attribute_def.py              # AttributeDef, AttributeValueDict
├── entity_class.py               # EntityClass
├── entity.py                     # Entity
├── schema_manifest.py            # SchemaManifest (version + stability tiers)
├── helpers.py                    # build_model_from_yaml, safe_set_attr, ...
└── model/
    ├── core.py                   # Model — combines the mixins below
    ├── schema_loading.py         # YAML class loading, inheritance, introspection
    ├── entity_ops.py             # add_entity / add_attribute / add_relation / add
    ├── validation.py             # validate(), type coercion
    ├── persistence_yaml_json.py  # generic flat YAML/JSON import-export
    ├── persistence_csv.py        # generic CSV import
    ├── pydantic_export.py        # runtime pydantic model generation
    └── frictionless.py           # generic Frictionless Data Package I/O

cesdm/                             # energy-system domain layer, built on ear
├── helpers.py                     # build_model_from_yaml (CesdmModel)
└── domain/
    └── model/
        ├── core.py                # CesdmModel — combines the mixins below
        ├── discovery.py           # asset/view/domain role + view-class discovery
        ├── hierarchical_yaml.py   # native CESDM YAML round-trip
        ├── csv.py                 # CESDM CSV layouts (narrow/wide/hierarchical)
        ├── hdf5_parquet.py        # binary tabular I/O (profiles/time series)
        ├── excel.py                # spreadsheet I/O
        ├── frictionless.py         # CESDM-aware Frictionless override
        ├── library.py              # default-library import
        ├── json_schema.py          # JSON Schema export
        ├── accessors.py            # schema-safe getters/setters + read-only
        │                           #   view/asset lookups (views_for_asset,
        │                           #   get_dispatch_view, ...)
        ├── builders.py             # composite, multi-step builders only --
        │                           #   add_bus / add_thermal_generator /
        │                           #   create_generation_unit_from_technology /
        │                           #   ... -- see the module's own docstring
        │                           #   for the exact rule of what belongs here
        │                           #   vs generated_builders.py/accessors.py
        ├── generated_builders.py   # auto-generated, one add_<EntityClass>()
        │                           #   per schema class -- regenerate with
        │                           #   `cesdm-update-generated` after any
        │                           #   schema change, never hand-edit
        ├── analysis_validation.py  # CESDM addon: view_family resolution for
        │                           #   validate_for_analysis() -- the generic
        │                           #   core lives in ear/model/
        │                           #   analysis_validation.py instead
        └── statistics.py           # total_capacity(), convenience wrappers

ear_toolbox.py                     # backward-compatible shim -> re-exports `ear`
cesdm_toolbox.py                   # backward-compatible shim -> re-exports `cesdm`
```

## How the classes are assembled

`Model` and `CesdmModel` are each still a single class with one MRO —
splitting the *file* doesn't mean splitting the *class*. Each concern
lives in its own **mixin** (`SchemaLoadingMixin`, `EntityOpsMixin`,
`BuildersMixin`, ...); the class itself is assembled once, in
`ear/model/core.py` and `cesdm/domain/model/core.py` respectively, via
multiple inheritance:

```python
class Model(
    SchemaLoadingMixin,
    EntityOpsMixin,
    ValidationMixin,
    PersistenceYamlJsonMixin,
    PersistenceCsvMixin,
    PydanticExportMixin,
    FrictionlessMixin,
):
    def __init__(self):
        ...
```

```python
class CesdmModel(
    DiscoveryMixin,
    HierarchicalYamlMixin,
    CsvMixin,
    Hdf5ParquetMixin,
    ExcelMixin,
    FrictionlessMixin,     # CESDM-aware; overrides ear's generic one
    LibraryMixin,
    JsonSchemaMixin,
    AccessorsMixin,
    BuildersMixin,
    StatisticsMixin,
    Model,
):
    ...
```

This means:

- **The public API is unchanged.** `model.add_entity(...)`,
  `model.export_excel(...)`, etc. all still exist directly on the
  `Model`/`CesdmModel` instance — callers never interact with the
  mixins directly.
- **Only `core.py` needs to know the full method inventory.** Adding a
  new persistence format means adding a new mixin file and one line in
  `core.py`'s class declaration — not touching any existing file.
- `cesdm`'s `FrictionlessMixin` intentionally comes *before* `Model` in
  `CesdmModel`'s MRO, so it overrides the generic
  `ear.model.frictionless.FrictionlessMixin` implementation (CESDM
  annotates Frictionless resources with `cesdm:role` and orders them
  so domain entities import before representation views — see that
  module's docstring).

## Backward compatibility

`ear_toolbox.py` and `cesdm_toolbox.py` still exist at the repository
root, but now only re-export the same names from `ear`/`cesdm`:

```python
# cesdm_toolbox.py
from cesdm import CesdmModel, build_model_from_yaml
```

Every existing `from cesdm_toolbox import build_model_from_yaml` /
`from ear_toolbox import Model` in `examples/`, `tools/`, and `tests/`
continues to work unmodified. **New code should import from `cesdm` /
`ear` directly** — the top-level modules are a compatibility shim, not
the primary API surface, and may be removed in a future MAJOR toolbox
version once external callers have had time to migrate.

`pyproject.toml`'s `[tool.setuptools.packages.find]` was updated to
include `ear*` and `cesdm*` alongside the existing `tools*`, so
`pip install -e .` picks up the new packages.

## Verification

Before and after the split, the following were run and compared:

- `pytest tests/` — 6/6 passing, unchanged.
- Every script in `examples/` — all run to completion with unchanged
  output.
- The README quick-start snippet (`build_model_from_yaml("schemas")`).
- A byte-for-byte diff of generated YAML/Frictionless output between
  the pre-split code and the post-split code, for
  `example_multienergy.py`. One real (if pre-existing) issue surfaced
  by this diff: `_build_view_index()` iterated a `frozenset` of view
  class names, whose order depends on Python's per-process string-hash
  randomization — so the key order inside `representations:` blocks in
  hierarchical YAML exports could already vary run-to-run before this
  refactor. Fixed as part of this change (sorted iteration instead);
  see `CHANGELOG.md`.
