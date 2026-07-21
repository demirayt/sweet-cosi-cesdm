# Analysis-dependent validation

`model.validate()` checks a model's structural completeness against
the **schema** — required attributes/relations present, types and
constraints satisfied. That's necessary, but it isn't the same thing
as "ready for a specific analysis". Different analyses need different
subsets of attributes from different entity classes and their views,
often with value ranges narrower than the schema itself demands:

- An optimal-dispatch/unit-commitment study needs every
  `GenerationUnit`'s dispatch view to carry a real
  `variable_operating_cost` — the schema doesn't strictly require this
  attribute at all, since plenty of valid CESDM models (a pure
  topology study, say) never need it.
- A dynamic-stability study needs `MACHINE_xd`/`MACHINE_H` and AVR/
  governor/PSS parameters that an optimal-dispatch study doesn't care
  about in the slightest.
- The same attribute can need a *tighter* range for one analysis than
  the schema enforces globally (e.g. an analysis that assumes positive
  dispatch only, even though the schema itself allows negative values
  for some other legitimate reason).

`model.validate_for_analysis(profile)` checks fitness for a specific
analysis, declared in a YAML **analysis profile** file — the same
schema-driven philosophy CESDM already uses for its own entity/
attribute/relation definitions, applied one level up, so a new
analysis's requirements can be defined without writing any Python.

## Two layers: generic EAR core + a thin CESDM addon

Entities, attributes, relations, and constraints are core EAR
concepts, not CESDM-specific ones — so the core of this feature lives
in `ear.model.analysis_validation.AnalysisValidationMixin` and works
for *any* EAR-based schema, not just CESDM. It has no notion of
CESDM's asset/representation-view split at all: a check either finds
`attribute` directly on the entity, or it doesn't.

CESDM adds exactly one thing on top, in
`cesdm.domain.model.analysis_validation.CesdmAnalysisValidationMixin`:
resolving a check against one of an asset's representation views
(`view_family`) when the attribute isn't declared on the entity
itself — explicitly requested, or auto-detected (see "Entity-centric
checks" below). It does this by overriding
`_resolve_check_beyond_entity()`, the one extension point the generic
core defines for exactly this purpose — a plain `ear.model.Model` (no
CESDM layer loaded) implements that hook as "nothing further to try",
which is the correct, honest answer for a schema that has no concept
of views to begin with.

Concretely: `model.validate_for_analysis(...)` and
`model.load_analysis_profile(...)` work identically whether `model` is
a bare `ear.model.Model` or a `CesdmModel` — only what counts as
"beyond the entity itself" differs.

## Using it

```python
errors = model.validate_for_analysis("optimal_dispatch")
if errors:
    for e in errors:
        print(e)
else:
    print("Model is ready for an optimal-dispatch study.")

# or, to raise instead of returning the list:
model.validate_for_analysis_or_raise("optimal_dispatch")
```

`profile` can be:

- a **bare name**, looked up as `analysis_profiles/<name>.yaml`
  relative to the current working directory (as above),
- a **path** to a single profile file, or to a **directory** of
  profile files (every `*.yaml`/`*.yml` in it is merged — the same
  convention `import_library()` uses for a directory of library files),
- an **already-loaded dict**, from `model.load_analysis_profile(path)`
  — useful if you want to inspect or programmatically edit a profile
  before validating against it.

## Writing a profile

See [`analysis_profiles/optimal_dispatch.yaml`](https://github.com/cesdm/cesdm-toolbox/blob/main/analysis_profiles/optimal_dispatch.yaml)
for the full worked example. The shape:

```yaml
name: optimal_dispatch
description: >
  Free-text description of what this analysis needs and why.

requirements:
  - entity_class: GenerationUnit
    # Every entity of this class *and its subclasses* (e.g.
    # HydroGenerationUnit for a GenerationUnit requirement) is checked.
    checks:
      - attribute: nominal_power_capacity
        # Just the attribute id -- CESDM figures out on its own that
        # this lives on the asset's "dispatch" view (there's no need
        # to know or state that; see "Entity-centric checks" below).
        required: true
        constraints:
          minimum: 0
          # Same constraint vocabulary the schema itself uses for
          # attribute definitions: minimum, maximum, enum.

      - attribute: energy_conversion_efficiency
        required: false
        # required: false -- checked *if present*, not flagged if
        # absent. Useful for a constraint that should hold whenever
        # the value is set, without forcing every asset to set it.
        constraints:
          minimum: 0
          maximum: 1

  - entity_class: TransmissionLine
    checks:
      - attribute: thermal_capacity_rating
        required: true
        constraints:
          minimum: 0
```

Each `requirements` entry is one `entity_class` block; each `checks`
entry is one attribute or relation to look for, with:

| Key | Meaning |
|---|---|
| `attribute` | The attribute or relation id to check. |
| `required` | If `true` and the value is missing, that's an error. If `false`, the check only runs when a value is actually present. |
| `constraints` | Optional. `minimum`/`maximum` (numeric values) and `enum` (value must be one of a list) — the same vocabulary the schema's own attribute definitions use. |
| `view_family` | Optional, rarely needed (see below) — forces the check to look at a specific representation view rather than auto-resolving one. |

### Entity-centric checks: you don't need to know about views

A check only has to name the attribute or relation — not whether it
lives directly on the entity or on one of its representation views.
If `attribute` isn't declared on `entity_class` itself, CESDM looks
for exactly one view class among the entity's representation views
that declares it (the same schema-driven `view_family` lookup that
already powers `.dispatch`/`.powerflow`/etc. on the proxy API), and
checks it there automatically:

```yaml
- entity_class: GenerationUnit
  checks:
    - attribute: nominal_power_capacity   # -> resolves to the "dispatch" view
      required: true
    - attribute: hasTechnology             # -> a relation directly on the asset
      required: true
```

This means writing a profile never requires knowing CESDM's own
asset/view split — say what the analysis needs from the entity, not
where CESDM happens to store it.

The one thing this can't guess is a name that's genuinely ambiguous —
declared in more than one view family for the same entity class. In
practice that only happens for a handful of structural, every-view-has-
one relations (`representsAsset`, `hasRunRecord`) that no real analysis
profile would check anyway; for that rare case, add `view_family`
explicitly to force a specific one:

```yaml
- attribute: nominal_power_capacity
  view_family: dispatch   # explicit -- only needed if the name is ambiguous
  required: true
```

A missing **view** (not just a missing attribute — the view doesn't
exist on that asset at all) is reported as its own, distinct error
rather than silently creating one: unlike the proxy API's `.dispatch`
etc, which auto-create a view on first access for convenience,
validation must never have a side effect on the model it's checking.

## Design notes

- **Entity-centric by default.** A check names an attribute or
  relation, not where CESDM happens to store it — no need to know the
  asset/view split to write a profile (see above).
- **Independent of schema `required:`.** An attribute can be
  schema-optional but analysis-required, or schema-required but
  irrelevant to a given analysis — the two checks answer different
  questions and don't need to agree.
- **Subclasses are covered automatically.** A `GenerationUnit`
  requirement block also applies to every `HydroGenerationUnit`
  instance, following the schema's own inheritance tree
  (`model.inheritance`).
- **Multiple profiles can coexist.** Nothing prevents having
  `optimal_dispatch.yaml`, `dynamic_stability.yaml`,
  `investment_planning.yaml`, etc. side by side under
  `analysis_profiles/`, each checked independently — a model can be
  "ready" for one and not another at the same time, which is exactly
  the point.
- **Read-only.** `validate_for_analysis()` never modifies the model —
  it only reads existing attributes/relations/views.

See [`examples/example_analysis_validation.py`](https://github.com/cesdm/cesdm-toolbox/blob/main/examples/example_analysis_validation.py)
for a complete, runnable walkthrough.
