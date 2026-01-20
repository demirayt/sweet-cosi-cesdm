# Core Concepts and the Minimal CESDM API

CESDM deliberately exposes a **minimal API**.
Despite this, it can represent arbitrarily complex energy systems.

The reason is that **schemas provide meaning**, while the API only populates
that meaning.

---

## The three core functions

Every CESDM system can be built using only three operations:

1. `add_entity(entity_class: str, entity_id: str)`
2. `add_attribute(entity_id: str, attribute_id: str, value)`
3. `add_relation(entity_id: str, relation_id: str, target_entity_id: str)`

These functions are sufficient because:

- `add_entity` creates objects defined by schemas
- `add_attribute` assigns schema-defined properties
- `add_relation` creates schema-defined connections

---

## Example: creating an energy asset

```python
model.add_entity(entity_class="CombinedHeatandPowerPlant", entity_id="CHP_plant")
model.add_attribute(entity_id="CHP_plant",attribute_id="rated_electrical_power_capacity", value=500)
plant.add_attribute(entity_id="CHP_plant",attribute_id="net_electrical_efficiency", 0.25)
```

Whether these attributes are valid is determined entirely by the schema.

> 💡 **Key idea**  
> The API never decides what is allowed — schemas do.
