# Schemas

Schemas define the **formal structure** of a CESDM model. They specify which
entity classes exist, which attributes and relations they may carry, which
constraints apply, and how classes inherit from each other.

A CESDM model is an instance of these schemas:

```text
schemas define what is allowed
model data instantiates the schemas
toolbox validates the model against the schemas
```

The schema files are the **source of truth**. The Python toolbox should not
hard-code concrete energy-system concepts such as generator dispatch views,
power-flow views, or conversion-unit port semantics. Those concepts belong in
the YAML schemas.

---

## Current schema organisation

The current schema directory is organised around the basic CESDM concepts:

```text
schemas/
├── attributes.yaml          # global attribute registry
├── relations.yaml           # global relation registry
└── entities/
    ├── Assets/
    ├── Representations/
    ├── TechnologyTypes/
    ├── Carriers/
    ├── Buses/
    ├── Profiles/
    └── ...
```

The exact folder names are organisational. The loader scans the schema tree and
registers all schema YAML files it finds.

Important current entity classes include:

```text
GenerationUnit
StorageUnit
DemandUnit
ConversionUnit
ConversionPort
TransmissionLine
Transformer
Interconnector
NetworkNode          ← abstract base for all network nodes
ElectricalBus        ← subclass of NetworkNode
GasBus               ← subclass of NetworkNode
HydrogenBus          ← subclass of NetworkNode
HeatBus              ← subclass of NetworkNode
WaterBus             ← subclass of NetworkNode
EnergyCarrier
CarrierDomain
GeographicalRegion
TimestampSeries
Profile
```

> `Bus` is a deprecated stub retained for backwards compatibility only.
> Always use the typed `NetworkNode` subclasses in new models.

Important technology type classes include:

```text
GeneratorType
StorageType
ConverterType
TransmissionType
```

Important current representation classes include:

```text
SinglePort.TopologyView
TwoPort.TopologyView
TwoPort.TopologyView
Generation.DispatchView
Generation.DispatchView
Generation.DispatchView
Generation.DispatchView
HydroGenerationUnit.DispatchView
ReservoirStorageUnit.DispatchView
Generation.DispatchView
Storage.DispatchView
Demand.DispatchView
Conversion.DispatchView
TransmissionLine.PowerFlowView
Transformer.PowerFlowView
Interconnector.PowerFlowView
```



---

## Loading schemas

A model is created by loading the schema directory:

```python
from cesdm_toolbox import build_model_from_yaml

model = build_model_from_yaml("schemas")
```

The loader reads the schema files, registers classes, attributes and relations,
resolves inheritance, and validates schema-level consistency.

After loading, model construction uses the generic EAR operations:

```python
model.add_entity(class_name, entity_id)
model.add_attribute(entity_id, attribute_id, value)
model.add_relation(entity_id, relation_id, target_entity_id)
```

The allowed class names, attribute names and relation names come from the YAML
schemas.

---

## Entity class YAML format

Each entity class is described by a YAML schema file.

A simplified asset schema may look like this:

```yaml
name: GenerationUnit
parents:
  - EnergyAsset
description: >
  A generation asset such as a PV unit, wind turbine, thermal generator,
  hydro generator, or other producer.
attributes:
  - id: name
    required: false
relations:
  - id: hasTechnology
    required: false
    target: GeneratorType
```

The exact parent class names depend on the current schema hierarchy. The key
idea is that the entity file defines:

| Field | Meaning |
|---|---|
| `name` | Schema class name used in `model.add_entity()` |
| `parents` | Parent classes from which attributes and relations are inherited |
| `description` | Human-readable explanation |
| `attributes` | Attribute ids from `attributes.yaml` |
| `relations` | Relation ids from `relations.yaml`, optionally with target and required constraints |

The class name in the YAML file is the name users must use in Python:

```python
model.add_entity("GenerationUnit", "gen.pv.rooftop")
```

---

## Attribute definitions

Attributes are defined centrally in `attributes.yaml` and referenced from entity
or representation schemas.

Example:

```yaml
nominal_power_capacity:
  description: Rated active power capacity.
  label: Nominal power capacity
  value:
    type: decimal
    minimum: 0.0
  unit:
    constraints:
      enum:
        - MW

dispatch_type:
  description: Operational dispatch category.
  label: Dispatch type
  value:
    type: string
    enum:
      - dispatchable
      - nondispatchable
      - must_run
```

The attribute registry defines:

- data type,
- optional unit,
- constraints,
- allowed enum values,
- description and label.

This is why examples must use schema-valid values. For example, the current
schema expects values such as:

```text
dispatchable
nondispatchable
must_run
```

not values such as `variable_renewable`.

---

## Relation definitions

Relations are defined centrally in `relations.yaml`.

Example:

```yaml
representsAsset:
  description: Links a representation view to the asset entity it describes.

hasTechnology:
  description: Links an asset instance to a reusable technology type.

atNode:
  description: Links a topology view or port to a network node.
  target:
    - Bus
```

Relations define how entities may refer to one another. The `target` constraint
is important: validation checks that relation targets have compatible classes.

For example, if `ConversionPort.atNode` targets `NetworkNode`, then the referenced
node must be a typed `NetworkNode` subclass (`ElectricalBus`, `GasBus`, etc.).

---

## Schema inheritance

Classes inherit attributes and relations from their parent classes.

Conceptually:

```text
SemanticEntity
    ├── SystemAsset
    │       └── EnergyAssetInstance
    │               ├── GenerationUnit
    │               ├── StorageUnit
    │               ├── DemandUnit
    │               ├── ConversionUnit
    │               ├── TransmissionElement
    │               │       ├── TransmissionLine
    │               │       ├── Transformer
    │               │       └── Interconnector
    │               └── DemandUnit
    │
    ├── NetworkNode          ← NOT a SystemAsset; topological primitive
    │       ├── ElectricalBus
    │       ├── GasBus
    │       ├── HydrogenBus
    │       ├── HeatBus
    │       └── WaterBus
    │
    ├── EnergyTechnologyType
    │       ├── GeneratorType
    │       ├── StorageType
    │       ├── ConverterType
    │       └── TransmissionType
    │
    └── Representation views (via representsAsset relation)
            ├── SinglePort.TopologyView       ← one-node connection
            ├── TwoPort.TopologyView          ← two-node branch
            ├── ElectricalBus.PowerFlowView  ← bus type (slack/PV/PQ)
            ├── Generator.PowerFlowView      ← generator P/Q setpoints
            ├── Demand.PowerFlowView         ← load P/Q values
            ├── Generation.DispatchView / Generation.DispatchView
            ├── Generation.DispatchView / Generation.DispatchView
            ├── HydroGenerationUnit.DispatchView / ReservoirStorageUnit.DispatchView
            ├── Generation.DispatchView
            ├── Storage.DispatchView
            ├── Demand.DispatchView
            ├── Conversion.DispatchView
            ├── TransmissionLine.PowerFlowView
            ├── Transformer.PowerFlowView
            ├── Interconnector.PowerFlowView
            ├── Generator.DynamicView.Subtransient
            ├── ControllerView.AVR  (abstract)  →  ControllerView.AVR.SEXS / .IEEET1 / .AC1A / .ST1A
            ├── ControllerView.GOV  (abstract)  →  ControllerView.GOV.IEEEG1 / .GGOV1 / .HYGOV
            └── ControllerView.PSS  (abstract)  →  ControllerView.PSS.STAB1 / .PSS2A / .PSS2B
```

The exact parent classes should be read from the schema YAML files. The important
principle is that users define or extend the schema by editing YAML, not by
changing toolbox code.

---

## Representation schemas

A representation schema describes a model-specific view of an asset.

Example: generation dispatch representation.

```yaml
name: Generation.DispatchView
parents:
  - RepresentationView
description: Dispatch representation for solar generation units.
attributes:
  - id: nominal_power_capacity
relations:
  - id: representsAsset
    required: true
    target: GenerationUnit
  - id: hasAvailabilityProfile
    required: false
    target: Profile
```

A valid model instance then uses this class name exactly:

```python
model.add_entity("Generation.DispatchView", "dispatch.gen.pv.rooftop")
model.add_relation("dispatch.gen.pv.rooftop", "representsAsset", "gen.pv.rooftop")
model.add_attribute("dispatch.gen.pv.rooftop", "nominal_power_capacity", 15.0)
```

---

## Topology schemas

Topology views describe how assets connect to network nodes.

The current naming convention uses dot-separated topology view classes:

```text
SinglePort.TopologyView
TwoPort.TopologyView
TwoPort.TopologyView
```

Use `SinglePort.TopologyView` for one-port assets:

```python
model.add_entity("SinglePort.TopologyView", "topology.gen.pv.rooftop")
model.add_relation("topology.gen.pv.rooftop", "representsAsset", "gen.pv.rooftop")
model.add_relation("topology.gen.pv.rooftop", "atNode", "bus.electricity.main")
```

Use `TwoPort.TopologyView` for two-node assets:

```python
model.add_entity("TwoPort.TopologyView", "topology.line.1")
model.add_relation("topology.line.1", "representsAsset", "line.1")
model.add_relation("topology.line.1", "fromNode", "bus.1")
model.add_relation("topology.line.1", "toNode", "bus.2")
```

For conversion assets, the current design uses explicit `ConversionPort`
entities to describe carrier-specific topology and conversion structure.

---

## Conversion-unit schemas

`ConversionUnit` should remain lightweight. The carrier-specific structure is
described by `ConversionPort`.

Example:

```python
model.add_entity("ConversionUnit", "conv.heatpump.1")

model.add_entity("ConversionPort", "port.heatpump.1.electricity_in")
model.add_attribute("port.heatpump.1.electricity_in", "port_direction", "input")
model.add_attribute("port.heatpump.1.electricity_in", "flow_coefficient", -1.0)
model.add_attribute("port.heatpump.1.electricity_in", "is_reference_port", True)
model.add_relation("port.heatpump.1.electricity_in", "belongsToUnit", "conv.heatpump.1")
model.add_relation("port.heatpump.1.electricity_in", "atNode", "bus.electricity.main")
model.add_relation("port.heatpump.1.electricity_in", "hasCarrier", "carrier.electricity")

model.add_entity("ConversionPort", "port.heatpump.1.heat_out")
model.add_attribute("port.heatpump.1.heat_out", "port_direction", "output")
model.add_attribute("port.heatpump.1.heat_out", "flow_coefficient", 3.0)
model.add_attribute("port.heatpump.1.heat_out", "maximum_output_power", 12.0)
model.add_relation("port.heatpump.1.heat_out", "belongsToUnit", "conv.heatpump.1")
model.add_relation("port.heatpump.1.heat_out", "atNode", "bus.heat.main")
model.add_relation("port.heatpump.1.heat_out", "hasCarrier", "carrier.heat")
```

This avoids older redundant patterns such as direct `hasInputCarrier` and
`hasOutputCarrier` relations on every conversion-unit instance or a separate
`CrossDomainConnectionView`.

---

## Power-flow schemas

Power-flow representation classes use the current dot-separated naming pattern
where defined by the schemas.

Examples:

```text
TransmissionLine.PowerFlowView
Transformer.PowerFlowView
Interconnector.PowerFlowView
```

Example:

```python
model.add_entity("Interconnector.PowerFlowView", "pf.interconnector.ch.fr")
model.add_relation("pf.interconnector.ch.fr", "representsAsset", "interconnector.ch.fr")
model.add_attribute("pf.interconnector.ch.fr", "maximum_power_flow_from_to", 1200.0)
model.add_attribute("pf.interconnector.ch.fr", "maximum_power_flow_to_from", 1000.0)
```

Use the exact class names from the schema files. Do not use old names such as
`Interconnector.PowerFlowView` if the current schema defines
`Interconnector.PowerFlowView`.

---

## Technology type schemas

Technology type schemas define reusable parameter templates.

Common current technology classes include:

```text
GeneratorType
StorageType
ConverterType
TransmissionType
```

Example:

```python
model.add_entity("GeneratorType", "technology.generator.pv")
model.add_attribute("technology.generator.pv", "name", "PV generator type")
model.add_attribute("technology.generator.pv", "dispatch_type", "nondispatchable")
model.add_attribute("technology.generator.pv", "nominal_power_capacity", 15.0)
model.add_attribute("technology.generator.pv", "variable_operating_cost", 0.0)
model.add_relation("technology.generator.pv", "hasOutputCarrier", "carrier.electricity")

model.add_entity("GenerationUnit", "gen.pv.rooftop")
model.add_relation("gen.pv.rooftop", "hasTechnology", "technology.generator.pv")
```

Technology types are useful when several assets share the same default
techno-economic parameters.

---

## Profile and time-series schemas

Time-varying data is represented using `TimestampSeries` and `Profile`.

Example:

```python
model.add_entity("TimestampSeries", "ts.hourly.2025")
model.add_attribute("ts.hourly.2025", "start_datetime", "2025-01-01T00:00:00")
model.add_attribute("ts.hourly.2025", "resolution", "PT1H")
model.add_attribute("ts.hourly.2025", "length", 8760)
model.add_attribute("ts.hourly.2025", "timezone", "Europe/Zurich")

model.add_entity("Profile", "profile.pv.capacity_factor")
model.add_attribute("profile.pv.capacity_factor", "profile_type", "as_capacity_factor")
model.add_attribute("profile.pv.capacity_factor", "profile_unit", "p.u.")
model.add_attribute(
    "profile.pv.capacity_factor",
    "data_reference",
    "profiles.h5:/profiles/profile.pv.capacity_factor/values",
)
model.add_relation("profile.pv.capacity_factor", "hasTimestampSeries", "ts.hourly.2025")
```

The current schema expects profile type values such as:

```text
as_SI
as_capacity_factor
as_normalized_annual_energy
```

---


## Attribute namespace convention

Attribute ids in CESDM follow a `Family.Model.Parameter` naming convention
that prevents collision across controller families and model types.

### Why namespacing is needed

Many dynamic model parameters share the same symbol — `T1`, `T2`, `Ka`, `Ta`
appear in AVR, governor, and PSS models alike, but carry different physical
meanings and units. A flat attribute namespace would require renaming (`T1_pss`,
`T1_gov`, `Ka_avr`) and would still be ambiguous if a new model type reuses
the symbol.

### Three tiers

```text
MACHINE_xd           ← machine reactance (no model qualifier needed — IEEE symbol)
AVR_Efd_max          ← shared across all AVR types (same physical meaning)
AVR_SEXS_Ka          ← SEXS-specific gain (distinct from AVR_IEEET1_Ka)
GOV_IEEEG1_T1        ← IEEEG1 lag time constant (distinct from PSS_STAB1_T1)
PSS_STAB1_Kstab      ← STAB1 stabiliser gain
PSS_PSS2A_Ks1        ← PSS2A first-path gain
```

| Tier | When to use | Example |
|---|---|---|
| `MACHINE.*` | Machine identity + electromagnetic parameters | `MACHINE_xd`, `MACHINE_H`, `MACHINE_ra` |
| `Family.*` | Shared limits/filters valid across all model variants | `AVR_Efd_max`, `GOV_Pmax`, `PSS_Vs_max` |
| `Family.Model.*` | Parameters specific to one IEEE or commercial model | `AVR_SEXS_Ka`, `GOV_GGOV1_Kpgov` |

### Adding a new controller type

To add `AVR_AC4A` (a new exciter type not yet in the schema):

1. Add `AVR_AC4A.*` attributes to `attributes/dynamic.yaml`.
2. Create `schemas/entities/Controllers/AVR/AC4A_ControllerView.AVR.yaml` referencing
   those attribute ids.
3. Register the new file in `entities/entities.yaml`.

No Python changes are needed. The toolbox picks up the new class and attributes
when the schema directory is reloaded.

---

## Adding a new asset class

To add a new asset class, create a schema YAML file under the appropriate
entities folder.

Example: `HydrogenElectrolyser`.

```yaml
name: HydrogenElectrolyser
parents:
  - ConversionUnit
description: >
  Electrolyser converting electricity to hydrogen.
attributes:
  - id: name
relations:
  - id: hasTechnology
    required: false
    target: ConverterType
```

Then model its carrier coupling with `ConversionPort` entities rather than
hard-coding hydrogen-specific relations into the core toolbox.

---

## Adding a new representation class

To add a new representation, create a schema YAML file for the view class.

Example:

```yaml
name: HydrogenElectrolyser.DispatchView
parents:
  - OperationalDispatchView
description: Dispatch representation for hydrogen electrolysers.
attributes:
  - id: nominal_power_capacity
  - id: variable_operating_cost
relations:
  - id: representsAsset
    required: true
    target: HydrogenElectrolyser
```

After reloading the schemas, the new class can be used directly:

```python
model.add_entity("HydrogenElectrolyser.DispatchView", "dispatch.electrolyser.1")
model.add_relation("dispatch.electrolyser.1", "representsAsset", "electrolyser.1")
```

No Python changes should be required if the toolbox is schema-driven.

---

## What should not be in this schema chapter

This chapter intentionally avoids documenting a separate authoring language or
schema compiler.

For the current CESDM design, the recommended approach is:

```text
schema YAML files are the source of truth
the toolbox loads and validates the schemas
helper scripts may generate schema files, but they are not part of the core model
```

This keeps the design simple and avoids divergence between an authoring layer
and the canonical schema files.

---

## Schema validation

Validation happens at two levels.

### Schema-level validation

When the schema is loaded, the toolbox checks whether:

- referenced attributes exist in `attributes.yaml`;
- referenced relations exist in `relations.yaml`;
- relation target classes exist;
- parent classes exist;
- required fields are structurally valid.

### Model-level validation

When a model is validated, the toolbox checks whether:

- entities use known classes;
- attributes are allowed on the entity class;
- attribute values have valid types;
- enum values are valid;
- relation targets exist;
- relation targets have compatible classes;
- required attributes and relations are present.

Example:

```python
errors = model.validate()

if errors:
    for error in errors:
        print("ERROR:", error)
```

Validation errors are often the best way to discover outdated examples or
incorrect class names.

---

## Summary

Schemas are the formal contract of CESDM.

The key rules are:

1. Use the exact class names from the current schema files.
2. Use the exact attribute and relation ids from the registries.
3. Use enum values defined in `attributes.yaml`.
4. Keep assets lightweight.
5. Put model-specific parameters in Representation Views.
6. Use `ConversionPort` for conversion-unit carrier coupling.
7. Use `TimestampSeries` and `Profile` for time-varying data.
8. Add new concepts by extending YAML schemas, not by modifying toolbox code.

A CESDM model is reliable only when its examples, documentation, and code all
use the same schema-defined vocabulary.

See [`examples/example_schema_extension.py`](https://github.com/cesdm/cesdm-toolbox/blob/main/examples/example_schema_extension.py)
for a complete, runnable walkthrough of adding a genuinely new entity
type this way.
