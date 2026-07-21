# What is CESDM?

## The problem in one sentence

Researchers who study energy systems use many different computer programs.
Power flow models analyse network operation and voltages, economic dispatch
models optimise short-term generation schedules, capacity expansion models
determine long-term investment decisions, and dynamic simulation models
study transient stability — often describing the very same power plants,
storage systems, and transmission networks, but each in its own data
structure, naming convention, and set of assumptions.

This fragmentation creates real problems: identical concepts get
represented differently across tools, input datasets are duplicated and
transformed over and over, a custom converter is needed for every pair of
tools, assumptions end up hidden inside tool-specific formats, and
comparing studies becomes difficult because the underlying data isn't
aligned.

**CESDM is the shared translator.**

## What CESDM does — and what it does not

CESDM describes an energy system. It does not calculate anything, optimise
anything, or simulate anything.

Think of CESDM as a detailed architectural blueprint: the blueprint shows
where a power plant is located, how large it is, and what it is connected
to — but it does not produce electricity itself.

```
      Real energy system
               │
               ▼
            CESDM
     (shared description)
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
 PyPSA      MATPOWER    FlexDYN
(optimise)  (load flow) (simulate)
```

The tools at the bottom are examples of calculation tools. CESDM supplies
all of them with the same input data — clean, validated, and in a format
they all understand. The aim is not to replace these tools, but to make it
easier for them to share, validate, compare, and reuse structured data.

## Three simple building blocks

CESDM builds everything from just three basic building blocks:

### 1. Entity — "What exists?"

An entity is a named object in the energy system — a power plant, a grid
node, a storage facility, an energy carrier category, a geographic region.
Every entity has a unique id, similar to a passport number.

### 2. Attribute — "What properties does it have?"

An attribute describes a property of an entity, with a value and a unit —
rated power = 450 MW, efficiency = 58%, nominal voltage = 380 kV.

### 3. Relation — "What is it connected to?"

A relation is a named link between two entities — a power plant *is
connected to* a grid node, a grid node *is located in* a region, a power
plant *uses as fuel* natural gas.

## A concrete example: a wind farm

This is what a wind farm looks like in CESDM — without any programming code:

**Entity:** Wind Farm Switzerland (id: `gen.wind.ch0`)

**Attributes:**
- Name: "Wind Farm Switzerland"
- Rated power: 250 MW
- Dispatch type: non-dispatchable (the wind decides when electricity is produced)

**Relations:**
- Uses as input resource → Wind resource
- Produces as output → Electricity
- Is connected to → Grid node "CH 380 kV"
- Has time-series profile → hourly wind availability data

That's all. From these three building block types — entities, attributes,
relations — the entire CESDM model is constructed, whether it describes a
single wind farm or a pan-European energy system.

## What is a "schema"?

A schema is a rulebook that defines what is allowed. Think of a form: it
has certain fields (name, date of birth, address), each field expects a
certain type of value, and some fields are mandatory. CESDM schemas work
the same way — they define which entity classes exist, which attributes
and relations each type may have, and which values are valid (for example,
efficiency cannot exceed 100%). These schemas are stored in plain YAML
files that anyone can read with a text editor — the domain knowledge lives
in the schema, not buried in program code, so adding a new asset type (an
electrolyser, say) means writing a new schema file, not changing the
toolbox itself.

Any dataset that conforms to a schema can be validated automatically, and
any tool that understands the schema can interpret the data without
relying on implicit assumptions.

## Representation views

A central idea in CESDM is the separation between an asset and its
model-specific representations. The same storage unit might need a
dispatch representation for optimisation, a power-flow representation for
network analysis, and a dynamic representation for transient simulation —
so instead of putting every possible parameter into one large entity,
CESDM separates *what the object is* (the asset) from *how it's used in a
particular modelling context* (a representation view). See
[`05_representation_views.md`](05_representation_views.md) for the full
design.

## Two layers underneath

CESDM is built in two layers: a generic, domain-agnostic
entity/attribute/relation engine (`ear`) that knows nothing about energy
systems at all, and the CESDM domain layer on top of it, which adds
energy-system schemas, representation-view patterns, and import/export
adapters. See [`09_ear_toolbox.md`](09_ear_toolbox.md) and
[`10_cesdm_toolbox.md`](10_cesdm_toolbox.md).

## Glossary of key terms

| Term | Explanation |
|---|---|
| **Entity** | A named object (power plant, bus, region, energy carrier) |
| **Attribute** | A property with a value and unit (power = 450 MW) |
| **Relation** | A named link between two entities |
| **Schema** | A rulebook defining which entities, attributes, and relations are allowed |
| **Representation view** | A model-specific perspective on an asset (dispatch, power-flow, dynamic, ...) |
| **YAML** | A simple text format for structured data — readable like a shopping list |
| **HDF5** | A file format for large numerical datasets (e.g. 8,760 hourly values) |
| **PyPSA** | A Python program for energy system optimisation |
| **MATPOWER** | A program for AC load flow calculation |
| **Grid node / Bus** | A point in the electricity grid where energy is injected or withdrawn |
| **Energy carrier** | The form of energy (electricity, natural gas, hydrogen, heat) |
| **per unit (pu)** | Normalised dimensionless unit; 1.0 pu = the rated/nominal value |

See [`glossary.md`](glossary.md) for the full glossary.
