# Introduction: Schema-Driven Energy System Modelling

CESDM is a **general-purpose, schema-driven modelling framework** applied here
to the **energy system domain**.

The core idea of CESDM is simple:

> A system is described using **entities**, **attributes**, and **relations**,
> and the allowed structure is defined by **schemas**.

CESDM focuses on *structure*, not behaviour.
It defines **what an energy system consists of**, not how it is optimised or
simulated.

---

## Why schema-driven modelling?

Energy systems are complex and heterogeneous. Without a formal structure,
models quickly become:

- Ambiguous
- Inconsistent
- Untraceable
- Hard to reuse across tools

Schemas solve this by acting as a **formal contract**:
they define what is allowed, required, and forbidden in a model.

---

## Entity, Attribute, Relation

All CESDM models are built from three primitives:

- **Entity**: an object in the system (region, asset, carrier)
- **Attribute**: a property of an entity (output_capacity, maximum_efficiency)
- **Relation**: an explicit link between entities (hasLocation, hasConversion)

Everything else in CESDM builds on these three concepts.
