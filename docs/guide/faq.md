# Frequently Asked Questions

## General

**Do I need to know Python to understand CESDM?**

To understand the concepts — no. The ideas behind CESDM (entities, attributes,
relations, views) are independent of Python. The tools are written in Python,
but the principle is universal.

To use CESDM yourself, basic Python knowledge is helpful.

---

**Can I open a CESDM model in Excel?**

Yes. The export command `model.export_excel("model.xlsx")` creates an Excel
workbook with one sheet per object type. You can read all entities, attributes,
and relations there — but cannot re-import the file directly.

---

**What is the difference between CESDM and PyPSA/MATPOWER?**

PyPSA and MATPOWER are calculation tools — they optimise or calculate the
electricity grid. CESDM is a data description layer — it describes what is
in the system but does not calculate anything itself.

Analogy: PyPSA is a calculator. CESDM is the piece of paper where the
numbers are written before you enter them into the calculator.

---

**Why is it called "schema-driven"?**

Because the rules of the system are defined in readable text files (schemas),
not buried in program code. Anyone can read the schemas and understand what
is allowed — without needing to read Python code.

---

## About the concepts

**What is the difference between an entity and a view?**

An **entity** describes what an object is — its identity and intrinsic
properties (name, technology type, energy carrier).

A **view** describes how this object is represented in a particular modelling
context — for example its operational parameters for optimisation, or its
electrical parameters for a network calculation.

Simply put: the entity is the power plant. The views are the different
perspectives on the same power plant — from the dispatch modeller, the
network planner, and the stability engineer.

---

**Why does a wind farm have `dispatch_type = "nondispatchable"`?**

Because the wind farm cannot be freely controlled — the operator can shut it
down, but cannot produce more than the wind allows. In an optimisation model
this means: production is limited by a time-series profile, not freely choosable.

By contrast, `"dispatchable"` is used for power plants that the operator can
ramp up or down at any time (e.g. gas turbine, pumped hydro).

---

**What does `representsAsset` mean?**

This relation links a view to the asset it describes.

Without this relation, the view would be "orphaned" — nobody would know which
asset it belongs to. The `representsAsset` relation is the bond between
an asset and its views.

---

**Why are there carrier domains — does the energy carrier not suffice?**

The energy carrier "electricity" says: what flows. The carrier domain says:
in which network it flows.

Imagine there are two separate electricity networks (high voltage and low
voltage). Both transport electricity — the same energy carrier. But they are
physically separate networks with their own nodes and their own power balances.
Each of these networks would be its own carrier domain.

---

## About the formats

**What is the difference between `as_capacity_factor` and
`as_normalized_annual_energy`?**

Both describe how a time-series profile is to be interpreted:

`as_capacity_factor`: Each value lies between 0 and 1.
Multiplying by the installed power gives the instantaneous power.
Example: capacity factor 0.3 × 250 MW = 75 MW at this hour.

`as_normalized_annual_energy`: All 8 760 hourly values sum to 1.
Multiplying by the annual energy gives the energy in each hour.
Example: profile[t] = 0.00015 × 547 500 MWh = 82 MWh in this hour.

The second type is useful for water inflows or annual energy potentials,
where the total annual energy is the more important quantity than the
instantaneous power.

---

**What is a YAML file and what does it look like?**

YAML is a simple text format for structured data. A YAML file looks like
this — readable without any programming knowledge:

```yaml
GenerationUnit:
  gen.ccgt.01.ch0:
    name: CCGT Switzerland
    attributes:
      - id: nominal_power_capacity
        value: 450.0
        unit: MW
    relations:
      - id: hasOutputCarrier
        target: carrier.electricity
```

It is like a structured list: indentation shows hierarchy, no brackets or
special characters needed.

---

**What is a Frictionless Data Package?**

A standardised data package consisting of:
1. Several CSV tables (one per entity type, like in Excel)
2. A `datapackage.json` file that describes what each table contains

It is self-describing — whoever receives the package knows without asking
what each column means, what units apply, and how the tables relate to
each other.
