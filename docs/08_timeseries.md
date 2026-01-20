# Time Series Handling in CESDM

This document describes how **time series profiles** (e.g. demand profiles, generation availability, inflows)
are handled in CESDM, how they are stored in **HDF5 files**, and how CESDM entities **reference** these profiles.

The goal is to clearly separate:
- **semantic system structure** (CESDM model)
- **numerical time-dependent data** (HDF5 time series storage)

---

## 1. Design Principle

CESDM follows a **separation-of-concerns** principle:

- CESDM entities describe **what exists** in the energy system
- Time series files describe **how values vary over time**
- CESDM entities only **reference** time series, they do not embed them

This makes models:
- lightweight and readable
- solver-agnostic
- scalable to large time series datasets

---

## 2. Why HDF5 Is Used

Time series data are stored in **HDF5 (`.h5`) files** because HDF5:

- efficiently stores large numerical arrays
- supports compression and chunking
- allows hierarchical naming (similar to folders)
- is widely supported in Python, Julia, MATLAB, and C++

A single HDF5 file can store **all time series** of a CESDM model.

---

## 3. HDF5 File Structure

A typical CESDM HDF5 file follows a simple, predictable hierarchy:

```text
timeseries.h5
├── time
│   ├── index              # time index (e.g. hours, timestamps)
│   └── resolution         # metadata (optional)
│
├── EnergyDemand
│   ├── L_ELEC_CH
│   │   └── profile        # electricity demand profile
│   └── L_HEAT_CH
│       └── profile        # heat demand profile
│
├── EnergyConversionTechnology1x1
│   └── G_CH_GAS
│       └── availability   # availability or capacity factor
│
├── EnergyStorageTechnology
│   └── RES_CH
│       └── inflow         # reservoir inflow
│
└── metadata
    └── units              # optional units description
```

### Key idea

The HDF5 hierarchy mirrors:

```
<EntityType>/<EntityID>/<timeseries_name>
```

This makes the mapping **explicit and unambiguous**.

---

## 4. Naming Conventions

### Entity type
- Must exactly match the CESDM schema entity type
- Examples:
  - `EnergyDemand`
  - `EnergyConversionTechnology1x1`
  - `EnergyStorageTechnology`

### Entity ID
- Must exactly match the CESDM `entity_id`
- Case-sensitive

### Time series name
- Depends on the attribute semantics
- Common names:
  - `profile` (demand, consumption)
  - `availability` (capacity factor)
  - `inflow` (hydro, storage)
  - `price` (market prices)

---

## 5. Referencing Time Series from CESDM

CESDM entities reference time series **by name**, not by embedding data.

### Example: demand with time series

```python
m.add_entity(entity_type="EnergyDemand", entity_id="L_ELEC_CH")
m.add_attribute(
    entity_id="L_ELEC_CH",
    attribute_id="timeseries_profile",
    value="EnergyDemand/L_ELEC_CH/profile"
)
```

This tells the consuming tool:

> “Load the dataset `EnergyDemand/L_ELEC_CH/profile` from the HDF5 file.”

The CESDM model does **not** care about:
- time resolution
- length of the series
- numerical values

---

## 6. Common Time Series References by Entity Type

### EnergyDemand

| Attribute | HDF5 dataset |
|---------|-------------|
| `timeseries_profile` | `EnergyDemand/<id>/profile` |

### EnergyConversionTechnology1x1

| Attribute | Meaning | HDF5 dataset |
|--------|--------|-------------|
| `timeseries_availability` | Capacity factor | `EnergyConversionTechnology1x1/<id>/availability` |

### EnergyStorageTechnology

| Attribute | Meaning | HDF5 dataset |
|--------|--------|-------------|
| `timeseries_inflow` | Natural inflow | `EnergyStorageTechnology/<id>/inflow` |
| `timeseries_initial_soc` | Initial SOC | scalar or separate dataset |

### NetTransferCapacity

| Attribute | Meaning | HDF5 dataset |
|--------|--------|-------------|
| `timeseries_ntc` | Time-varying NTC | `NetTransferCapacity/<id>/capacity` |

---

## 7. Time Index

The time index is stored once and shared by all series:

```text
/time/index
```

Examples:
- hourly index for one year (8760 values)
- representative time steps
- timestamps or integer indices

All datasets are assumed to align with this index.

---

## 8. Validation Rules (Conceptual)

CESDM itself does **not** validate time series values, but tools consuming CESDM should check:

- referenced dataset exists in the HDF5 file
- dataset length matches time index
- units are consistent with the attribute meaning

These checks belong to **model execution**, not semantic modelling.

---

## 9. Advantages of This Approach

- CESDM models remain **compact**
- Time series can be **exchanged independently**
- Large datasets do not pollute semantic definitions
- Same CESDM model can be run with different time series

---

## 10. Summary

In CESDM:

- **Structure lives in CESDM**
- **Numbers live in HDF5**
- **Links are explicit string references**
- **Naming follows entity type and ID**

This design enables scalable, transparent, and interoperable
energy system modelling workflows.
