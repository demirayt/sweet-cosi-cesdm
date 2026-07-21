# CESDM schema and library layout

CESDM separates the schema language from reusable master-data instances.

## Schema

```text
schemas/
├── core/          # SemanticEntity, ports and shared structural classes
├── assets/        # Generation, demand, storage, conversion and grid assets
├── nodes/         # Electrical, gas, heat, hydrogen and water nodes
├── carrier/       # EnergyCarrier and NaturalResource schema classes
├── technology/    # GeneratorType, StorageType and other technology templates
├── profiles/      # Profile and TimestampSeries schema classes
├── system/        # EnergySystemModel, regions and run records
├── controllers/   # AVR, governor and PSS model schemas, nested by family:
│   ├── AVR/       #   ControllerView.AVR, ControllerView.AVR.AC1A, ...
│   ├── GOV/       #   ControllerView.GOV, ControllerView.GOV.IEEEG1, ...
│   └── PSS/       #   ControllerView.PSS, ControllerView.PSS.PSS2A, ...
│                  #   (ControllerView.yaml itself has no family and stays
│                  #    at controllers/ root)
├── views/         # Representation views grouped by analysis domain
│   ├── dispatch/
│   ├── powerflow/
│   ├── dynamics/
│   ├── topology/
│   ├── planning/
│   ├── spatial/
│   ├── technical/
│   └── results/   # Result views, nested by the analysis domain that
│                  # produced them (mirrors the input-view split above):
│       ├── ResultView.yaml     # shared abstract base (hasRunRecord)
│       ├── dispatch/           # e.g. GenerationUnit.DispatchResultView
│       ├── powerflow/          # e.g. ElectricalBus.PowerFlowResultView
│       └── dynamics/           # e.g. Generator.DynamicResultView
├── attributes/    # Central attribute registry
├── relations/     # Central relation registry
└── units/         # Central unit registry
```

The directory name is organizational only. Class identity and inheritance are
specified inside each YAML file. The loader scans the schema tree recursively.

### Filename convention

A schema file's name must equal its declared `name:` field plus `.yaml`,
including dots for dot-namespaced classes:

```yaml
# schemas/views/dispatch/Demand.DispatchView.yaml
name: Demand.DispatchView
```

This isn't required for loading (class identity comes from `name:`, not
the path), but it is required for the schema tree to be greppable —
`grep -r "Demand.DispatchView" schemas/` should find the file by name,
not just its contents. `tests/test_schema_filenames_match_class_names.py`
enforces this for every schema file across `schemas/` and
`schemas_agentbased/` (registry files — `attributes.yaml`,
`relations.yaml`, `_index.yaml`, `SCHEMA_MANIFEST.yaml` — are exempt,
since they aren't single-class definition files).

### Registry folders vs. entity-class folders

Most subdirectories of `schemas/` (`assets/`, `nodes/`, `views/`, ...)
hold **entity class definitions** — one class per file, discovered
automatically by recursively scanning for `*.yaml`. Directory placement
there is purely organizational.

`attributes/`, `relations/`, and `units/` are architecturally
different: they hold **global registries** — flat id → spec
dictionaries referenced by id from entity class definitions elsewhere
(or, for `units/`, from attributes' `unit.constraints.enum` values).
Like the entity-class folders, every `*.yaml` file present is
auto-discovered and merged — there is no curated file list to keep in
sync. The one property that does matter is still enforced: a registry
id must not be defined twice with conflicting specs (`ValueError` at
load time if it is). `units/` additionally enforces that every
attribute's unit(s) actually exist in the registry — see
`docs/architecture/schema_governance.md` ("Central unit registry").

An earlier version required each of these two folders to carry a
curated `_index.yaml` with an explicit `imports:` list. That was
removed: the ordering it provided was never functionally
meaningful — a duplicate id across files was always a hard error,
never "last file wins" — so it was a second file to keep in sync with
reality for no real benefit, which is exactly the kind of drift that
left `schemas_agentbased/assets/_index.yaml` stale (see
`CHANGELOG.md`). Adding a new attribute or relation file today needs no
registration step, the same as adding a new class file anywhere else
in the tree.

### Cross-tree dependencies (`extends`)

A schema tree may depend on another one instead of duplicating its
classes. Declare this in `SCHEMA_MANIFEST.yaml`:

```yaml
extends:
  - ../schemas
```

`load_classes_from_yaml` resolves and auto-loads `extends` targets
before the declaring tree's own classes, so
`build_model_from_yaml("schemas_agentbased")` alone is equivalent to
`build_model_from_yaml(["schemas", "schemas_agentbased"])` — the
extension doesn't need its own copy of `EnergyAssetInstance`,
`SemanticEntity`, etc. just to be independently loadable. See
`schemas_agentbased/SCHEMA_MANIFEST.yaml` for the real example.

### Result views and RunRecord (provenance)

A result view's shape is dictated by which analysis domain produced
it, so `views/results/` is subdivided the same way the input views
are — `results/dispatch/`, `results/powerflow/`, `results/dynamics/`
— rather than being one flat, dispatch-shaped family.

Every result view carries `hasRunRecord`, a relation back to the
`RunRecord` that produced it (not a plain string attribute — this is
what lets the relation engine validate and traverse it). `RunRecord`
is an abstract base (`schemas/system/RunRecord.yaml`), analogous to
`EnergyAssetInstance` for assets: `DispatchRunRecord`,
`PowerFlowRunRecord`, and `DynamicRunRecord` are its concrete
subclasses, each carrying domain-specific run metadata (solver name
and objective value for a dispatch run; convergence tolerance for a
power-flow run; integration method for a dynamics run). Each domain's
abstract result-view base narrows `hasRunRecord`'s target to its own
`RunRecord` subclass (e.g. `PowerFlowResultView.hasRunRecord` targets
only `PowerFlowRunRecord`).

For chained multi-stage workflows (dispatch → power-flow → dynamics),
`RunRecord.hasInputRun` links a run to the upstream run whose output
it used as input, so the full provenance chain is traversable from any
result view backward through every analysis stage that fed into it.
A single asset can carry result views from multiple domains
simultaneously — e.g. a generator with both a
`GenerationUnit.DispatchResultView` and a `Generator.DynamicResultView`
from the same chained run — without collision, the same way an asset
can carry multiple input representation views.

**Power-flow results: snapshot vs. time series.** A power-flow study
is either a single-snapshot solve (one fixed operating point — the
common case, and what this toolbox's own pandapower/MATPOWER
integrations produce via one solver call) or a time-series
("quasi-steady-state") study run across many operating points.
`PowerFlowRunRecord.hasTimestampSeries` is optional — unlike
`DispatchRunRecord`'s required one — and its presence/absence is the
explicit signal for which kind a given run is. Every
`*.PowerFlowResultView` therefore carries plain snapshot-value
attributes (`voltage_magnitude_pu`, `loading_percent`, ...) that are
always the primary values; `average`/`min`/`max` attributes and
`Profile` relations are populated only for a time-series run.

### `view_family` (optional class field)

A view class may declare `view_family: <name>` (e.g.
`view_family: dispatch` on `OperationalDispatchView`) — a free-text tag
consumed by `cesdm.proxy.AssetProxy` to resolve `.dispatch`,
`.powerflow`, `.topology`, etc. to the right view class for an asset
(`docs/architecture/proxy_api.md`). It is not a core EAR concept and
has no effect on validation, export, or anything else — purely
descriptive metadata for that one consumer.

Unlike `abstract`, `view_family` **does** inherit from parent to
child: declare it once on a family's abstract root and every concrete
subclass gets it automatically (`ear/model/schema_loading.py`
resolves this the same way it resolves attributes/relations — child's
own declared value wins if set, otherwise the first parent's resolved
value). The ten existing families (dispatch, powerflow, dynamic,
topology, planning, spatial, technical, and their result-view
counterparts) are each tagged exactly once, on their abstract root:

| Family | Root class | File |
|---|---|---|
| `dispatch` | `OperationalDispatchView` | `schemas/views/dispatch/` |
| `dispatch` | `DispatchResultView` | `schemas/views/results/dispatch/` |
| `powerflow` | `PowerFlowView` | `schemas/views/powerflow/` |
| `powerflow` | `PowerFlowResultView` | `schemas/views/results/powerflow/` |
| `dynamic` | `DynamicView` | `schemas/views/dynamics/` |
| `dynamic` | `DynamicResultView` | `schemas/views/results/dynamics/` |
| `topology` | `NetworkTopologyView` | `schemas/views/topology/` |
| `planning` | `AssetPlanningView` | `schemas/views/planning/` |
| `spatial` | `SpatialView` | `schemas/views/spatial/` |
| `technical` | `Generation.TechnicalView` | `schemas/views/technical/` |

Adding a new view family — for a hypothetical `EconomicView` root, say
— only requires adding `view_family: economic` to that one file;
`asset.economic` then resolves automatically, with no change to
`cesdm/proxy.py`.

## Default library

```text
library/default_library/
├── carriers/
├── resources/
├── generator_types/
└── storage_types/
```

The default library contains entity instances, not schema definitions. Load it
with:

```python
model.import_library("library/default_library")
```

A single YAML library file remains supported by `import_library()` for external
libraries, but the built-in library is modular.
