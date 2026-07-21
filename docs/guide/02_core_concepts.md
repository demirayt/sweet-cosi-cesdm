# Core Concepts: How CESDM Describes an Energy System

## The fundamental principle: separate identity from representation

CESDM makes a strict distinction between two questions:

> **What is this object?** → the entity
> **How is this object used in a particular model?** → the representation view

### Why this separation matters

Take a gas-fired power plant as an example:

- In an **optimisation study**, what matters is: capacity, efficiency,
  operating cost, minimum up-time
- In a **load flow calculation**, what matters is: injection point, active
  and reactive power, bus type
- In a **stability simulation**, what matters is: inertia constant,
  machine reactances, controller parameters

If all these parameters were stored directly on the power plant entity,
the object would become huge and unwieldy — full of parameters that are
irrelevant to the model at hand.

**CESDM solves this as follows:**

```
Power plant (entity) — describes ONLY what it IS
        │
        ├── Dispatch view      ← only for optimisation
        ├── Power flow view    ← only for network calculation
        ├── Topology view      ← where is it connected?
        └── Dynamic view       ← only for stability simulation
```

Each calculation program reads only the view it needs.
The other views do not interfere with it.

---

## The view families at a glance

### Topology views — "Where is the object connected?"

Every asset must be connected to the network. The topology view describes
this connection.

**Single-node connection** (generator, storage, consumer):
```
Wind farm → connected to → grid node "CH 380 kV"
```

**Two-node connection** (line, transformer, interconnector):
```
Line → from node "CH" → to node "DE"
```

### Dispatch views — "How is the object parametrised in optimisation?"

This view contains all parameters that an optimisation model needs:

| View type | Typical parameters |
|---|---|
| Generation unit | Rated power, efficiency, variable cost, min/max output |
| Storage unit | Power, capacity, charge/discharge efficiency, state-of-charge limits |
| Demand unit | Annual energy demand, peak load, time-series profile |
| HVDC link | Maximum transfer power, variable cost |

### Power flow views — "How does the object behave in the electricity network?"

This view contains electrical parameters for network calculations:

| View type | Typical parameters |
|---|---|
| Grid node | Bus type (Slack/PV/PQ), voltage setpoint |
| Transmission line | Resistance, reactance, thermal rating |
| Transformer | Primary/secondary voltage, short-circuit voltage |
| Generator | Active and reactive power setpoints |

> **What do Slack, PV, PQ mean?**
> These are three types of grid nodes in a load flow calculation:
> - **Slack**: reference node — holds voltage and angle fixed, absorbs all
>   power imbalances in the system
> - **PV**: node with controlled voltage (typically a generator bus with an AVR)
> - **PQ**: node with fixed load (active and reactive power are given)

### Dynamic views — "How does the generator behave during disturbances?"

These views are only needed for transient stability simulations.
They describe the time-domain behaviour of generators and their controllers.

A synchronous generator typically has three controllers:

| Controller | Function |
|---|---|
| **AVR** (Automatic Voltage Regulator) | Keeps the generator voltage constant — responds to voltage changes in the network |
| **GOV** (Turbine Governor) | Keeps the frequency constant — adjusts steam or water flow to the turbine |
| **PSS** (Power System Stabilizer) | Damps power oscillations in the network — a "shock absorber" for the generator |

---

## Energy domains, carriers, and natural resources

CESDM separates **energy carriers** transported inside networks from
**natural resources** that enter the model from outside the boundary.

**EnergyCarrier** is a transported commodity inside an explicit network:
- Electricity
- Natural gas
- Hydrogen
- Heat

**NaturalResource** is an exogenous resource that is not transported as a carrier:
- Wind
- Solar irradiation
- Water inflow / reservoir water

**CarrierDomain** is the network that transports a particular `EnergyCarrier`.
A domain always transports exactly one carrier. Natural resources do not have
their own CarrierDomain unless the physical carrier is explicitly transported
inside the model boundary.

```
Electricity domain ─────────────────────────────────────────────
  │  Generators   Storage    Consumers    Transmission lines     │
  └──────────────────────────────────────────────────────────────

Gas domain ─────────────────────────────────────────────────────
  │  Gas sources  Caverns    Consumers    Pipelines              │
  └──────────────────────────────────────────────────────────────

Conversion technologies (e.g. gas turbine, heat pump)
connect two domains to each other.
```

### Three roles in the system

| Role | What it does | Examples |
|---|---|---|
| **Generation unit** (GenerationUnit) | Feeds energy from an external source into the system | Wind, solar, nuclear, run-of-river hydro |
| **Conversion unit** (ConversionUnit) | Transforms one energy carrier into another | Gas turbine, heat pump, electrolyser |
| **Storage unit** (StorageUnit) | Shifts energy in time | Battery, pumped hydro, gas cavern |

> **When is a gas turbine a generation unit and when a conversion unit?**
> It depends on whether the gas supply is explicitly modelled:
> - If gas is outside the model boundary → **generation unit** (gas is simply "there")
> - If the gas network is part of the model → **conversion unit** (gas is consumed from the gas domain)

---

## Time series and profiles

Many parameters change hourly — wind availability, demand, solar irradiation.
CESDM stores these time series separately from the model to keep model files
small.

**Two entity classes manage time series:**

**TimestampSeries** — defines the time axis:
- Start date: e.g. 1 January 2030, 00:00
- Resolution: PT1H = one hour per time step
- Length: 8 760 time steps (= one year)
- Timezone: Europe/Zurich

> **What is PT1H?** This is the ISO 8601 format for time durations.
> P stands for "Period", T for "Time", 1H for 1 hour.
> PT1H = one hour. PT15M = 15 minutes. PT30M = 30 minutes.

**Profile** — describes a single time series:
- Profile type: capacity factor (0–1) or normalised annual energy
- Unit: pu (per unit = normalised, dimensionless)
- Link to the TimestampSeries
- Link to the data file (HDF5)

> **What is HDF5?** A file format for large numerical datasets.
> An HDF5 file can store millions of numerical values efficiently —
> for example, the hourly wind availability of 1 000 sites over a full year.

### Three profile types

| Type | Meaning | Example |
|---|---|---|
| `as_capacity_factor` | Value between 0 and 1; multiply by rated power to get instantaneous power | Wind capacity factor |
| `as_normalized_annual_energy` | All values sum to 1; multiply by annual energy to get hourly distribution | Water inflow |
| `as_SI` | Absolute values in physical units (MW, MWh, …) | Measured load profile |

---

## Data exchange formats

CESDM supports several formats:

| Format | Best for |
|---|---|
| **YAML** (hierarchical) | Human-readable, version-controllable with Git, ideal for small to medium models |
| **Frictionless Data Package** | Standard format for tabular data packages — good for sharing with external partners |
| **HDF5** | Large time-series datasets (millions of values) |
| **Excel** | Easy inspection and manual editing |

> **What is YAML?** A simple text format — readable like a structured
> shopping list. Unlike Excel or JSON files, YAML files can be opened
> and understood directly in a text editor.

> **What is a Frictionless Data Package?** An open standard for
> self-describing data packages — similar to a ZIP archive with an
> attached table of contents that explains what each file contains
> and what values are valid.
