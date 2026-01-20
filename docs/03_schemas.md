# Schemas: Defining the Energy System Domain

Schemas define the **formal structure** of an energy system model in CESDM.

They are the *single source of truth* that specifies:
- Which **entity types** exist
- Which **attributes** those entities may or must have
- Which **relations** they may or must form with other entities
- Which **constraints** apply to attributes and relations
- How models are **validated**

In CESDM, models do not define meaning themselves.
They only **instantiate** what schemas allow.

---

## 1. Why schemas are central in CESDM

Energy systems are structurally complex:
- many components
- many connections
- many implicit assumptions

Schemas make this structure:
- **explicit**
- **machine-checkable**
- **shared across tools**

> 💡 **Key idea**  
> A CESDM schema is a *contract*:  
> if a model validates against the schema, it is structurally correct.

---

## 2. Entity types and schema inheritance

### Entity types

Each schema defines an **entity type**, such as:
- `EnergyCarrier`
- `ElectricityNode`
- `EnergyConversionTechnology1x1`
- `EnergyStorageTechnology`

An entity type specifies:
- which attributes are allowed or required
- which relations are allowed or required

---

### Schema inheritance

Schemas can **inherit** from other schemas.

Inheritance means:

> A derived entity type automatically includes all attributes,
> relations, and constraints of its parent type.

This avoids duplication and enforces consistency.

---

### Conceptual inheritance example

For conversion technologies, a typical conceptual hierarchy is:

```
EnergyTechnology
└── EnergyConversionTechnology
    └── EnergyConversionTechnology1x1
```

Each level adds specialization:
- base types define common metadata
- derived types restrict structure and semantics

---

## 3. Case study: EnergyConversionTechnology1x1

`EnergyConversionTechnology1x1` represents a technology that:
- converts **exactly one input energy carrier**
- into **exactly one output energy carrier**
- and injects energy into a grid node

In the CH & neighbours example, it is used for:
- Gas → Electricity
- Water → Electricity (run-of-river hydro)
- Uranium → Electricity (nuclear)

---

## 4. Attributes in schemas

Attributes describe **intrinsic properties** of an entity.
They are typed and constrained.

Typical attributes for `EnergyConversionTechnology1x1` include:

| Attribute | Meaning | Typical constraints |
|---------|--------|---------------------|
| `name` | Human-readable name | string |
| `energy_conversion_efficiency` | Conversion efficiency | number ∈ [0, 1] |
| `nominal_power_capacity` | Installed capacity | number ≥ 0 |
| `generator_technology_type` | Technology label | enum / string |

### Conceptual attribute definition

```yaml
attributes:
  - id: energy_conversion_efficiency
    value:
      type: number
      constraints:
        minimum: 0.0
        maximum: 1.0
```

Schemas ensure:
- the attribute exists (if required)
- the value has the correct type
- the value satisfies constraints

---

## 5. Relations in schemas

Relations define **how entities connect** to other entities.

For `EnergyConversionTechnology1x1`, key relations are:

| Relation ID | Target entity type | Meaning |
|------------|-------------------|--------|
| `hasInputEnergyCarrier` | EnergyCarrier | Input carrier |
| `hasOutputEnergyCarrier` | EnergyCarrier | Output carrier |
| `isOutputNodeOf` | ElectricityNode | Injection point |
| `isInEnergyDomain` | EnergyDomain | Domain membership |
| `isInGeographicalRegion` | GeographicalRegion | Spatial location |

### Conceptual relation definition

```yaml
relations:
  - id: hasInputEnergyCarrier
    target: EnergyCarrier
```

---

## 6. Validation

When `model.validate()` is called, CESDM checks:

### Attribute validation
- required attributes exist
- types are correct
- numeric ranges are respected
- enum values are allowed

### Relation validation
- relations exist in the schema
- targets exist in the model
- targets have the correct entity type

### Inheritance validation
- rules inherited from parent schemas apply automatically

---

### Example validation failures

| Error | Reason |
|------|-------|
| Efficiency = 1.2 | Violates attribute constraint |
| No input carrier | Violates relation cardinality |
| Missing output node | Incomplete connectivity |

---

## 8. Schemas vs models

| Schemas | Models |
|--------|--------|
| Define what is allowed | Instantiate what exists |
| Encode meaning | Contain data |
| Enforce constraints | Are validated |
| Shared across tools | Scenario-specific |

---

## Key takeaway

Schemas in CESDM:
- encode **domain knowledge**
- enforce **structural correctness**
- make models **unambiguous and reusable**

`EnergyConversionTechnology1x1` demonstrates how inheritance, attributes,
relations, and validation work together in a schema-driven
modelling framework.
