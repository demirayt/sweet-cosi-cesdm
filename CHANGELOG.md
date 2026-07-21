# CESDM changelog

This file tracks both the **schema tree** (`schemas/` and
`schemas_agentbased/` — see `schemas/SCHEMA_MANIFEST.yaml` /
`schemas_agentbased/SCHEMA_MANIFEST.yaml`'s `changelog:` field and the
version-compatibility check in
`cesdm.domain.model.hierarchical_yaml.import_yaml_hierarchical`) and
the Python toolbox (`ear/`, `cesdm/`, `tools/`, examples, and
documentation) built on top of it.

Schema versioning follows semver (`MAJOR.MINOR.PATCH`) as defined in
`docs/architecture/schema_governance.md`.

## [Unreleased]

### Changed

- **README's "What is CESDM?" section restructured into three clearly
  headed subsections** — asked directly for the progression to read
  as its own section per layer: EAR (any structured system describable
  with three building blocks) first, then CESDM (EAR applied
  specifically to energy systems, with energy-domain helper APIs) as
  its own section, then the proxy API (the same system, described more
  conveniently) as its own section after that. The content itself
  already made exactly this argument — it just lived as three
  unlabelled bold-lead-in paragraphs under one heading rather than as
  three distinct, scannable sections; split apart with no wording
  changes to the substance, verified the internal links and image
  still resolve.


- **README's "What is CESDM?" restructured to lead with EAR, not
  CESDM** — requested directly: Entity/Attribute/Relation is a
  general-purpose idea that can describe *any* structured system, not
  an energy-specific one, and the README previously introduced
  entities/attributes/relations as if they were CESDM's own concepts.
  Reordered: EAR's generality first (with a pointer to
  `examples/example_ear_generic_domain.py` as direct proof — zero
  energy-specific code), then CESDM as what applying that idea to
  energy systems produces (the energy schema, helper builder
  functions, representation views, importers/exporters), then the
  object-oriented proxy API as a convenience layer describing the
  identical underlying data, not a different model.

### Fixed

- **`examples/example_import_tyndp.py` looked for
  `TYNDP24_StorageCapacitites.csv`** (extra "tites") in its actual,
  executed file-path construction — every other mention of this
  filename in the codebase (docstrings, the proxy-API sibling)
  already had the correct spelling, `TYNDP24_StorageCapacities.csv`,
  making this specifically a runtime bug, not just a documentation
  inconsistency: anyone with a correctly-named real TYNDP dataset
  would have had storage energy capacities silently go unread. Fixed
  at the one real occurrence, plus two matching mentions in
  `examples/README_TYNDP_IMPORT_LOGIC.md`; confirmed no occurrence of
  the misspelling remains anywhere in the repository.

- **`download_external_data.py` was a completely orphaned script** —
  reported directly: a user hit `[SSL: CERTIFICATE_VERIFY_FAILED]
  certificate verify failed: self-signed certificate in certificate
  chain` running it. Checking first: the script existed at the
  repository root but was never referenced from `README.md` or
  `docs/` anywhere, and — since `ethz.ch` isn't a reachable domain in
  this environment either — had never actually been exercised. The
  reported error is the specific signature of a network intercepting
  HTTPS traffic (common on corporate/institutional staff networks and
  VPNs presenting their own certificate) rather than a problem with
  the script or with ethz.ch, so the fix is better diagnostics and an
  explicit opt-in, not silently disabling verification: on an SSL
  certificate error, the script now prints both likely causes
  (intercepting proxy vs. an outdated/missing certificate bundle —
  the classic macOS python.org-installer issue, fixed by running its
  bundled "Install Certificates.command") and how to address each,
  plus a `--insecure` flag for a user who has checked both and
  explicitly accepts the risk — off by default, since disabling
  certificate verification removes protection against a genuine
  man-in-the-middle attack, not just a warning. Wired into
  `docs/importers/tyndp.md` (which `docs/importers/pypsa.md` already
  points to for this same dataset) so it's no longer orphaned. 5 new
  regression tests covering the parts that don't need a real network
  call: the default stays secure (no SSL context override unless
  `--insecure` is given), `--insecure` builds a real unverified
  context, an SSL certificate error gets the actionable message, and a
  non-certificate `URLError` (e.g. DNS failure) correctly does not.


- **`examples/legacy/` removed — 8 of its 9 files were silently
  broken** — asked directly why the folder existed at all; checking
  before answering found that 8 of the 9 files crash immediately
  (`FileNotFoundError`/`ModuleNotFoundError`), not just outdated in
  content. The cause: each computed its own repo root as
  `Path(__file__).resolve().parents[1]`, correct while these files
  lived directly in `examples/`, but never updated to `parents[2]`
  when they were moved into `examples/legacy/` (one level deeper) —
  broken since that move, invisible because none of them are in the
  test suite. Since their stated purpose (showing the pre-proxy-API
  style for comparison) is already served, working and tested, by
  `docs/getting_started.md` and the per-example companion docs added
  earlier, 8 files were deleted outright rather than repaired.
  `example_import_tyndp.py` was the one genuine exception — it's a
  real dependency, not just a comparison artifact:
  `example_import_tyndp_proxy_api.py` imports its technology-
  classification functions and constants directly to stay faithful to
  the original's business rules. Moved back to `examples/` (its
  original location, which also correctly fixes its own
  `parents[1]` path bug as a side effect, since that calculation is
  only wrong one level deeper) instead of into the deleted folder;
  `example_import_tyndp_proxy_api.py`'s `sys.path` setup and comments
  updated to match, and `docs/importers/tyndp.md`/`examples/
  README_TYNDP_IMPORT_LOGIC.md`/the six other examples' own docstring
  mentions of `examples/legacy/` all updated or removed. Verified
  after the move: both TYNDP examples run correctly, the full test
  suite passes, and a complete link check across `README.md`, `docs/`,
  and `examples/` finds nothing broken.

### Changed

- **README's "Editor typings" section expanded with per-editor setup
  instructions** — asked directly whether VS Code/Sublime Text/PyCharm
  setup was documented; it wasn't — the previous single line
  ("picked up automatically via `[tool.pyright]`") is only actually
  true for Pyright-based editors, and PyCharm doesn't read that config
  section at all, so the same sentence was silently misleading for
  PyCharm users. Verified before writing anything: PyCharm's own
  documentation confirms marking a stub directory as a *Sources Root*
  is the officially recommended mechanism for external `.pyi` stubs;
  Sublime Text's LSP-pyright package runs the same underlying Pyright
  engine as VS Code's Pylance and reads the identical `[tool.pyright]`
  config the same automatic way. Added concrete, verified steps for
  all three editors.


- **`docs/illustrations/cesdm_architecture.svg` redesigned as a proper
  layered-architecture diagram** — the previous version (a linear
  data-flow diagram: external data → importers → CesdmModel → proxy
  API → Build/Explore/Validate/Transform → export formats) didn't
  actually show the architecture: it collapsed EAR and CESDM into one
  box, never showed the schema at all, and showed the proxy API as a
  pipeline step rather than a layer on top. Redesigned bottom-up:
  Schema (YAML) and the generic EAR Engine as the two complementary
  foundations (schema = data, engine = code that interprets it), the
  CESDM Domain Layer built on both (with Representation Views,
  Composite Builders, Import/Export Adapters, and — new — Analysis
  Validation as its four sub-parts), and the object-oriented Proxy API
  as an explicitly optional layer on top of that. Verified
  programmatically (no unexpected bounding-box overlaps, every text
  line's estimated rendered width checked against its containing
  box) and by rendering to PNG. Also embedded in the README for the
  first time — the file existed in the repository already but wasn't
  linked from anywhere, so nobody browsing the docs would ever have
  actually seen it.

### Added

- **Per-example step-by-step walkthrough docs, and a "why it matters"
  column in the README's examples table** — asked directly whether the
  README described why each example matters, and whether each example
  could get a step-by-step companion doc with source code (following
  the existing pattern of `README_AGENT_BASED_EXAMPLE.md`/
  `README_PYPSA_IMPORT_LOGIC.md`/`README_TYNDP_IMPORT_LOGIC.md`, which
  only covered 3 of the (now) 14 examples). Added the remaining 11:
  `README_IN_README_EXAMPLE.md`, `README_SIMPLE_EXAMPLE.md`,
  `README_MULTIENERGY_EXAMPLE.md`, `README_HYDRO_RESERVOIR_EXAMPLE.md`,
  `README_KUNDUR_TWO_AREA_EXAMPLE.md`, `README_CH_NEIGHBOURS_TUTORIAL.md`,
  `README_EXPLORE_MODEL_EXAMPLE.md`, `README_POWERFLOW_EXPORT_EXAMPLE.md`,
  `README_ANALYSIS_VALIDATION_EXAMPLE.md`,
  `README_EAR_GENERIC_DOMAIN_EXAMPLE.md`,
  `README_SCHEMA_EXTENSION_EXAMPLE.md` — all in `examples/`, linked
  from the README table. Every code snippet shown is copied from the
  actual current example source (not reconstructed from memory) and
  every printed output shown was captured by actually running the
  example, not assumed. `example_explore_cesdm_model.py`'s functions
  needed a small self-contained model to demonstrate against, since
  the script itself requires an external PyPSA-imported YAML file as
  input — documented as such rather than silently working around it.

- **Three new examples filling gaps found in a coverage review** —
  asked directly whether the examples covered EAR, CESDM, the proxy
  API, and general usage well; on review, three real gaps: zero
  coverage of `validate_for_analysis()`, no standalone example of the
  generic EAR engine outside the energy domain, and no worked example
  of extending the schema with a genuinely new entity type.
  - `examples/example_analysis_validation.py` — `validate_for_analysis`
    against `model.validate()`, plus what a schema-constraint violation
    actually looks like in practice. Confirmed directly, not assumed:
    setting an invalid enum value through the proxy API (`gas.dispatch.
    dispatch_type = "steerable"`) prints a warning immediately but does
    *not* raise or block the assignment — `model.validate()` is the
    authoritative, structured way to catch it afterward.
  - `examples/example_ear_generic_domain.py` — the same household/
    energy-community scenario `docs/guide/09_ear_toolbox.md` walks
    through in prose, as a complete runnable script using only
    `ear_toolbox` (no proxy API, no energy-specific helpers at all).
    Found while writing it: `validate_or_raise()` is CESDM-only and
    doesn't exist on a plain `ear.model.Model` — used the generic
    `validate()` pattern instead.
  - `examples/example_schema_extension.py` — adds a new
    `ElectricVehicleChargingStation` entity type via a schema extension
    (the same `extends:` mechanism `schemas_agentbased/` uses), with no
    core schema or Python changes. Found while designing it: the
    attribute name first chosen (`maximum_charging_power`) already
    existed in the core schema for something else — reused directly
    rather than redefined, and left in as an explicit illustration of
    "check whether an attribute already exists before adding a new one."
  - Cross-referenced from `docs/architecture/analysis_validation.md`,
    `docs/guide/09_ear_toolbox.md`, and `docs/guide/03_schemas.md`;
    added to the README's examples table.

### Fixed

- **Every example referenced in the README and `docs/` audited against
  what actually exists in `examples/`** — asked directly. Found:
  - `docs/importers/pandapower.md`, `docs/importers/matpower.md`,
    `docs/exporters/pandapower.md`, `docs/exporters/matpower.md` all
    referenced two files
    (`examples/example_pandapower_to_cesdm_to_matpower.py`,
    `examples/example_matpower_to_cesdm_to_pandapower.py`) that **do
    not exist anywhere in the repository**, plus a whole "IEEE
    case118 example" section describing IEEE 118-bus test-case
    functionality that was never actually built (confirmed with a
    repository-wide search for `case118` — zero matches anywhere).
    Fixed to reference the actual existing example
    (`examples/example_cesdm_to_pandapower_and_matpower.py`); the
    fictional case118 sections removed.
  - That same actual example file's own docstring told the reader to
    run a *different*, nonexistent filename
    (`python examples/example_matpower_to_cesdm_to_pandapower.py`) —
    a copy-paste mistake, fixed to reference itself correctly. The
    same mistake existed in `examples/legacy/
    example_cesdm_to_pandapower_and_matpower.py`'s own docstring;
    fixed there too.
  - `examples/test.py` — an unlisted, broken scratch file (a literal
    `SyntaxError`, an unclosed parenthesis) left over from earlier
    interactive debugging, not a real example and not referenced
    anywhere — removed.
  - Confirmed clean otherwise: every example the README's table and
    `docs/importers/`/`docs/exporters/` reference by name exists, and
    every `.py` file actually in `examples/` is referenced from
    somewhere in the README or `docs/`.

### Changed

- **`docs/simple/` + `docs/detailed/` (19 files, 5441 lines) consolidated
  into a single `docs/guide/` (13 files, 3618 lines)** — requested
  directly: with 12 tested, runnable examples plus the README already
  covering "how to build a model" thoroughly, keeping two separate
  tutorial tiers on the same ground was pure duplicated-maintenance
  risk, not reader value (this exact duplication is what let
  `schemas/prosumer`/`schemas_v4`/`cesdm_resources` — none of which
  exist anywhere in the repository — go unnoticed for as long as they
  did, see the entries below). Removed entirely: the two
  step-by-step "building a model" tutorials
  (`docs/simple/02_building_a_model.md`,
  `docs/detailed/07_building_models.md`) and
  `docs/detailed/04b_how_to_use_cesdm_schema.md` (an 80-call raw-API
  tutorial, same duplication), all already covered by the README and
  `examples/`; `docs/detailed/00a_executive_summary.md` (near-verbatim
  restatement of the README's own "What is CESDM?"). Merged: the
  plain-language `docs/simple/00_what_is_cesdm.md` and
  `docs/detailed/01_introduction.md` into one
  `docs/guide/01_what_is_cesdm.md` (fixing an `ElectricalElectricalBus`
  typo found while merging). Everything else kept and renumbered into
  one sequence — `docs/guide/00_disclaimer.md` through
  `docs/guide/10_cesdm_toolbox.md`, plus `faq.md`/`glossary.md`. Every
  cross-reference (README, `schema_governance.md`,
  `schemas/SCHEMA_MANIFEST.yaml`, and the guide files' own links to
  each other) updated and verified with a full automated link check,
  not just assumed correct.
- **All FlexECO-related documentation removed**
  (`docs/tyndp_flexeco_field_mapping.md`, added last turn, plus a
  passing mention in the spatial-aggregation guide) — FlexECO-specific
  Python tooling (`tools/import_flexeco.py`,
  `tools/cesdm_yaml_to_flexeco.py`,
  `tools/cesdm_frictionless_to_flexeco.py`) deliberately left alone,
  since removing working import/export code is a different, larger
  decision than a documentation cleanup.
- **`docs/illustrations/cesdm_architecture.svg` updated** to show the
  object-oriented proxy API as its own layer between `CesdmModel` and
  the Build/Explore/Validate/Transform operations — the previous
  version predated the proxy API entirely. Verified programmatically
  (no bounding-box overlaps) and by rendering to PNG.
- **`docs/architecture/proxy_api.md` trimmed further** — asked
  directly whether it still had unnecessary detail for an end user;
  on a second pass, yes: the `AssetProxy` class's actual Python source
  (`__new__` implementation), internal/private method names
  (`_discover_view_map`, `connect_single_port`, `class_attributes`,
  `create_generation_unit_from_technology`, ...), a specific internal
  schema file path, and design-rationale prose in the limitations
  section were all implementation detail a user calling
  `gen.dispatch.x = y` never needs. Rewritten to describe behaviour
  only; every code example re-verified by running it.

- **Documentation prepared for release, and `doc/`/`docs/` consolidated
  into a single `docs/`** — requested directly: developer-facing
  narrative ("bugs found while building this", session references)
  didn't belong in user documentation, and having both a `doc/`
  (Sphinx) and `docs/` (plain Markdown) folder was confusing.
  `docs/architecture/proxy_api.md` rewritten to a clean design
  reference with no development-journal content; `schema_governance.md`
  had a handful of "this session"/incident-narrative references
  removed, keeping the underlying rules. `CHANGELOG.md` itself
  condensed from ~1800 lines to under 1000 by rewriting the
  accumulated `[Unreleased]` section into concise, categorized
  bullets, since a changelog documents *what changed*, not the
  debugging process that found it.

  `doc/`'s Sphinx build machinery (`conf.py`, `Makefile`, `index.rst`,
  `requirements.txt`) was dropped — confirmed unused first: no CI
  workflow builds or publishes it, and the README's own docs badge
  linked to a GitHub Pages URL that doesn't resolve. Its Markdown
  content moved into `docs/simple/` and `docs/detailed/` (same
  filenames, same relative structure), `doc/illustrations/` into
  `docs/illustrations/`, and three small, closely related stray files
  (`flexeco_roundtrip_fixes.md`, `tyndp_flexeco_value_precedence.md`,
  `tyndp_hydro_dispatch_attributes.md`) merged into one
  `docs/tyndp_flexeco_field_mapping.md`. Every cross-reference
  (README, `schema_governance.md`, `schemas/SCHEMA_MANIFEST.yaml`, and
  the moved files' own relative links to each other) updated and
  verified to actually resolve, not just assumed — a full,
  programmatic link check across every `.md` file in `docs/` and the
  README found and fixed one broken cross-directory link along the way.

  While re-reading the moved files for the narrative cleanup, also
  found and fixed: two more files (`docs/detailed/05_representation_views.md`,
  `docs/detailed/04a_schemas.md`) still using the pre-rename
  dot-separated attribute ids (`MACHINE.xd`, `AVR.SEXS.Ka`) from
  earlier in this changelog; an invalid enum value in one of
  `05_representation_views.md`'s own examples (`MACHINE_model:
  "subtransient"`, not one of the schema's real allowed values); and,
  while first attempting the dot-to-underscore substitution, two
  self-inflicted mistakes (a class name corrupted to
  `ControllerView.AVR_SEXS`, and a file-path example's `.yaml`
  extension corrupted to `_yaml`) caught by rereading the diff rather
  than assuming the substitution had landed correctly, and fixed
  before they could ship.

### Added

- **Object-oriented proxy API** (`cesdm.proxy`) as the primary,
  recommended way to build models: `AssetProxy` (a `str` subclass
  returned by every builder function) with `.dispatch`/`.powerflow`/
  `.topology`/`.dynamic`/`.avr`/`.governor`/`.pss`/etc. resolving
  lazily to a `ViewProxy` via the schema's own `view_family` field —
  no hardcoded view-class list in Python. Unknown attributes/relations
  raise immediately with a spelling suggestion instead of silently
  doing nothing. `model.asset(id)` wraps an existing entity;
  `asset_as(id, SpecificProxyClass)` gives the concrete type for
  static type-checking. `gen.connect(bus)` /
  `line.connect(bus1, bus2)` wire topology relations directly. See
  `docs/architecture/proxy_api.md`.
- **Analysis-dependent validation**: `model.validate_for_analysis(profile)`
  / `model.validate_for_analysis_or_raise(profile)` check fitness for
  a specific analysis (e.g. "optimal dispatch needs
  `variable_operating_cost` on every generator") against a YAML
  profile (`analysis_profiles/*.yaml`), independent of what the schema
  itself marks `required:`. Checks are entity-centric — a check names
  an attribute/relation and CESDM resolves which view it lives on
  automatically; `view_family` can be given explicitly for the rare
  ambiguous case. Split across a generic, schema-agnostic core
  (`ear/model/analysis_validation.py`, works on any EAR-based schema)
  and a thin CESDM addon (`cesdm/domain/model/analysis_validation.py`)
  that adds the view-resolution capability. See
  `docs/architecture/analysis_validation.md`.
- **Real IEEE Std 1110-2002 / IEEE Std 421.5-2016 / Kundur / PSS/E
  Model Library reference default values** for 113 of the
  `MACHINE_*`/`AVR_*`/`GOV_*`/`PSS_*` dynamic-simulation attributes,
  applied automatically on entity creation through any construction
  path (builder function or raw `add_entity`), independent of the
  schema's own `required:` flag.
- **`view_family`**: a new optional, inheritable schema class field
  identifying which representation-view family a class belongs to
  (`dispatch`, `topology`, `powerflow`, `dynamic`, `avr`, `governor`,
  `pss`, `planning`, `spatial`, `technical`), replacing hardcoded
  Python view-family lists with schema-driven resolution.
- RDF/OWL schema export, a central unit registry with QUDT alignment
  (partial — see `docs/architecture/schema_governance.md`),
  `model.summary()`, `model.get_effective_attribute_value(...)`.
- `cesdm-update-generated` console command regenerating the default
  library, generated builders, and typings in one call.
- `examples/example_import_tyndp_proxy_api.py`: the full TYNDP import
  pipeline (nodes, installed capacities, hydro/PHS composites,
  storage, demand, time-series profiles, NTC interconnectors) ported
  to the proxy API, with synthetic fixtures so it runs standalone.
- `LICENSE` (MIT) and `.gitignore`.

### Changed

- **Every dot-separated attribute id in the `MACHINE`/`AVR`/`GOV`/`PSS`/
  HVDC families renamed to underscore-separated** (`MACHINE.xd` →
  `MACHINE_xd`, `AVR.SEXS.Ka` → `AVR_SEXS_Ka`) so these ids work as
  plain Python identifiers/kwargs directly. The family-prefix
  disambiguation this naming exists for (many controller models reuse
  the same short IEEE symbol) is unchanged; only the separator
  character is.
- **`cesdm/domain/model/builders.py` reorganized around one rule**: a
  function belongs there only if it does something a single generated
  `add_<EntityClass>()` call can't (multi-entity/multi-view composite
  construction, or real decision-making). Read-only query/lookup
  functions (`get_dispatch_view`, `views_for_asset`, ...) moved to
  `accessors.py`; a couple of thin, redundant aliases removed.
- **`GeneratorType`/`ControllerView.AVR/GOV/PSS` view-family
  disambiguation**: `Generator.DynamicView.Subtransient` and every
  `ControllerView.AVR.*`/`GOV.*`/`PSS.*` class used to share one
  `view_family: dynamic`, so `.dynamic` could resolve to an arbitrary
  controller instead of the machine model. AVR/GOV/PSS now have their
  own `view_family`, so `.dynamic`, `.avr`, `.governor`, `.pss` are
  each independently and unambiguously resolvable.
- Every example in `examples/` rewritten to use the object-oriented
  proxy API; pre-conversion versions kept in `examples/legacy/` for
  comparison. README, `docs/getting_started.md`, and the Sphinx
  documentation under `doc/` rewritten accordingly, leading with the
  proxy API as the primary, recommended way to build a model.
- `tools/generate_typings.py` extended to cover the full generated
  API surface (builder return types, view proxies, analysis
  validation, mixin sources) so editor type-checking matches runtime
  behaviour.

### Fixed

- Several silent bugs in `create_generation_unit_from_technology` and
  the family-specific generator builders: incorrect routing between
  wind/solar/thermal/nuclear technologies, a duplicate dict key that
  silently discarded 4 of 5 view-id mappings, and a non-canonical
  default fuel carrier id (`carrier.natural_gas` →
  `carrier.fuel.fossil.gas.natural_gas`) that created an orphaned,
  wrongly-attached entity.
- `HydroGenerationUnit.drawsFromReservoir` was incorrectly
  `required: true` (run-of-river units have no reservoir by
  definition) — reverted to `required: false`.
- `AssetProxy` had no `__setattr__`, so `bus.name = "X"` silently
  became an inert, ordinary Python instance attribute instead of
  setting the actual model attribute — now raises on unknown
  names, mirroring `ViewProxy`.
- Most functions in `builders.py` (`create_demand_unit`,
  `create_transmission_line`, family-specific generator builders, and
  others) returned the generic `AssetProxy` instead of the entity's
  actual, specific generated proxy class; a few
  (`ensure_carrier`/`ensure_resource`/`ensure_technology`,
  `create_timestamp_series`, `create_profile`) computed the correctly
  typed proxy internally and then discarded it for a bare id string.
  All now return the specific type, verified with Pyright.
- `export_yaml`/`export_json`/`export_long_csv` crashed
  (`FileNotFoundError`) when given a bare filename with no directory
  component; now handled correctly.
- Two carrier-classification bugs found by diffing importer behaviour
  against the canonical carrier registry (non-canonical ids reaching
  the model instead of their canonical equivalents).
- `Model.ensure_entity()` returned the raw internal `Entity` object
  instead of a typed proxy; `AssetProxy` values leaking into stored
  entity data instead of being coerced back to plain strings on write.
- A confirmed correctness bug in `ear.model.entity_ops.
  _get_entity_and_class`: given a nonexistent entity id, it silently
  returned a stale class reference instead of raising, producing
  misleading error messages unrelated to the actual problem.
- Sphinx documentation (`doc/simple/`, `doc/detailed/`) referenced two
  schema directories (`schemas/prosumer`, `schemas_v4`) and one Python
  module (`cesdm_resources`) that did not exist anywhere in the
  repository, and described an internal role-classification mechanism
  (hardcoded class-name frozensets) that had since been replaced by a
  purely structural derivation. Corrected throughout, with every code
  example re-verified by actually running it.
- `CESDM_Schema_Reference.html` was stale (pre-rename attribute ids)
  and baked the generating machine's absolute filesystem path into the
  committed output; regenerated, and the generator fixed to show the
  schema version instead.


## [0.8.0] — entity/attribute/relation naming and description audit

A systematic pass over all 114 classes, 393 attributes, and 71
relations (naming-convention conformance, fuzzy-match near-duplicate
detection, description-completeness and -accuracy checks) — see
conversation history for the full methodology and false-positive
analysis (most fuzzy-matched "near duplicates" turned out to be
correct, consistent structured naming — `active_power_output`/
`reactive_power_output`, `maximum_X`/`minimum_X` pairs, IEEE
`T1`/`T2`/`T3` sequences — not naming problems).

### Removed
- **`storage_technology_category`**: a dead attribute whose description
  confidently claimed to be *"the single source of truth for import/
  export tool routing decisions"* — but was never referenced by any
  class or any Python code. `storage_technology_type` (described more
  modestly) is what `tools/
  import_flexeco.py` actually uses in practice (4 real call sites).
  Left in place, the unused one — reading more authoritative — was a
  real trap for the next reader. Removed rather than "finished," since
  there's no evidence the planned migration it described was ever
  picked back up.

### Fixed
- **`variable_operating_cost`'s description undersold its real scope**:
  worded as if exclusively for demand ("the marginal operational cost
  associated with providing the demand... for loads, this often
  represents...") when it's actually declared on `Generation.
  DispatchView`, `HydroGenerationUnit.DispatchView`,
  `HVDCLink.DispatchView`, and `Storage.DispatchView` too — a genuinely
  correct, generic, cross-domain cost attribute, just inaccurately
  documented as demand-only.
- **`pumping_efficiency`'s description referenced `storage_technology_
  category`'s now-removed enum values** (`"phs_closed_loop and
  phs_open_loop categories"`) — repointed at the attribute that's
  actually live (`storage_technology_type` value `"phs"`).
- `tests/test_naming_audit_fixes.py`: regression coverage for all
  three (including a check that no class anywhere still declares the
  removed attribute, not just that the registry no longer has it).

### Added
- `docs/architecture/schema_governance.md`: new naming-convention
  bullet documenting the ~130 `AVR.*`/`GOV.*`/`PSS.*`/`HVDC.*`/
  `MACHINE.*` attributes that deliberately don't follow snake_case
  (they match their source IEEE/PSS-E standard's own symbol notation,
  e.g. `AVR.SEXS.Ka`, `MACHINE.Td0_prime`) and the dot-namespacing this
  requires (many controller models reuse the same short symbol, so the
  model-family prefix avoids id collisions) — this was previously true
  but undocumented, so it looked like unexplained inconsistency to
  anyone who didn't already know why. Also flags, honestly, that the
  `provenance_ref` citation practice modeled well by `AVR.SEXS.Ka`
  (PSS/E Model Library citation + governing equation in the
  description) is applied to only ~5 of the 130 — real, unfinished
  work, not silently left looking like an oversight. Not attempted to
  fill in here: doing so correctly needs access to the actual source
  standards, and a fabricated citation would be worse than none.

## [0.7.0] — schema-driven view_family (proxy API resolution no longer hardcoded)

### Added
- **`view_family` — a new optional, inheritable class field** in the
  schema (`ear/entity_class.py`, parsed like `abstract`/`description`).
  Declared once on a view family's abstract root
  (`schemas/views/dispatch/OperationalDispatchView.yaml:
  view_family: dispatch`, and 9 more — see
  `docs/schema_layout.md`, "`view_family` (optional class field)", for
  the full table) and inherited by every concrete subclass through the
  normal resolution machinery. Unlike `abstract`, this field is
  designed to inherit (a real "is-a" categorization, not something
  becoming a subclass invalidates) — `ear/model/schema_loading.py`
  resolves it the same way as attributes/relations: child's own
  declared value wins, otherwise the first parent's resolved value,
  processed in topological order so every parent is already resolved
  by the time a child needs it.
- `cesdm.proxy.AssetProxy` now resolves `.dispatch`/`.powerflow`/
  `.topology`/etc. entirely from this schema field — `cesdm/proxy.py`
  no longer contains any hardcoded list of view-family names at all.
  Adding a new view family that "just works" as a property now only
  requires tagging one YAML file, not touching Python — proven with a
  from-scratch scratch-schema test
  (`test_new_view_family_works_with_zero_python_changes`) that defines
  an `EconomicView` family cesdm/proxy.py has never heard of and shows
  `asset.economic.irr = 0.08` resolving correctly.
- Two distinct, explicit failure modes in `AssetProxy._view()`: a
  keyword that isn't a real view family at all falls through to the
  generic "not a view, attribute, or relation" error (with a spelling
  suggestion); a keyword that *is* a real family but has no matching
  view class for a particular asset's class raises a more specific
  error naming the valid view classes for that asset instead (e.g.
  `bus.dynamic` — `ElectricalBus` has no dynamic-simulation view).
- `tests/test_view_family.py` (28 tests): every root/leaf class pair
  from the table above, both error modes, the typo-suggestion path,
  and the from-scratch new-family proof.

### Fixed
- **`_merge_common()` silently dropped any top-level YAML key it didn't
  explicitly know about** — it only ever forwarded `("description",
  "parents", "abstract")` from the raw parsed dict before `view_family`
  was added to that list. Every one of the 10 `view_family:` tags
  above initially resolved to `None` everywhere, including on the very
  class where it was declared, until this was traced back to this one
  line. A schema author adding *any* new top-level class metadata key
  in the future would hit the identical silent-drop failure mode
  without this fix, or without remembering to extend the same tuple by
  hand.
- **`AssetProxy._view()` could resolve to an abstract view class**
  instead of a concrete subclass when both declared a `representsAsset`
  relation targeting the same asset class with the same `view_family`
  (an abstract root and its concrete child can both legitimately do
  this) — `_discover_view_map()` doesn't filter out abstract classes,
  and the previous candidate-matching logic picked whichever came
  first. Found via the from-scratch `EconomicView` test above (its
  abstract root and concrete `Thing.EconomicView` subclass both
  targeted `Thing`); `ensure_view` would then instantiate the abstract
  class directly, which is never correct. Fixed by filtering abstract
  candidates out of both the existing-views and new-view-creation
  matching paths.

### Added
- `examples/example_import_tyndp_proxy_api.py`: a second TYNDP
  importer, rebuilt on the `AssetProxy`/`ViewProxy` object-oriented API
  instead of raw `add_entity`/`add_relation`/`add_attribute` calls —
  a real-world showcase of the proxy API against genuine complexity
  (technology classification, hydro reservoir and pumped-hydro
  composite pairing, capacity accumulation across repeated imports),
  not just toy examples. Reuses `example_import_tyndp.py`'s own
  classification functions and constants (`TECH_HIERARCHY`,
  `TYNDP_TECH_DATA`, `_generation_asset_class_for_type`, ...) directly
  for fidelity — only the entity-construction style changes; not a
  byte-for-byte port of the full ~1800-line original (see that file's
  module docstring for exact scope).
- `examples/sample_data/tyndp_sample_installed_capacities.csv`: a
  small, realistic, TYNDP-column-shaped synthetic fixture (nuclear,
  thermal, wind, solar, battery storage, plain reservoir hydro,
  closed-loop pumped hydro across two nodes) so the new importer runs
  and validates standalone, without needing the external TYNDP
  reference dataset.
- `tests/test_tyndp_proxy_api_importer.py` (10 tests): full pipeline
  validates against the schema; correct techno-economic defaults per
  technology; correct hydro reservoir/PHS composite wiring
  (`drawsFromReservoir`/`suppliesResourceTo`, machine_role
  reversible-vs-turbine); capacity accumulates correctly across
  repeated imports of the same source data.

### Fixed
- **`ear.model.entity_ops._get_entity_and_class`**: given a
  nonexistent entity id, silently returned `(None,
  self.classes[<cname>])` where `cname` was a *stale for-loop
  variable* left over from the failed search — not the actual entity's
  class (there wasn't one), but whichever class happened to be last in
  `self.entities`' iteration order. Every caller (`add_attribute`,
  `add_relation`) would then report a wildly misleading `"Unknown
  attribute/relation of <unrelated random class>"` error with no
  connection to the real problem. There was even dead code right below
  the buggy `return` (an unreachable `print(...)` and a commented-out
  `raise KeyError(...)`) showing a proper fix had been intended but
  never actually took effect. Found while building the TYNDP proxy-API
  importer above — a missing prerequisite entity
  (`domain.electricity`) produced an error blaming
  `TwoPort.TopologyView`, a completely unrelated class, before this
  was traced back to its real cause. Now raises a clear `KeyError`
  naming the actual missing entity id.
- `add_reservoir_storage`, `add_reservoir_hydro`, `add_phs_closed_loop`,
  `add_phs_open_loop` now also return `AssetProxy` (the last four
  high-level builders from the original proxy-API pass that were still
  returning plain strings) — same zero-risk change as the rest (`str`
  subclass), needed for the new TYNDP importer above to use the
  object-oriented API consistently for hydro composites too.
- **Test-collection failure with no editable install, environment-
  and collection-order-dependent**: reported by a user running `pytest`
  directly after unzipping (no `pip install -e .`) — exactly
  `tests/test_abstract_resolution.py`, `test_attribute_semantics.py`,
  and `test_generation_technology_routing.py` failed with
  `ModuleNotFoundError: No module named 'cesdm_toolbox'`, while ~150
  other test items collected fine. Root cause: `tests/
  test_hvdc_schema.py` (pre-existing) does its own `sys.path.insert(...)`
  as an import-time side effect, which persists in `sys.path` for the
  rest of the same pytest process — so every test file collected
  *after* it alphabetically benefited from that fix, while the three
  collected *before* "hvdc" (alphabetically) and lacking their own fix
  failed. Reproduced exactly (ran just those 3 files, then the full
  suite, both with no install) before fixing, and re-verified after.
  Fixed with a single `conftest.py` at the repo root, which pytest
  imports unconditionally before collecting *any* test file regardless
  of alphabetical order — the standard, robust solution, replacing the
  fragile "whichever file happens to be collected first must fix
  sys.path for everyone" situation entirely.
- `tests/test_pypsa_default_library_mapping.py`: a missing `numpy`
  (an optional dependency, not installed by default) caused a hard
  collection *error* that aborted collecting every other test file in
  the run (`Interrupted: N errors during collection`), not just a
  skip of that one file. Added `pytest.importorskip("numpy")` so it
  degrades to a graceful per-file skip instead.

_Note: the proxy API and generation-technology-routing bugfix entries
below were originally Python/toolbox-only changes with no schema YAML
changes of their own, so they didn't warrant their own version bump at
the time. They ended up bundled into 0.7.0 together with the
view_family schema change above them in this file, once that shipped —
not because they touch the schema themselves._

### Added
- `cesdm/proxy.py`: `AssetProxy` and `ViewProxy` — an object-oriented
  ergonomics layer over the existing low-level EAR API, in response to
  a detailed API-design proposal. `AssetProxy` is a `str` **subclass**,
  so it's usable anywhere a plain entity id was already accepted (dict
  keys, `==`, passed to any existing `model.*` method) — making every
  builder that now returns one instead of a bare string a
  zero-risk, 100%-backward-compatible change. Verified against the
  full existing test suite and every example script with no changes
  needed elsewhere.
  - `asset.dispatch` / `.powerflow` / `.dynamic` / `.topology` /
    `.planning` / `.spatial` / `.technical` / `.results` resolve to a
    `ViewProxy` for the matching representation view, created lazily
    via the schema's own `representsAsset` relationships
    (`model._discover_view_map()`) if it doesn't exist yet.
  - `ViewProxy` attribute get/set is validated against the view
    class's real attributes/relations; an unknown name raises
    immediately with a `difflib.get_close_matches` spelling
    suggestion, instead of silently doing nothing.
  - Setting a plain scalar auto-attaches the attribute's unit from
    `schemas/units/units.yaml` only when the attribute has exactly one
    registered valid unit; ambiguous attributes (e.g. `reservoir_volume`,
    which legitimately accepts GWh/TWh/hm3/m3) are left unit-less
    rather than guessed.
  - `asset.connect(bus)` (single-port) / `asset.connect(bus1, bus2)`
    (two-port) wrap `connect_single_port`/`connect_two_port`.
- `model.add_generator(id=, technology=, bus=, ...)`: clean top-level
  entry point wrapping `create_generation_unit_from_technology`, returning
  an `AssetProxy`.
- `model.asset(entity_id)`: wrap an already-existing entity (created
  via the low-level API, or an untouched builder) in an `AssetProxy`
  after the fact.
- `docs/architecture/proxy_api.md`: full design writeup, including
  what's deliberately *not* built yet (fluent method-chaining,
  `gen.static.*` metadata with no schema home yet, short
  library-hiding technology strings, importer/exporter renames,
  `model.summary()`/`model.find()`) — see the conversation history for
  the full 10-point proposal this responds to.
- `tests/test_proxy_api.py` (14 tests) and
  `tests/test_generation_technology_routing.py` (7 tests).

### Fixed
- **Three related, silent bugs in `create_generation_unit_from_technology`**,
  all found by hand-testing the closest existing analog to "smart
  defaults from technology" before designing the proxy layer above:
  1. Every non-hydro generation technology (wind, solar, thermal,
     nuclear) silently routed through `add_solar_generator()`
     regardless of what was requested. Root cause:
     `generation_asset_class_from_technology()` correctly returns the
     same CESDM entity class (`"GenerationUnit"`) for all four — the
     schema deliberately has no separate subclasses for them — but the
     routing code compared against that value across four separate
     `if cls == "GenerationUnit":` branches, so only the first was
     ever reachable. Fixed with a new, separate
     `_generator_family_from_technology()` classifier used only for
     builder routing, with no schema meaning of its own.
  2. `_view_id()`'s id-prefix dict had 5 entries for the literal key
     `"Generation.DispatchView"` (one intended per technology family);
     dict literals silently let later duplicate keys win, so every
     non-hydro generator's auto-generated view id claimed to be
     `"solar_dispatch_view"` regardless of its real technology.
     Collapsed to one entry, since the view class genuinely is shared
     across these technologies (only hydro has its own dispatch-view
     class).
  3. The thermal branch always passed
     `fuel_carrier_id=input_carrier_id` (`None` unless the caller
     explicitly supplied one), clobbering `add_thermal_generator`'s
     own sensible default (`"carrier.natural_gas"`) every time it was
     reached through the technology-routing entry point.
  - `dispatch_view_class_for_asset()` had the same duplicate-key/
    duplicate-branch pattern (5x `"GenerationUnit"` dict key, repeated
    identical `if` conditions) — harmless here since every duplicate
    mapped to the same value, but cleaned up as the same class of
    copy-paste residue as bugs 1-2 above.

## [0.6.0] — QUDT unit alignment (partial) and RDF/OWL schema export

### Added
- `qudt_iri` and `qudt_status` fields on every entry in `schemas/units/
  units.yaml`. `qudt_status` is one of `verified` (checked against the
  live QUDT vocabulary — currently `MW`→`unit:MegaW`,
  `MWh`→`unit:MegaW-HR`, `kV`→`unit:KiloV`, `kW`→`unit:KiloW`, 4 of
  47), `unverified` (plausibly has a QUDT equivalent, not yet checked
  — most of the 47), or `no_qudt_equivalent` (`date`, `Timestamp / time
  index` — definitionally outside QUDT's scope). Deliberately not a
  complete mapping: pattern-guessing the remaining unverified IRIs
  would produce a mapping that *looks* authoritative while potentially
  being wrong, which is worse than leaving them honestly unmapped.
- `CesdmModel.export_rdf_schema(path, namespace=None)`
  (`cesdm/domain/model/rdf_export.py`): exports the loaded schema
  (classes, attributes, relations — not instance data) as an OWL
  ontology in Turtle syntax. Classes → `owl:Class` with
  `rdfs:subClassOf` from the inheritance graph; relations →
  `owl:ObjectProperty`; attributes → `owl:DatatypeProperty`, with a
  `cesdm:hasUnit` annotation pointing at the real QUDT IRI when an
  attribute has exactly one registered unit and that unit's
  `qudt_status` is `verified`. Pure string generation — no new runtime
  dependency for the export itself.
- **The export namespace (`CESDM_ONTOLOGY_NAMESPACE`) is explicitly
  provisional**, using the project's existing published GitHub Pages
  docs URL as a placeholder rather than inventing a new one. Minting a
  permanent identifier is a decision for the schema's maintainers, not
  something to decide unilaterally; re-basing later is a one-constant
  change.
- `tests/test_rdf_export.py`: validates the generated Turtle actually
  *parses* (via `rdflib`, `pytest.importorskip`'d), not just that
  something was written — checks class/property counts match the
  loaded schema exactly, `rdfs:subClassOf` edges match the inheritance
  graph (including a dot-namespaced class name, to prove the
  full-IRI-not-prefixed-name approach sidesteps Turtle's PN_LOCAL
  restrictions), the verified QUDT annotation is present where
  expected, and absent for multi-unit/unverified attributes.
- `rdf` and `pydantic` extras in `pyproject.toml` (the latter was
  already a working lazy-imported optional dependency for
  `build_pydantic_models()`; formalized here for discoverability).
- `docs/architecture/schema_governance.md`: new "Formal ontology
  alignment (partial)" section documenting both limitations above
  explicitly, replacing the old "No RDF/OWL alignment yet" non-goal.

## [0.5.0] — central unit registry

### Added
- `schemas/units/units.yaml`: the single source of truth for every
  unit used anywhere in the schema tree — the structural fix for "unit
  spellings are canonical today, but nothing stops the next
  contributor from introducing a new inconsistent spelling tomorrow"
  (the exact problem the 51→47-string cleanup earlier in this file had
  to fix by hand). Same registry-folder pattern as `attributes/` and
  `relations/` (auto-discovered, no `_index.yaml`). Each of the 47
  entries has a `symbol`, a `quantity_kind` (informational dimensional
  tag — `power`, `energy`, `angle`, `cost_rate`, ... — not currently
  used for automated dimensional-consistency checking), and a
  `description`.
- `load_classes_from_yaml` now validates every attribute's
  `unit.constraints.enum` values against this registry at load time:
  an attribute referencing an unregistered unit string fails to load
  immediately with a clear error, rather than silently introducing
  drift. Verified with a negative test that deliberately introduces an
  unregistered unit and confirms the load fails.
- `Model.unit_info(symbol)`: look up a unit's registry entry from code.
- `tests/test_unit_registry.py`: regression coverage (registry loads,
  every existing attribute's units are registered, the enforcement
  actually fires on a bad unit, `units.yaml` itself is correctly
  excluded from entity-class scanning).
- `docs/architecture/schema_governance.md`: new "Central unit
  registry" section; updated the "Unit strings must be spelled
  consistently" naming-convention bullet (now enforced, not just
  documented) and removed the now-resolved "no central unit registry
  yet" non-goal.

### Fixed
- **Stray top-level `constraints:` keys, silently ignored by the
  loader** (constraints are only read from `value.constraints` or
  `unit.constraints` — see `ear/attribute_def.py`): found on 7
  attributes. Five (`initial_state_of_charge`, `maximum_state_of_charge`,
  `minimum_state_of_charge`, `discount_rate`, `salvage_fraction_value`)
  had a genuinely-intended `maximum: 1.0` bound trapped there that had
  therefore **never actually been enforced** — moved into
  `value.constraints` so it's real now. `maximum_state_of_charge` had
  its entire description trapped there too (moved to a proper
  `description:` key). The other two (`fixed_operating_cost`,
  `investment_cost`) were pure dead duplicates of already-correct
  content a few lines below (their unit enum) — removed. Also fixed
  `salvage_fraction_value`'s stray block containing a typo
  (`minnimum`) that made the dead content even harder to notice was
  dead. `tests/test_attribute_semantics.py`
  guards against this pattern recurring anywhere in either schema tree.
- **3 attributes with no description at all**: `maximum_state_of_charge`
  (recovered from the stray `constraints:` key above),
  `converter_rating_from`/`converter_rating_to` (recovered from
  `HVDC.converter_rating_from`/`HVDC.converter_rating_to` — orphaned
  near-duplicates with the correct description text but never actually
  referenced by any class; deleted after transplanting their text into
  the live, referenced attributes). `test_every_attribute_has_a_
  description` guards against this recurring.
- **Two categorical string attributes now have real closed enums**:
  `carrier_group` (`electricity`/`gas`/`heat`/`hydrogen`/`water`,
  mirroring CESDM's own fixed set of per-carrier Bus node types) and
  `resource_group` (`renewable`/`hydro`/`geothermal`/`environmental`,
  exactly matching what its own description already stated). Both were
  previously unconstrained free strings.
- **Five other categorical string attributes documented as
  intentionally open, not force-enumerated**: `carrier_type`,
  `generator_technology_type`, `resource_type`, `storage_technology_type`
  each got a recommended-vocabulary description instead of a hard
  `enum:` — checked `storage_technology_type` against its actual
  consumer (`tools/import_flexeco.py`) first and confirmed it's used
  as a soft pass-through string, not matched against a fixed set, so a
  hard enum would have risked rejecting values the code already
  handles correctly. `demand_type` was left honestly flagged as
  too ambiguous to document a vocabulary for in good faith (zero usage
  evidence anywhere in this toolbox to disambiguate sector-based vs.
  flexibility-based classification) rather than guessing.
  `solver_status`'s pre-existing enum (the one categorical attribute
  that already had one) was restyled from a shorthand `value.enum`
  form to the dominant `value.constraints.enum` form used everywhere
  else, for consistency — both forms are parsed identically, so this
  is style-only.
- `docs/architecture/schema_governance.md`: new "Attribute and relation
  naming conventions" section codifying the unit-suffix, unit-spelling,
  comma-crammed-enum, categorical-vocabulary, and stray-top-level-
  constraints rules, plus a
  central-unit-registry non-goal noting the residual risk that remains
  even after this pass (nothing yet stops a *new* spelling variant).

- **Unit-string vocabulary inconsistency**: the schema has no central
  unit registry — every attribute declares its own free-text
  `unit.constraints.enum` — and the same physical unit had drifted
  into multiple incompatible spellings across 360 attributes:
  - `pu` / `p.u.` (per-unit) → canonicalized to `pu` (the pre-existing,
    ~60-attribute-strong spelling).
  - `deg` / `degree` / `degrees` / `decimal degrees` (angle) → `deg`.
  - `percent` / `%` (percentage) → `%`.
  - `Fraction` / `Fraction (0-1)` / `Fraction 0-1` / `-` (dimensionless
    0-1 ratio) → `fraction`.
  - `tCO2/MWh` / `tCO2_per_MWh` (CO2 intensity) → `tCO2/MWh` (matching
    the slash-notation convention used everywhere else in the registry:
    `MU/MWh`, `CHF/tCO2`, `MWh/year`, ...).
  - `investment_cost` and `fixed_operating_cost`: their unit enum was a
    single comma-separated string (`"MU/kW, MU/MW, MU/unit"`) instead
    of a proper list of three enum values — split correctly.
  - `maximum_downward_adjustment`/`maximum_upward_adjustment`: same
    comma-crammed-string bug (`"kW / MW"`) — split into `[kW, MW]`.
  - `flexibility_time_resolution`: fixed a typo baked into the unit
    string itself (`"Houes / minutes"` → `[h, min]`).
  - `conversion_rules`: had `unit.constraints.enum: [List]` — not a
    unit at all, describes the value's data shape, which `value.type`
    already captures. Removed the (incorrect) `unit:` block entirely.
  - `tests/test_unit_vocabulary_consistency.py`: regression coverage
    guarding against these specific spellings reappearing, plus a
    general check that no unit enum value contains a comma.
- **Naming-convention inconsistency in the power-flow/dynamics result
  attributes**: they embedded
  their unit as a suffix in the attribute id itself (`active_power_
  flow_from_mw`, `voltage_magnitude_pu`, ...) — inconsistent with the
  dominant pre-existing convention of keeping the unit solely in the
  separate `unit:` field (`nominal_power_capacity`, `reactive_power_
  demand`, ...). Renamed 18 attributes to drop the suffix and match the
  dominant convention: `active_power_flow_from`, `reactive_power_flow_
  from`, `active_power_flow_to`, `reactive_power_flow_to`, `active_
  power_loss`, `reactive_power_loss`, `active_power_output`, `reactive_
  power_output`, `voltage_magnitude`, `average_voltage_magnitude`,
  `min_voltage_magnitude`, `max_voltage_magnitude`, `max_speed_
  deviation`, `current_magnitude`, `voltage_angle`, `max_rotor_angle_
  deviation`. Two (`active_power_injection_mw`, `reactive_power_
  injection_mvar`) were renamed to `net_active_power_injection` /
  `net_reactive_power_injection` instead of reusing the pre-existing
  bare `active_power_injection`/`reactive_power_injection` ids, since
  those are genuinely shunt-specific (MATPOWER Gs/Bs and pandapower
  sign-convention semantics baked into their description) rather than
  a generic bus-injection concept — verified before reusing rather
  than assumed.
- **Cross-tree attribute/relation duplication** (the same DRY issue
  already fixed for classes via `extends`, never applied to the
  registries): `schemas_agentbased/attributes/attributes.yaml` and
  `schemas_agentbased/relations/relations.yaml` independently
  redeclared 34 attributes and 10 relations already defined in the
  core `schemas/` registries — all verified byte-identical (after
  whitespace normalization) except 5 that had drifted to a stale unit
  spelling the unit-canonicalization above just fixed in the core copy
  only, which surfaced as a real `ValueError: Duplicate attribute id
  ... with different definitions` when loading both trees together.
  Removed all 44 duplicate blocks from the agent-based registries;
  they're already available via `extends: [../schemas]`. Verified
  `build_model_from_yaml("schemas_agentbased")` alone and
  `build_model_from_yaml(["schemas", "schemas_agentbased"])` still
  produce identical 114-class models.
- Investigated but **left alone**: `nominal_power_capacity` vs.
  `rated_electrical_power_capacity` vs. `supply_capacity` vs.
  `thermal_capacity` vs. `thermal_capacity_rating` looked like a
  cluster of near-synonymous "capacity" attributes. Checked which
  classes declare each: they're scoped to different roles (general
  dispatch capacity, a `ConverterType` technology-template rating, an
  external-supply boundary condition, nuclear thermal vs. electrical
  output, and a transmission branch's MVA rating respectively) — a
  defensible, if not optimally named, set of distinct concepts rather
  than true duplication. Not merged.

- **Severe pre-existing bug in `resolve_inheritance()`**: `abstract` was
  incorrectly propagated from a parent class to every descendant, no
  matter how many inheritance levels down. Since nearly every class in
  the tree eventually traces back to an abstract root
  (`SemanticEntity`, `EnergyAssetInstance`, ...), this meant **all 103
  classes** resolved to `abstract=True` after loading — including
  plain concrete leaf classes like `GenerationUnit` and `ElectricalBus`.
  Being a subclass of an abstract base does not make the subclass
  abstract; that is the entire point of an abstract base class.
  - **Real, silent impact**: `build_pydantic_models()` only registers a
    class in `self.py_models` when `not c.abstract` — so `py_models`
    was always empty, for every class, with no error raised. Verified
    broken before the fix, verified fixed after (see
    `tests/test_abstract_resolution.py`).
  - A previous developer had already independently discovered and
    worked around this exact bug in `cesdm/domain/model/frictionless.py`
    (~40 lines re-deriving "directly abstract" by re-parsing raw YAML
    or a parents-graph heuristic, with a comment explaining why
    `cdef.abstract` couldn't be trusted) — but the workaround was never
    applied at the root cause, so every other consumer of `.abstract`
    stayed silently broken independently. Removed the workaround now
    that `cdef.abstract` is directly correct.
  - Found via `tools/schema_audit.py` (see "Added" below): the
    "orphaned classes" check initially reported 0 findings across 103
    classes, which was itself the tell — every class being (wrongly)
    abstract meant the orphan-detection logic was skipping all of them.
  - Only 20 of 103 classes are genuinely abstract after the fix — a
    plausible number for actual abstract bases (`SemanticEntity`,
    `EnergyAssetInstance`, `RepresentationView`, `ResultView`,
    `RunRecord`, the `ControllerView` family roots, ...).

### Added
- `tools/schema_audit.py`: static-analysis tool that cross-references
  the schema tree (declared relations/attributes, class hierarchy,
  `SCHEMA_MANIFEST.yaml` stability tiers) against actual usage in
  `examples/`, `tests/`, `tools/`, and the `ear`/`cesdm` library source,
  producing `docs/architecture/schema_audit_report.md`. Surfaces: dead
  relations/attributes, orphaned (never-instantiated) concrete classes,
  relations declared on an over-broad base class (the
  `StorageUnit.storesResource` pattern, generalized into a repeatable
  check), and `stable`-tier classes with zero usage evidence. Not a
  sound analysis — literal-argument AST scan only — see the tool's own
  docstring and the documented `hasInputResource` false positive before
  acting on any finding.
- `tests/test_abstract_resolution.py`: regression coverage for the
  fix above.

- `SCHEMA_MANIFEST.yaml` in `schemas/` and `schemas_agentbased/`:
  formalizes a version number and a per-family stability tier
  (`stable` / `experimental` / `deprecated`) for the schema tree.
  Read by `ear.schema_manifest.SchemaManifest`.
- `_cesdm_meta.schema_version` header written by
  `export_yaml_hierarchical`; `import_yaml_hierarchical` now warns
  (does not fail) if a model is imported against a schema tree with a
  different major version.
- `docs/architecture/schema_governance.md`: versioning policy,
  stability-tier definitions, and the change-proposal process for
  schema edits.
- `docs/architecture/package_layout.md`: documents the split of
  `ear_toolbox.py` / `cesdm_toolbox.py` into the `ear`/`cesdm`
  packages.
- `tests/test_schema_filenames_match_class_names.py`: enforces that
  every schema file's filename matches its declared `name:` field, so
  the mismatches described below can't silently recur.
- `SchemaManifest.extends`: a schema tree can declare
  `extends: [../schemas]` to depend on and auto-load another schema
  tree, instead of forking its classes. See "Removed" below and
  `docs/schema_layout.md` ("Cross-tree dependencies").
- Registry-folder consistency check in `load_classes_from_yaml`:
  `attributes/` and `relations/` folders now fail fast (`ValueError`)
  if they contain a `*.yaml` file that isn't listed in that folder's
  `_index.yaml`, instead of silently ignoring it. Covered by
  `tests/test_registry_index_consistency.py`.

### Changed
- `cesdm.domain.model.discovery._build_view_index` now iterates
  view classes in sorted order instead of raw `frozenset` order. This
  is a **behavior fix, not a schema change**: the previous ordering
  depended on Python's per-process string-hash randomization, so the
  key order of `representations:` blocks in hierarchical YAML exports
  could vary between runs of the *same* model. Data/content is
  unaffected; only serialization order is now deterministic.
- Renamed 22 files under `schemas/views/{dispatch,dynamics,powerflow,
  technical,topology}/` to match their declared `name:` field (e.g.
  `HydroReservoirDispatchView.yaml` → `ReservoirStorageUnit.DispatchView.yaml`,
  `NodalConnectionView.yaml` → `SinglePort.TopologyView.yaml`). No class
  identity, inheritance, or loaded-model behavior changed — this is a
  filename-only fix for grep-ability; see `docs/schema_layout.md`.
- Nested `schemas/controllers/*.yaml` into `AVR/`, `GOV/`, and `PSS/`
  subdirectories by controller family, consistent with how `views/` is
  already subdivided by analysis domain. `ControllerView.yaml` (the
  family-less abstract base) stays at `controllers/` root. No class
  identity or loaded-model behavior changed — the loader scans the
  schema tree recursively regardless of nesting depth.

### Removed
- `schemas_agentbased/assets/_index.yaml`: referenced non-existent
  subdirectories (`Agents/`, `Assets/`, `Representations/`) and files
  (`DemandAsset.yaml`, `StorageAsset.yaml`, `SupplyAsset.yaml`) that
  don't exist anywhere in the repository, and listed one file three
  times. It was also never actually read by the loader — only
  `attributes/_index.yaml` and `relations/_index.yaml` are consulted
  (see `ear/model/schema_loading.py`) — so it was pure stale
  documentation actively describing a layout that no longer (or never
  did) match reality. Deleted rather than fixed, since a corrected
  version would still be dead weight.
- 8 duplicate class files from `schemas_agentbased/`
  (`assets/EnergyAssetInstance.yaml`, `core/SystemAsset.yaml`,
  `core/SemanticEntity.yaml`, `carrier/EnergyCarrier.yaml`,
  `carrier/NaturalResource.yaml`, `profiles/Profile.yaml`,
  `profiles/TimestampSeries.yaml`, `system/GeographicalRegion.yaml`;
  the emptied `core/`, `carrier/`, `profiles/`, `system/`
  subdirectories were also removed). 7 were byte-identical copies of
  the corresponding file in `schemas/`; `core/SemanticEntity.yaml` had
  already drifted (reworded description, same meaning). They existed
  only so `schemas_agentbased/` could be loaded standalone; that
  capability is now provided by `extends: [../schemas]` in
  `schemas_agentbased/SCHEMA_MANIFEST.yaml` instead, with a single
  source of truth for the shared classes. Verified that
  `build_model_from_yaml("schemas_agentbased")` alone and
  `build_model_from_yaml(["schemas", "schemas_agentbased"])` (as
  `examples/example_agent_based_prosumer_model.py` already did) now
  produce identical 104-class models.
- The `_index.yaml`-based curated file-list mechanism for the
  `attributes/` and `relations/` registry folders. These two folders
  are now auto-discovered the same way every other schema folder is
  (every `*.yaml` file present is picked up, no registration step).
  The ordering `_index.yaml`'s `imports:` list provided was never
  functionally meaningful — a duplicate registry id across files was
  always a hard error, never "last file wins" — so requiring a second,
  separately-maintained file added drift risk (exactly what happened
  to `schemas_agentbased/assets/_index.yaml`, see 0.1.0 entry below)
  for no real benefit. The one property that did matter — a registry
  id must not be defined twice with conflicting specs — is still
  enforced by `ear.model.schema_loading._load_registry_from_folder`.
  Deleted `schemas/attributes/_index.yaml`,
  `schemas/relations/_index.yaml`,
  `schemas_agentbased/attributes/_index.yaml`,
  `schemas_agentbased/relations/_index.yaml`.
  `tests/test_registry_index_consistency.py` (which tested the removed
  fail-fast behavior) replaced by `tests/test_registry_auto_discovery.py`.

## [0.4.0] — reverted

Briefly narrowed `StorageUnit.storesResource` to `ReservoirStorageUnit`
only (see rationale that was here). Reverted at the requester's
direction before this version was ever released — `StorageUnit` and
`ReservoirStorageUnit` are back to their `0.3.0` state, both declaring
`storesCarrier` and `storesResource`. Noted here rather than silently
deleted so the reasoning isn't accidentally re-proposed unaware it was
already considered: the concern was real (every non-reservoir
`StorageUnit` instance inherits an optional relation it never uses),
but was judged not worth the breaking change to a `stable`-tier class
for now.

## [0.3.0] — standard power-flow result coverage

### Added
- `ElectricalBus.PowerFlowResultView`: `voltage_angle_deg`,
  `active_power_injection_mw`, `reactive_power_injection_mvar` (in
  addition to the existing `voltage_magnitude_pu`/average/min/max).
  `hasVoltageAngleProfile` relation.
- `TransmissionElement.PowerFlowResultView`: `active_power_flow_from_mw`,
  `reactive_power_flow_from_mvar`, `active_power_flow_to_mw`,
  `reactive_power_flow_to_mvar` (flow differs at each end due to
  losses/charging, hence separate from/to values), `active_power_loss_mw`,
  `reactive_power_loss_mvar`, `current_magnitude_ka`, plain
  `loading_percent` (alongside the existing average/max). Attribute
  names anchored to this toolbox's own pandapower integration's
  `res_line`/`res_trafo` result-table convention
  (`vm_pu`/`va_degree`/`p_from_mw`/... in pandapower) rather than
  invented independently. `hasActivePowerLossProfile` relation.
- `schemas/views/results/powerflow/GenerationUnit.PowerFlowResultView.yaml`
  (new leaf class): `active_power_output_mw`, `reactive_power_output_mvar`
  — the power-flow-solved generator output (reactive power at a PV bus,
  and active power at the slack bus, are solved by the power flow, not
  given as input, unlike at a plain PQ-dispatched generator).
  `hasActivePowerOutputProfile`/`hasReactivePowerOutputProfile` relations.
- `PowerFlowRunRecord.hasTimestampSeries` (optional, unlike
  `DispatchRunRecord`'s required one): its presence/absence is now the
  explicit signal for whether a power-flow run is a single-snapshot
  solve or a time-series ("quasi-steady-state") study — see "Changed"
  below.

### Changed
- **Made the single-snapshot vs. time-series distinction explicit**
  for power-flow results, rather than leaving both cases folded into
  one ambiguous attribute set. Previously
  `ElectricalBus.PowerFlowResultView` only had `average/min/max`
  attributes, which are meaningless for the single-snapshot case (the
  most common kind of power-flow study, and what this toolbox's own
  pandapower/MATPOWER integrations solve via one `runpp()`/`PYPOWER`
  call). Every power-flow result view now has plain snapshot-value
  attributes (`voltage_magnitude_pu`, `loading_percent`, ...) that are
  always the primary values; the average/min/max attributes and
  Profile relations are populated only when the producing
  `PowerFlowRunRecord.hasTimestampSeries` is set.

All additions are optional attributes/relations and one new leaf
class — purely additive, no renames or removals — hence a MINOR bump
rather than the MAJOR a breaking change would need.

## [0.2.0] — result-view restructuring

### Added
- `schemas/system/RunRecord.yaml`: abstract provenance base, analogous
  to `EnergyAssetInstance` for assets. `DispatchRunRecord` (existing,
  re-parented), `PowerFlowRunRecord`, and `DynamicRunRecord` (both new)
  are its concrete subclasses. `RunRecord.hasInputRun` links a run to
  the upstream run whose output it used as input, making chained
  multi-stage workflows (dispatch → power-flow → dynamics)
  traversable end-to-end.
- `schemas/views/results/ResultView.yaml`: abstract base shared by all
  result-view families, declaring `hasRunRecord` (a real relation,
  target `RunRecord`) so result views from different runs — and
  different analysis domains — can coexist on the same asset. Each
  domain's abstract result-view base narrows `hasRunRecord`'s target
  to its own `RunRecord` subclass.
- `schemas/views/results/powerflow/`: `PowerFlowResultView` (abstract),
  `ElectricalBus.PowerFlowResultView` (voltage magnitude outcomes),
  `TransmissionElement.PowerFlowResultView` (loading and losses,
  covers TransmissionLine/Transformer/Interconnector).
- `schemas/views/results/dynamics/`: `DynamicResultView` (abstract),
  `Generator.DynamicResultView` (rotor-angle/speed-deviation outcomes
  of a transient stability or contingency simulation).
- `hasRunRecord`, `hasInputRun`, `hasVoltageMagnitudeProfile`,
  `hasLoadingProfile`, `hasRotorAngleProfile`, `hasSpeedDeviationProfile`
  relations; `schemas/attributes/results.yaml` (new modular attribute
  file, registered in `attributes/_index.yaml`) for the power-flow and
  dynamics run/result attributes.
- `tests/test_view_only_asset_export.py`: regression coverage for the
  export bug described below.
- New per-domain stability entries `views/results/dispatch`,
  `views/results/powerflow`, `views/results/dynamics` (all
  `experimental`) in `SCHEMA_MANIFEST.yaml`, replacing the single
  flat `views/results` entry.

### Changed
- **`schemas/views/results/` is now subdivided by analysis domain**
  (`dispatch/`, `powerflow/`, `dynamics/`), mirroring how the input
  views under `schemas/views/` are already split. Previously every
  result view inherited from `DispatchResultView` regardless of what
  kind of study produced it — there was no schema-level place for
  power-flow or dynamics results at all.
- Renamed and moved the 5 existing concrete result-view classes to
  match the dot-namespaced convention and their new location:
  - `GenerationResultView` → `views/results/dispatch/GenerationUnit.DispatchResultView.yaml`
  - `StorageResultView` → `views/results/dispatch/StorageUnit.DispatchResultView.yaml`
  - `DemandResultView` → `views/results/dispatch/DemandUnit.DispatchResultView.yaml`
  - `InterconnectorResultView` → `views/results/dispatch/TransmissionElement.DispatchResultView.yaml`
    (renamed to its actual shared parent class, since it targets both
    `Interconnector` and `TransmissionLine`)
  - `NodalPriceResultView` → `views/results/dispatch/NetworkNode.DispatchResultView.yaml`

  **This is a breaking rename** (class identity, not just filename).
  `results/` was tagged `experimental`, so this is within the churn
  that tier signals; bumped to 0.2.0 (pre-1.0, so a breaking change is
  a MINOR bump per common semver practice) rather than 1.0.0.
- Moved `DispatchResultView` itself from `views/dispatch/` (an
  *input*-view folder) to `views/results/dispatch/` — it was a result
  view misplaced among input views the whole time, which is arguably
  the clearest sign the old flat structure was hiding this asymmetry.
  Re-parented from `RepresentationView` directly to the new
  `ResultView`.
- `DispatchRunRecord`: re-parented from `SemanticEntity` to the new
  `RunRecord`; its own `run_timestamp` attribute declaration removed
  (now inherited).
- **`run_ref` attribute replaced by the `hasRunRecord` relation** on
  all result views. `run_ref` was a plain string attribute with no
  referential integrity; a proper relation (`hasDispatchRun`, target
  `DispatchRunRecord`) already existed in `relations/relations.yaml`
  but was never actually used by any concrete result-view class — the
  five concrete views all used `run_ref` instead. `hasDispatchRun` is
  removed (superseded, was unused) in favor of the generic
  `hasRunRecord` declared once on `ResultView`.

### Fixed
- **Data-loss bug in `export_yaml_hierarchical`**: an asset with no
  direct attributes or relations of its own — the normal shape for an
  asset whose only real content lives in an attached representation
  view, e.g. exactly the `GenerationUnit` + `GenerationUnit.
  DispatchResultView` pattern this restructuring is built around — was
  silently dropped from the hierarchical YAML export entirely, views
  and all. The empty-block check ran *before* the code looked up and
  attached the asset's views; reordered so views are attached first,
  and the entity is only skipped if it has neither its own
  attributes/relations nor any attached views. Found while validating
  this change against a real chained dispatch → power-flow → dynamics
  scenario; unrelated to the results restructuring itself but was
  masking the exact case this feature is meant to support. Covered by
  `tests/test_view_only_asset_export.py`.

## [0.1.0] — baseline

Initial schema tree as delivered by the SWEET-CoSi CESDM prototype:
core structural classes, electricity/gas/heat/hydrogen/water assets and
nodes, representation views (topology/dispatch/power-flow/dynamics/...),
IEEE controller model schemas, and the agent-based prosumer extension.
Not retroactively versioned family-by-family — treated as the `0.1.0`
starting point for all families going forward.

## Schema-driven `add_<entity>` convenience API

- Every concrete class in the loaded CESDM schema is now exposed lazily as an
  `add_<snake_case_class_name>(entity_id, *, ...)` method on `CesdmModel`.
- Required inherited attributes and relations are required keyword-only
  arguments in the generated, introspectable Python signature.
- Optional attributes and relations default to `None`; multi-target relations
  accept iterables.
- Schema field names that are not valid Python identifiers are deterministically
  normalized with underscores.
- Generated methods validate all writes through the existing EAR schema-safe
  attribute and relation APIs and return an `AssetProxy`.
- `available_add_methods()` lists all generated method/class mappings.
