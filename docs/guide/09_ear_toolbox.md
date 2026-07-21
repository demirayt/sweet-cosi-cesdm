# The EAR Engine (`ear_toolbox.py`)

`ear_toolbox` is the foundation of CESDM. It is a **completely
domain-agnostic** engine for modelling any structured domain using three
primitives: **Entities**, **Attributes**, and **Relations**.

It knows nothing about electricity, generators, or kilowatts. It only knows
about objects, their properties, and how they connect. This makes it reusable
across domains — energy systems, transport networks, social sciences, supply
chains — without any changes to the engine itself.

---

## The three primitives

Everything in EAR reduces to three operations:

```python
model.add_entity(class_name: str, entity_id: str)
model.add_attribute(entity_id: str, attribute_id: str, value)
model.add_relation(entity_id: str, relation_id: str, target_entity_id: str)
```

- **Entity** — a named object of a schema-defined class.
  `"node.ch0"` is a `"ElectricalBus"`. `"household.zh.001"` is a `"Household"`.
- **Attribute** — a typed property with a value and optional unit.
  `nominal_voltage = 380.0 kV`. `annual_consumption_kwh = 4200.0`.
- **Relation** — an explicit typed link between two entities.
  `"node.ch0" locatedIn "region.ch"`. `"household.zh.001" connectedTo "node.zh.low"`.

> **Key insight:** the API never decides what is allowed — schemas do.
> `add_attribute` validates the attribute type and range against the schema.
> `add_relation` validates the target class. The engine enforces; it never guesses.

---

## A non-energy example: prosumers and energy communities

To understand EAR without energy-system baggage, consider a social science
dataset about **prosumers** — households and small businesses that both consume
and produce energy, and who may form **energy communities** for collective
self-consumption.

This is a real domain in social science and energy research (e.g. SWEET–CoSi
studies household behaviour, adoption barriers, and community structures).

### Designing the schema

We define three entity classes:

```yaml
# entities/Household.yaml
name: Household
parents:
  - SemanticEntity
description: >
  A residential household that may consume, produce,
  or store energy. The unit of social analysis.
attributes:
  - id: occupant_count
  - id: building_type          # detached / semi-detached / apartment
  - id: ownership_status       # owner / tenant
  - id: gross_floor_area_m2
  - id: annual_consumption_kwh
  - id: has_pv                 # boolean
  - id: has_battery            # boolean
  - id: has_ev                 # boolean
  - id: adoption_year          # year PV/battery was installed
relations:
  - id: locatedIn
    target: Municipality
    required: true
  - id: memberOf
    target: EnergyCommittee
  - id: connectedTo
    target: LowVoltageNode
```

```yaml
# entities/EnergyCommittee.yaml
name: EnergyCommittee
parents:
  - SemanticEntity
description: >
  A local energy community — a group of households and small
  businesses engaged in collective self-consumption.
attributes:
  - id: name
  - id: founding_year
  - id: member_count
  - id: total_pv_capacity_kwp
  - id: self_sufficiency_rate
  - id: legal_form              # cooperative / association / llc
relations:
  - id: locatedIn
    target: Municipality
  - id: hasOperator
    target: Organisation
```

```yaml
# entities/Municipality.yaml
name: Municipality
parents:
  - SemanticEntity
attributes:
  - id: name
  - id: bfs_code              # Swiss federal municipality code
  - id: canton
  - id: population
  - id: urbanisation_level    # urban / suburban / rural
relations:
  - id: isPartOf
    target: Canton
```

### Populating the model

```python
from ear_toolbox import build_model_from_yaml

model = build_model_from_yaml("schemas_agentbased")

# Municipalities
model.add_entity("Municipality", "mun.zurich.261")
model.add_attribute("mun.zurich.261", "name",              "Zürich")
model.add_attribute("mun.zurich.261", "bfs_code",          261)
model.add_attribute("mun.zurich.261", "canton",            "ZH")
model.add_attribute("mun.zurich.261", "population",        420000)
model.add_attribute("mun.zurich.261", "urbanisation_level","urban")

model.add_entity("Municipality", "mun.stmoritz.3787")
model.add_attribute("mun.stmoritz.3787", "name",           "St. Moritz")
model.add_attribute("mun.stmoritz.3787", "bfs_code",       3787)
model.add_attribute("mun.stmoritz.3787", "canton",         "GR")
model.add_attribute("mun.stmoritz.3787", "urbanisation_level", "rural")

# Energy community
model.add_entity("EnergyCommittee", "ec.sunergy.zh.001")
model.add_attribute("ec.sunergy.zh.001", "name",              "Sunergy Zürich-West")
model.add_attribute("ec.sunergy.zh.001", "founding_year",     2021)
model.add_attribute("ec.sunergy.zh.001", "member_count",      48)
model.add_attribute("ec.sunergy.zh.001", "total_pv_capacity_kwp", 340.0)
model.add_attribute("ec.sunergy.zh.001", "self_sufficiency_rate", 0.67)
model.add_attribute("ec.sunergy.zh.001", "legal_form",        "cooperative")
model.add_relation("ec.sunergy.zh.001",  "locatedIn", "mun.zurich.261")

# Households
model.add_entity("Household", "hh.zh.001.0042")
model.add_attribute("hh.zh.001.0042", "occupant_count",        3)
model.add_attribute("hh.zh.001.0042", "building_type",         "detached")
model.add_attribute("hh.zh.001.0042", "ownership_status",      "owner")
model.add_attribute("hh.zh.001.0042", "gross_floor_area_m2",   145.0)
model.add_attribute("hh.zh.001.0042", "annual_consumption_kwh",5200.0)
model.add_attribute("hh.zh.001.0042", "has_pv",                True)
model.add_attribute("hh.zh.001.0042", "has_battery",           True)
model.add_attribute("hh.zh.001.0042", "has_ev",                False)
model.add_attribute("hh.zh.001.0042", "adoption_year",         2022)
model.add_relation("hh.zh.001.0042",  "locatedIn", "mun.zurich.261")
model.add_relation("hh.zh.001.0042",  "memberOf",  "ec.sunergy.zh.001")

model.add_entity("Household", "hh.zh.001.0043")
model.add_attribute("hh.zh.001.0043", "occupant_count",        2)
model.add_attribute("hh.zh.001.0043", "building_type",         "apartment")
model.add_attribute("hh.zh.001.0043", "ownership_status",      "tenant")
model.add_attribute("hh.zh.001.0043", "annual_consumption_kwh",3100.0)
model.add_attribute("hh.zh.001.0043", "has_pv",                False)
model.add_attribute("hh.zh.001.0043", "has_battery",           False)
model.add_relation("hh.zh.001.0043",  "locatedIn", "mun.zurich.261")
# This household is not a community member — no memberOf relation
```

### Querying the model

```python
# All prosumer households (have PV)
prosumers = {
    eid: ent
    for eid, ent in model.entities["Household"].items()
    if ent.data.get("has_pv", {}).get("value") is True
}
print(f"Prosumer households: {len(prosumers)}")

# All community members in Zürich
community_members = {
    eid: ent
    for eid, ent in model.entities["Household"].items()
    if "ec.sunergy.zh.001" in str(ent.data.get("memberOf", ""))
}
print(f"Community members: {len(community_members)}")

# Average floor area of owner-occupiers
owner_areas = [
    ent.data["gross_floor_area_m2"]["value"]
    for ent in model.entities["Household"].values()
    if ent.data.get("ownership_status", {}).get("value") == "owner"
    and "gross_floor_area_m2" in ent.data
]
print(f"Average owner floor area: {sum(owner_areas)/len(owner_areas):.0f} m²")
```

### Exporting the dataset

```python
# To YAML (lossless, version-controllable)
model.export_yaml("prosumer_dataset.yaml")

# To Frictionless Data Package (self-describing, shareable)
model.export_frictionless(
    "prosumer_package/",
    name        = "sweet-cosi-prosumer-survey-zh-2023",
    title       = "SWEET-CoSi Prosumer Survey — Canton Zürich 2023",
    description = "Household-level prosumer and energy community dataset.",
)
```

---

## Why this matters for CESDM

The prosumer example shows that `ear_toolbox` is genuinely domain-agnostic.
The same three operations (`add_entity`, `add_attribute`, `add_relation`) and
the same export formats (YAML, Frictionless) work identically whether you
are modelling:

- A 380 kV transmission network (CESDM energy domain)
- A distribution grid with prosumers (social science / DSO domain)
- A cross-domain study linking household behaviour to grid impacts

This is the architectural advantage of the two-layer design. The engine never
changes. The schemas change, because they encode domain knowledge. The energy
domain simply adds energy-specific schemas on top of a generic foundation.

---

## `ear_toolbox` API reference

### Model container

```python
from ear_toolbox import build_model_from_yaml, Model

# Load the prosumer schema and return a Model instance
model = build_model_from_yaml("schemas_agentbased")

# Alternatively: create an empty model and load the same schema manually
model = Model()
model.load_classes_from_yaml("schemas_agentbased")
```

### Core operations

```python
# Create an entity of the given class
model.add_entity(class_name: str, entity_id: str)

# Set an attribute value on an existing entity
# Value is type-checked and range-validated against the schema
model.add_attribute(entity_id: str, attribute_id: str, value: Any)

# Add a relation from one entity to another
model.add_relation(entity_id: str, relation_id: str, target_entity_id: str)
```

### Reading back

```python
# Access entities by class and id
entity = model.entities["Household"]["hh.zh.001.0042"]

# Read an attribute value (returns AttributeValue dict or scalar)
raw  = entity.data["annual_consumption_kwh"]
val  = raw["value"] if isinstance(raw, dict) else raw
unit = raw.get("unit") if isinstance(raw, dict) else None

# Read all classes
for class_name, class_def in model.classes.items():
    print(class_name)

# Read all entities of a class
for entity_id, entity in model.entities.get("Household", {}).items():
    print(entity_id, entity.data.get("name"))
```

### Schema inspection

```python
# Collected attributes and relations for a class (including inherited)
attrs, rels = model._collect_inherited_fields(model.classes["Household"])
print("Attributes:", list(attrs.keys()))
print("Relations:",  list(rels.keys()))
```

### Validation

```python
errors = model.validate()    # list of error strings; empty = valid
if errors:
    for e in errors:
        print("ERROR:", e)
```

### Import / export

EAR/CESDM supports two main import/export mechanisms for complete models:
YAML and Frictionless Data Package. They serve different purposes.

#### YAML import/export

YAML is the standard way of exporting and importing EAR/CESDM models based on
the schema YAML files.

The schema directory, for example `schemas_agentbased`, defines which entity
classes, attributes, and relations are valid. A model instance can then be
exported to YAML as data that conforms to these schemas. When the YAML file is
imported again, the model is reconstructed and validated against the same schema
definitions.

This makes YAML the preferred native format for EAR/CESDM model exchange during
development because it is:

- directly aligned with the schema YAML files;
- human-readable and easy to inspect;
- suitable for version control with Git;
- easy to review in pull requests;
- lossless with respect to entities, attributes, and relations;
- convenient for editing examples, tests, and small to medium-sized models.

In practice, the workflow is:

```text
schemas_agentbased
      │
      ▼
model built with ear_toolbox
      │
      ▼
prosumer_dataset.yaml
      │
      ▼
model imported again and validated against schemas_agentbased
```

Example:

```python
from ear_toolbox import build_model_from_yaml

# Load the schema
model = build_model_from_yaml("schemas_agentbased")

# Build or modify the model here
# ...

# Export model to YAML
model.export_yaml("prosumer_dataset.yaml")

# Import the model again from YAML
model.import_yaml("prosumer_dataset.yaml")
```

The YAML export/import path should therefore be considered the canonical
EAR/CESDM-native way of storing and reloading structured models.

#### Frictionless import/export

Frictionless Data Package is also supported because it is a widely used standard
for tabular data exchange. It provides a standard way to describe datasets using
a `datapackage.json` file together with one or more tabular resources such as
CSV files.

This is useful when EAR/CESDM data has to be exchanged with external tools,
data portals, data pipelines, or research workflows that already understand
Frictionless packages. Compared with YAML, Frictionless is less focused on
human-authored hierarchical model structure and more focused on portable,
self-describing tabular datasets.

CESDM enables Frictionless import/export so that models can be shared in a
standardised data-exchange format while still being validated against the
schema-defined EAR/CESDM model structure.

Typical use cases are:

- publishing model input data as a data package;
- exchanging model data with non-CESDM tools;
- integrating with tabular data workflows;
- sharing datasets with metadata and resource descriptions;
- supporting reproducible research datasets.

Example:

```python
# Export model to a Frictionless Data Package
model.export_frictionless(
    "prosumer_package/",
    name="sweet-cosi-prosumer-survey-zh-2023",
    title="SWEET-CoSi Prosumer Survey — Canton Zürich 2023",
    description="Household-level prosumer and energy community dataset.",
)

# Import model from a Frictionless Data Package
model.import_frictionless("prosumer_package/")
```

In short:

- use **YAML** as the native EAR/CESDM format for schema-based model storage,
  editing, and round-tripping;
- use **Frictionless** when data should be exchanged as a standard,
  self-describing tabular data package.

See [`examples/example_ear_generic_domain.py`](https://github.com/cesdm/cesdm-toolbox/blob/main/examples/example_ear_generic_domain.py)
for this exact household/energy-community scenario as a complete,
runnable script.
