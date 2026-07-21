# The CESDM Toolbox (`cesdm_toolbox.py`)

`cesdm_toolbox` extends `ear_toolbox` with energy-domain awareness: the
object-oriented proxy API and builder functions for everyday model
building, energy-domain export/import adapters, the Representation
View infrastructure, and schema-driven role classification underneath
it all.

```python
from cesdm_toolbox import build_model_from_yaml, CesdmModel
```

---

## Loading a schema

```python
from cesdm_toolbox import build_model_from_yaml

model = build_model_from_yaml("schemas")
```

`build_model_from_yaml` does four things:

1. Scans all `*.yaml` files in the schema directory recursively
2. Registers every entity class, attribute, and relation definition
3. Resolves inheritance (child classes inherit parent attributes/relations)
4. **Validates all `representsAsset.target` references** — if a view schema
   declares a target class that does not exist, a `ValueError` is raised
   immediately with the class name and a suggestion for what you may have
   meant

```
ValueError: Schema validation failed — unknown relation target(s):
- [Generation.DispatchView] representsAsset.target 'GenerationUnitXXX'
  is not a known class.  Did you mean: GenerationUnit, GeneratorType?
```

---

## Building models: the object-oriented proxy API

This is what everyday CESDM code should look like, and the single most
commonly used part of `cesdm_toolbox`. Builder functions (`add_bus`,
`add_generator`, `create_demand_unit`, `create_transmission_line`,
`add_reservoir_hydro`, ...) each create an entity *and* wire up the
views/relations that go with it in one call, and hand back a live
object you keep working with:

```python
model.import_library("library/default_library")

bus1 = model.add_bus("bus.1", nominal_voltage=380)

gas = model.add_generator(id="gas.1", technology="Generation.Thermal.Gas.CCGT.New", bus=bus1)
gas.name = "Test plant"
gas.dispatch.nominal_power_capacity = 400   # sets the attribute on the right view
gas.connect(bus1)                           # wires a topology relation
```

A few things worth knowing:

- **The returned object (`gas`) is a real `AssetProxy`** — a `str`
  subclass, so it's usable anywhere a plain entity id is expected
  (dict keys, `==`, passed into any lower-level `model.*` method):

  ```python
  print(gas, isinstance(gas, str))   # -> gas.1 True
  ```

- **`.dispatch`/`.powerflow`/`.topology`/`.avr`/`.governor`/`.pss`** are
  lazily created `ViewProxy` objects, resolved via the class's
  `view_family` (see `docs/architecture/proxy_api.md` for the full
  resolution mechanism) — you never need to know or type the concrete
  view class name (`Generation.DispatchView`, `HydroGenerationUnit.
  DispatchView`, ...) yourself.

- **Typos are caught immediately**, with a spelling suggestion, instead
  of silently doing nothing:

  ```python
  gas.dispatch.nomial_power = 1
  # AttributeError: 'nomial_power' is not an attribute or relation of
  # 'Generation.DispatchView'. Did you mean: nominal_power_capacity?
  ```

- **For static type-checking** (Pyright/Pylance in an editor), `model.
  asset(entity_id)` returns the generic `AssetProxy` type — correct at
  runtime, but `.dispatch.x` won't type-check against it. Use
  `asset_as(entity_id, SpecificProxyClass)` when you need the concrete
  type to check too:

  ```python
  from cesdm.generated_proxies import GenerationUnitProxy
  gas = model.asset_as("gas.1", GenerationUnitProxy)
  gas.dispatch.nominal_power_capacity = 400   # now type-checks
  ```

See [`docs/getting_started.md`](../getting_started.md) for the
same model built with lower-level builder functions (no proxy sugar)
and with the raw EAR primitives directly, and
[`docs/architecture/proxy_api.md`](../architecture/proxy_api.md)
for the full design of this layer.

---

## Adding a technology library

The technology library holds shared techno-economic parameter templates for
generator and storage technology classes:

```python
model.import_library("library/default_library")
```

(`import_library` also accepts a path to a single YAML file, but a directory
of modular files -- the shipped `library/default_library/` -- is the norm.)

After loading, asset instances can reference library types via `hasTechnology`
(already done above through `technology=`) — export adapters read from the
instance's concrete dispatch view first — for example
`Generation.DispatchView`, `Storage.DispatchView`, or
`HydroGenerationUnit.DispatchView` — and fall back to the `GeneratorType`
via `hasTechnology` for attributes not set on the instance. Instance-specific
values always override library defaults.

---

## Export methods

### Canonical archive formats (lossless)

```python
# Hierarchical YAML — one section per class, views nested under assets
model.export_yaml_hierarchical("output.yaml")

# Hierarchical CSV — one file per class
model.export_csv_hierarchical("output_dir/")
```

### Analyst-friendly formats

```python
# Excel workbook — one sheet per class
model.export_excel("output.xlsx")

# Flat Excel — one sheet per class, all attributes as columns
model.export_excel_flat("output_flat.xlsx")

# Wide CSV directory — one CSV per class, all attributes as columns
model.export_csv_by_class_wide("output_csv_dir/")
```

### Exchange formats

```python
# Frictionless Data Package — self-describing, shareable
# Includes embedded Table Schema with types, constraints, units, foreign keys
dp_path = model.export_frictionless(
    "output_package/",
    name        = "cesdm-my-scenario",
    title       = "My Energy System Scenario",
    description = "Full description of the scenario.",
    version     = "1.0.0",
)

# A narrower variant: datapackage.json only, for by_class_wide resources,
# with each resource's schema embedded inline (no external schema files)
model.export_datapackage("output_dir/")
```

### Profile formats

```python
# CESDM hierarchical HDF5
model.export_hdf5("profiles.h5", values_map=profiles_values)
```

---

## Import methods

Every export method has a corresponding import method:

| Export | Import |
|--------|--------|
| `export_yaml_hierarchical` | `import_yaml_hierarchical` |
| `export_csv_hierarchical` | `import_csv_hierarchical` |
| `export_excel` | `import_excel` |
| `export_excel_flat` | `import_excel_flat` |
| `export_csv_by_class_wide` | `import_csv_by_class_wide` |
| `export_frictionless` | `import_frictionless` |
| `export_datapackage` | `import_datapackage` |
| `export_hdf5` | `import_hdf5` |

All import methods are schema-driven: each column in the CSV or sheet is
routed to `add_attribute` or `add_relation` based on the schema, with no
hardcoded column-to-field mappings.

`import_frictionless` sorts resources by role annotation (`custom.role`)
before loading — domain and asset entities first, representation views last —
so `representsAsset` relations are always resolvable in a single pass.

---

## Validation

Two independent kinds of check:

```python
errors = model.validate()
target_errors = model.validate_relation_targets()
```

`validate()` checks:
- Required attributes present on all entities
- Attribute values satisfy type and range constraints
- Required relations present on all entities
- Relation targets exist and are of the correct class

`validate_relation_targets()` checks schema-level correctness:
- Every `representsAsset.target` value names an existing class
- Run automatically by `build_model_from_yaml`

Neither of these checks whether the model is ready for a *specific
analysis* — an optimal-dispatch study needs `variable_operating_cost`
on every generator's dispatch view, a dynamic-stability study needs
different attributes entirely. That's a separate, third kind of check,
declared in a YAML profile rather than hard-coded:

```python
errors = model.validate_for_analysis("optimal_dispatch")
```

See [`docs/architecture/analysis_validation.md`](../architecture/analysis_validation.md)
for the full design and how to write a profile for a new analysis.

---

## Carrier constants (`tools/cesdm_carriers.py`)

Canonical carrier/resource ids, CO₂ intensities, and fuel costs shared
by the TYNDP and PyPSA importers live in `tools/cesdm_carriers.py` —
not part of `cesdm_toolbox` itself, and not a top-level installed
module (both importers add `tools/` to `sys.path` themselves). Reach
for this directly only if you're writing a new importer that needs the
same canonical ids: `canonical_carrier_id("gas")` resolves to
`"carrier.fuel.fossil.gas.natural_gas"`, `CARRIER_CO2[...]` and
`CARRIER_PRICE[year][...]` hold the corresponding constants. See the
module's own docstring for the full function list.

---

## Internals

Everything below is implementation detail `cesdm_toolbox` uses
internally (hence the leading underscore on each name) — useful to
know if you're debugging the toolbox itself or extending it, not
needed for everyday model building.

### Schema-driven role classification

`CesdmModel` never uses a hardcoded list of class names. Role is derived
purely from class structure via `_derive_role_from_parents` — no `role:`
YAML field consulted, no hardcoded seed frozensets of "anchor" class names:

```python
model._derive_role_from_parents("GenerationUnit")           # -> "asset"
model._derive_role_from_parents("Generation.DispatchView")  # -> "view"
model._derive_role_from_parents("ElectricalBus")            # -> "domain"
model._derive_role_from_parents("OperationalDispatchView")  # -> "domain" (abstract base)
```

The rules, checked in order:

1. **View** — the class or any ancestor declares `representsAsset` as a
   relation. This covers every concrete view and its abstract bases
   (`OperationalDispatchView`, `PowerFlowView`, ...) without needing to
   name them individually.
2. **Asset** — the class *is* `EnergyAssetInstance` or inherits from it
   (directly or transitively).
3. **Domain** — everything else.

Discovery methods (all cached after first call):

```python
views      = model._discover_view_classes()      # frozenset of view class names
assets     = model._discover_asset_classes()     # frozenset of asset class names
non_assets = model._discover_non_asset_classes() # frozenset of domain class names
view_map   = model._discover_view_map()          # {asset_class: [view_class, …]}
```

If you add new classes to `model.classes` after the first call to any
discovery method, clear the cache — rarely needed outside of
dynamically extending the schema at runtime:

```python
model._invalidate_discovery_cache()
```

### Schema abbreviations

`_abbrev_for(class_name)` returns a short string for Excel sheet names.
It reads an `abbrev:` field from the schema class definition if
present; otherwise it strips a known suffix (`DispatchView`,
`PowerFlowView`, `TopologyView`, `View`, `Unit`, `Element`, `Class`)
and truncates to 15 characters:

```python
model._abbrev_for("Generation.DispatchView")  # -> "Generation."
model._abbrev_for("SinglePort.TopologyView")  # -> "SinglePort."
model._abbrev_for("TransmissionLine")         # -> "TransmissionLin" (no known suffix to strip -- truncated as-is)
```

For custom classes, add an `abbrev:` field to the schema YAML instead
of relying on the fallback:

```yaml
name: HydrogenElectrolyserDispatchView
abbrev: H2Electrolyser
```
