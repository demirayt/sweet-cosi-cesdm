# Schema governance

`schemas/` and `schemas_agentbased/` are not just source code — they are
the actual *interoperability contract* CESDM offers to modellers and
companies exchanging data. This document says what "versioned and
governed" means in practice for this repository, and stops short of
introducing process overhead the project doesn't need yet.

## Version number

Each schema tree carries a single semantic version, declared in
`SCHEMA_MANIFEST.yaml` at its root (`schemas/SCHEMA_MANIFEST.yaml`,
`schemas_agentbased/SCHEMA_MANIFEST.yaml`):

```yaml
version: "0.1.0"
```

This is read by `ear.schema_manifest.SchemaManifest.load()` and
attached to every model as `model.schema_manifest`. It is domain-agnostic
machinery living in the generic `ear` package — versioning a schema tree
is a property of the EAR approach in general, not something CESDM-specific.

### What bumps which number

| Change | Bump | Example |
|---|---|---|
| Wording/typo fix, clarified `description:`, no structural change | PATCH | Fixing a docstring on `hasOutputCarrier` |
| Additive, backward-compatible change | MINOR | New optional attribute on `GenerationUnit`; new `ControllerView.GOV.*` model; new representation view class |
| Breaking change | MAJOR | Renaming/removing a class, attribute, or relation; changing a relation's cardinality or `required:` flag; changing an inheritance root |

The test is always: **does a model that validated against the old
version still validate, unchanged, against the new one?** If yes, it's
MINOR/PATCH. If no, it's MAJOR.

### What this buys an integrator

`export_yaml_hierarchical()` writes the exporting schema's version into
a `_cesdm_meta` header:

```yaml
_cesdm_meta:
  schema_version: 0.1.0
  format: cesdm-hierarchical-yaml
EnergyCarrier:
  ...
```

`import_yaml_hierarchical()` compares that against the *currently
loaded* schema's major version and emits a `UserWarning` (never a hard
failure — CESDM is still a research prototype, not a system that should
refuse your data) if they differ, so a silent structural mismatch
doesn't masquerade as a clean import. The warning text is also returned
in the summary dict (`schema_version_warning` key) for programmatic
handling.

This is intentionally lightweight: no schema migration tooling, no
"upgrade this model" command. That is future work if/when the schema
stabilizes enough for migrations to be worth automating — see the
disclaimer in `docs/guide/00_disclaimer.md`.

## Stability tiers

Not every part of the schema tree is equally mature. `SCHEMA_MANIFEST.yaml`
declares a tier per **family** (a top-level schema subdirectory, or a
nested path like `views/dynamics` where a directory contains a mix of
maturity levels):

- **`stable`** — exercised by the PyPSA/TYNDP import workflows and the
  MATPOWER/pandapower round-trip examples, or is foundational structure
  (`core/`) that everything else depends on. Safe to build a long-lived
  external integration against; breaking changes here are rare and will
  be a MAJOR bump with a CHANGELOG entry.
- **`experimental`** — present and usable, but with less cross-tool
  round-trip coverage (e.g. `controllers/`, most of `views/*` besides
  topology/dispatch/power-flow, all of `schemas_agentbased/`). Expect
  more churn; don't assume field names or structure are final.
- **`deprecated`** — kept for backward compatibility, scheduled for
  removal in a future MAJOR version. (No families are deprecated yet.)

Query it from code:

```python
model.schema_manifest.stability_for("controllers")   # "experimental"
model.schema_manifest.stability_for("assets")         # "stable"
```

This is informational, not enforced — CESDM does not currently reject
a model for using an experimental family. The intent is to give an
external integrator an honest signal about what's safe to depend on,
which is the main thing "provisional research prototype" was failing
to communicate at a granular level before this.

## Proposing a schema change

For anything beyond a typo fix, open an issue or PR that states:

1. **What** is changing (which file, which class/attribute/relation).
2. **Why** — what modelling need isn't currently representable, or what
   is currently ambiguous/inconsistent.
3. **Bump level** (PATCH/MINOR/MAJOR) per the table above, with a
   one-line justification.
4. **Affected stability tier(s)** — a MAJOR change to a `stable` family
   is a bigger deal than the same change to an `experimental` one, and
   should say so explicitly.
5. A CHANGELOG.md entry under `[Unreleased]`, in the same PR.

This is deliberately a lightweight PR-template-shaped process, not a
formal RFC body — CESDM has one implementation and (currently) one
primary maintaining group. If/when multiple organizations are actively
building on `stable` families, this is the place to add: a review
window before merging MAJOR changes to `stable` families, and a
migration note requirement alongside the CHANGELOG entry.

## Cross-tree dependencies

A schema tree that builds on another one (e.g. `schemas_agentbased/`
building on `schemas/`) declares that with `extends:` in its manifest
rather than copying the depended-on classes:

```yaml
extends:
  - ../schemas
```

The loader auto-resolves and loads `extends` targets first, so the
extension is independently loadable without a local fork of the base
tree's classes. This replaced a prior state where
`schemas_agentbased/` carried byte-identical copies of 7 core classes
(plus one that had already drifted in wording) purely so it could be
loaded standalone — see `CHANGELOG.md` and `docs/schema_layout.md`
("Cross-tree dependencies").

## Registry-folder consistency

`attributes/` and `relations/` are auto-discovered the same way every
other schema folder is — every `*.yaml` file present is picked up, no
registration step required. What the loader still enforces is the
property that actually matters: a registry id must not be defined
twice with conflicting specs across files (`ValueError` at load time).
An earlier `_index.yaml`-based curated-file-list mechanism was removed
because it added a second file to keep in sync with reality without
providing any real benefit (see `CHANGELOG.md`). See
`docs/schema_layout.md` ("Registry folders vs. entity-class folders").

## Central unit registry

`schemas/units/units.yaml` is the single source of truth for every
unit used anywhere in the schema tree — the same registry-folder
pattern as `attributes/` and `relations/` (auto-discovered, no
`_index.yaml`). Each entry has a `symbol` (the canonical spelling),
`quantity_kind` (a rough dimensional tag — `power`, `energy`, `angle`,
`dimensionless_fraction`, `cost_rate`, ...; informational only, not
currently used for automated dimensional-consistency checking), and a
`description`.

`load_classes_from_yaml` validates every attribute's
`unit.constraints.enum` values against this registry at load time: an
attribute using an unregistered unit string — a typo, or a new
spelling of an existing unit — fails to load immediately with a clear
error, rather than silently introducing the kind of drift that a
51-string, 4-different-spellings-of-"fraction" mess (see
`CHANGELOG.md`) needed a manual audit to catch after the fact. Look up
a unit's registry entry from code via `model.unit_info("MW")`.

Adding a genuinely new unit: add it to `schemas/units/units.yaml`
first, then reference its exact `symbol` from any attribute's
`unit.constraints.enum`. This is additive (MINOR bump) unless it also
involves renaming an existing unit's canonical spelling, which is
breaking for anyone already using the old spelling (MAJOR, or MINOR
pre-1.0 per the convention used throughout this changelog).

## Attribute and relation naming conventions

These aren't enforced by the loader (except where noted), but are
expected of new schema contributions, and are backed by regression
tests where a violation is mechanically checkable:

- **Don't embed a unit abbreviation in an attribute id.** The unit
  belongs solely in the attribute's `unit.constraints.enum` field.
  `voltage_magnitude` (unit: `pu`), not `voltage_magnitude_pu`. The
  dominant existing convention (`nominal_power_capacity`,
  `reactive_power_demand`, ...) has never done this; keep it that way.
- **Unit strings must exist in the central unit registry.** See
  "Central unit registry" above — this is now enforced at load time,
  not just documented; an attribute referencing an unregistered unit
  string fails to load. `tests/test_unit_registry.py` and `tests/
  test_unit_vocabulary_consistency.py` cover it from both the
  enforcement side and the specific-spellings side.
- **A unit enum value is one unit, not several crammed into one
  string.** `enum: [MU/kW, MU/MW]`, never `enum: ["MU/kW, MU/MW"]`.
  Checked by `test_no_comma_crammed_unit_values`.
- **Categorical string attributes**: if the domain is genuinely closed
  (mirrors an existing fixed set elsewhere in the schema, e.g.
  `carrier_group` mirroring the five `*Bus` node types), give it a
  real `value.constraints.enum`. If the domain is open/extensible by
  design (new generation technologies, resource types, etc. are
  expected over time), don't force a closed enum — document a
  recommended starting vocabulary in the description instead, so
  contributors have a convention to follow without being blocked from
  adding a legitimate new value. See `generator_technology_type` /
  `resource_type` / `storage_technology_type` / `carrier_type` for the
  documented-but-open pattern, versus `carrier_group` / `resource_group`
  for the enforced-closed pattern.
- **A top-level `constraints:` key on an attribute does nothing.**
  Constraints are read from `value.constraints` or `unit.constraints`
  only (see `ear/attribute_def.py`). A stray top-level `constraints:`
  key is silently ignored by the loader. If you find one, the fix is
  almost always "move this into `value.constraints`," not "delete it
  and lose the intent" — a stray top-level key often reflects a
  genuinely-intended bound that was simply never actually enforced.
- **Exception to snake_case: dynamic/controller model parameters use
  their literature's own symbol notation.** ~130 attributes under the
  `AVR_*`, `GOV_*`, `PSS_*`, `HVDC.*`, and `MACHINE_*` families (e.g.
  `AVR_SEXS_Ka`, `GOV_GGOV1_Kpgov`, `MACHINE_Td0_prime`) are
  deliberately *not* snake_case — they match the exact symbol from the
  IEEE/PSS-E standard model they represent, which is more useful to a
  power-systems engineer than a verbose rename, and matches how these
  parameters are named in every textbook and vendor tool. This is not
  an oversight; do not "fix" these to snake_case. It also explains the
  family-prefix namespacing used only here (`AVR_SEXS_Ka` vs
  `AVR_IEEET1_Ka`, ...): many controller models reuse the same short
  IEEE symbol (`Ka`, `Ta`, `T1`...), so the model-family prefix is
  required to avoid id collisions — this is the one place in the
  schema where attribute ids are namespaced this way. Originally
  dot-separated (`AVR.SEXS.Ka`) to visually mirror the literature's
  own `Family.Model.Parameter` convention; changed to underscores
  (`AVR_SEXS_Ka`) so these ids work as plain Python identifiers/kwargs
  directly (`add_generator_dynamic_view_subtransient(id,
  MACHINE_xd=1.8, ...)`) without a caller having to
  `str.replace(".", "_")` first — the family-prefix disambiguation is
  unchanged, only the separator character is.

  All ~113 of these that don't require a plant-specific value (rated
  MVA/kV, MW power limits, and the discrete model-order fields are the
  exceptions) carry a schema-level `default:` — real IEEE Std 1110-2002
  / IEEE Std 421.5-2016 / Kundur / PSS/E Model Library typical
  reference values, not invented numbers. These apply automatically on
  entity creation (`ear.model.entity_ops.add_entity` already applies
  every attribute's `default` unconditionally — this was a pre-existing
  mechanism, not something new built for this), so `gen.dynamic.
  MACHINE_xd` or `gen.avr.AVR_SEXS_Ka` return a sensible value even if
  never explicitly set, through *any* construction path — hand-written
  builder, generated `add_<EntityClass>()`, or raw `add_entity`. They
  are starting points for a study, not measured parameters for any
  specific real machine — override them for anything beyond a rough
  first model.

  Every one of these should carry a `provenance_ref` citing the
  source standard or vendor model library (see `AVR_SEXS_Ka`:
  `provenance_ref: "PSS/E Model Library, SEXS."`, paired with a
  description that includes the actual governing transfer-function
  equation) — but this is currently inconsistent: only `AVR.SEXS` (1
  of 2 attributes) and 4 of `MACHINE`'s ~19 attributes have one; every
  other family (`AC1A`, `IEEET1`, `ST1A`, `GGOV1`, `HYGOV`, `IEEEG1`,
  `LCC`, `VSC`, `PSS2A`, `PSS2B`, most of `STAB1`) has none, despite
  clearly following the same literature-derived convention. Filling
  these in needs real access to the source standards to cite
  correctly — a fabricated citation would be worse than none — so
  this is flagged here as known, real, unfinished work rather than
  silently left looking like an oversight.

## Formal ontology alignment (partial)

`CesdmModel.export_rdf_schema(path)` exports the loaded *schema*
(classes, attributes, relations — not instance data) as an OWL
ontology in Turtle syntax: classes become `owl:Class` with
`rdfs:subClassOf` from the inheritance graph, relations become
`owl:ObjectProperty`, attributes become `owl:DatatypeProperty`. Where
an attribute accepts exactly one registered unit and that unit's
`schemas/units/units.yaml` entry has `qudt_status: verified`, a
`cesdm:hasUnit` annotation points at the real QUDT unit IRI.

Two important limitations, both deliberate:

- **The namespace is provisional.** `cesdm.domain.model.rdf_export.
  CESDM_ONTOLOGY_NAMESPACE` currently points at the project's existing
  published GitHub Pages docs URL as a reasonable placeholder, not a
  namespace confirmed final by the schema's maintainers. Minting a
  permanent identifier and later changing it breaks anyone who
  referenced it — re-basing later only requires changing this one
  constant, but that decision hasn't been made yet.
- **QUDT unit coverage is small and honest, not complete.** Only 4 of
  47 registered units (`MW`, `MWh`, `kV`, `kW`) have a QUDT IRI that
  has actually been verified against the live QUDT vocabulary — the
  rest are marked `qudt_status: unverified` (plausibly mappable,
  not yet checked) or `no_qudt_equivalent` (`date`, `Timestamp / time
  index` — definitionally outside QUDT's scope, which models physical
  units of measurement, not calendar references). Pattern-guessing the
  remaining ~35 IRIs is deliberately avoided: a wrong QUDT mapping
  that looks authoritative is worse than an honestly-unmapped one.
  Completing this needs either individual verification per unit or a
  bulk cross-reference against QUDT's published TTL/JSON vocabulary
  export.

Not attempted: exporting model *instance* data (entities and their
attribute/relation values) as RDF individuals — a separate, larger
feature from schema export.

## Non-goals (for now)

- **No automated schema-diff / breaking-change linter yet.** The bump
  level is currently a human judgment call using the table above. A
  natural follow-up once the schema is more stable: a CI check that
  loads schema at tag `vN` and `vN+1` and flags removed/renamed
  classes, attributes, or relations that weren't accompanied by a MAJOR
  bump.
- **No per-model minimum-schema-version pinning.** The compatibility
  check is major-version-only; finer-grained "requires >= 0.3.0"
  constraints are not implemented.
