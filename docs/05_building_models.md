# Building Energy System Models from Schemas

Schemas define *what is allowed*.  
Models define *what exists*.

This page explains **how to build a CESDM model** in a practical way and how
schemas influence every step.

CESDM supports two equivalent construction styles:

1. **Programmatic construction (Python)** — good for automation and scenario generation
2. **Declarative construction (YAML)** — good for readable, shareable model definitions

In both cases, **schemas are always enforced** (same rules, same validation).

---

## 1. The modelling workflow in CESDM

A typical CESDM workflow is:

1. **Load schemas** (define the domain model)
2. **Create a model container** (root object)
3. **Add entities** (typed objects)
4. **Attach attributes** (typed values)
5. **Connect entities using relations** (typed links)
6. **Validate** (schema checks)
7. *(Optional)* Export / import (YAML, CSV, tool adapters)

> 💡 Rule of thumb  
> If you can’t point to a schema rule that allows an attribute or relation,
> CESDM should reject it.

---

## 2. The three core operations

Even complex energy systems are built from just three operations:

### `add_entity(entity_class, entity_id)`
Creates a new object of a schema-defined type.

- **`entity_class`** must match a schema type (e.g., `EnergyCarrier`, `ElectricityNode`)
- **`entity_id`** must be unique within the model

### `add_attribute(entity_id, attribute_id, value)`
Assigns a value to a specific entity attribute.

- the attribute must be allowed by that entity’s schema
- the value must satisfy schema constraints (type, ranges, enums)

### `add_relation(entity_id, relation_id, target_entity_id)`
Creates a typed connection from one entity to another.

- relation name must exist in schema
- target must be of the allowed entity type
- cardinality constraints must be satisfied

---

## 3. Programmatic construction (Python)

Programmatic construction is recommended when models are:

- Generated automatically (scenarios)
- Assembled from external datasets (databases, CSV)
- Created interactively in notebooks or scripts

### Minimal electricity example (structure-first)

Below is a compact example showing the typical sequence:

1) create entities  
2) fetch entity handles  
3) add attributes  
4) add relations  
5) validate

```python
# 1) Create entities
model.add_entity(entity_class="GeographicalRegion", entity_id="R_CH")
model.add_entity(entity_class="EnergyCarrier", entity_id="Electricity")
model.add_entity(entity_class="ElectricityNode", entity_id="N_CH")
model.add_entity(entity_class="EnergyDemand", entity_id="L_CH")

# 2) Add attributes (schema-checked)
model.add_attribute(entity_id="R_CH", attribute_id="name", value="Switzerland")
model.add_attribute(entity_id="N_CH", attribute_id="name", value="CH electricity bus")
model.add_attribute(entity_id="N_CH", attribute_id="nominal_voltage", value=220.0)
model.add_attribute(entity_id="L_CH", attribute_id="annual_energy_demand", value=60e6)

# 3) Add relations (schema-checked)
model.add_relation(entity_id="N_CH", relation_id="isInGeographicalRegion", target_entity_id="R_CH")
model.add_relation(entity_id="L_CH", relation_id="isConnectedToNode", target_entity_id="N_CH")

# (Optional) connect node to carrier/domain if your schema uses it
# model.add_relation("N_CH", "isInEnergyDomain", "ELEC")

# 5) Validate
errors = model.validate()
if errors:
    for e in errors:
        print(" -", e)
    raise SystemExit(1)
```

---

## 4. Declarative construction (YAML)

Declarative construction describes the same information based on YAML artifacts, enabling models that are:

- easy to review in pull requests
- reproducible and shareable
- editable without Python

### Minimal electricity example (YAML)

```yaml
GeographicalRegion:
  - id: R_CH
    name: Switzerland

EnergyCarrier:
  - id: Electricity
    name: Electricity
    energy_carrier_type: DOMAIN
    co2_emission_intensity: 0.0

ElectricityNode:
  - id: N_CH
    name: CH electricity bus
    nominal_voltage: 220.0
    isInGeographicalRegion: R_CH

EnergyDemand:
  - id: L_CH
    name: CH aggregate load
    annual_energy_demand: 60000000.0
    isConnectedToNode: N_CH
```

### How YAML maps to CESDM concepts

| YAML element | CESDM concept |
|-------------|---------------|
| Top-level keys (`ElectricityNode`, `EnergyCarrier`, …) | Entity types |
| List items | Entity instances |
| `id` | Entity identifier |
| Other scalar fields (e.g., `nominal_voltage`) | Attributes |
| Fields referencing other IDs (e.g., `isConnectedToNode: N_CH`) | Relations |

> 💡 In YAML, relations are usually written as **ID references**.
> During loading, CESDM resolves these IDs into actual entity links and validates them.

---

## 5. Validation (common failure modes)

Validation errors typically fall into one of the following categories:

- **Unknown attribute**: attribute not defined for this entity type in the schema
- **Wrong attribute type**: string vs number, etc.
- **Constraint violation**: negative capacity, efficiency > 1, invalid enum value
- **Unknown relation**: relation id not defined in schema
- **Wrong relation target**: linking to the wrong entity type
- **Cardinality mismatch**: missing required relation, or too many targets

A good workflow is to validate frequently and fix problems at the smallest scope.

---

## 6. Programmatic vs Declarative (summary)

Both approaches produce the **same internal CESDM model**.

| Aspect | Programmatic | Declarative (YAML) |
|------|--------------|--------------------|
| Best for | Generated models | Static/shared models |
| Readability | Medium | High |
| Automation | High | Medium |
| Version control | Harder | Easier |
| Validation | Schema-based | Schema-based |

Both approaches are used by CESDM, which enables interoperability within the ecosystem.
