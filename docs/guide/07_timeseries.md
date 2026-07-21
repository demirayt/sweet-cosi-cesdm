# Time Series Handling in CESDM

CESDM follows a strict **separation of concerns**:

- CESDM entities describe *what exists* in the energy system (structure)
- Time series files describe *how values vary over time* (data)
- CESDM entities only **reference** time series — they do not embed them

This makes models lightweight, solver-agnostic, and scalable to large datasets.

---

## 1. Entities involved

Two entity classes manage time series:

### `TimestampSeries`

Defines the time axis — start datetime, resolution, length, and timezone.

| Attribute | Meaning |
|-----------|---------|
| `start_datetime` | ISO 8601 start (e.g. `"2030-01-01T00:00:00"`) |
| `resolution` | Step duration (e.g. `"PT1H"` = one hour) |
| `length` | Number of timesteps |
| `timezone` | Timezone string (e.g. `"UTC"`, `"Europe/Zurich"`) |

### `Profile`

Holds metadata about one time series and links to its `TimestampSeries`.
Actual numerical values live in the HDF5 file — the Profile entity only carries
references.

| Attribute | Meaning |
|-----------|---------|
| `profile_type` | `as_capacity_factor` / `as_normalized_annual_energy` / `as_SI` |
| `profile_unit` | Unit string (e.g. `"pu"`, `"MW"`, `"MWh"`) |
| `hasTimestampSeries → TimestampSeries` | Time axis reference |

---

## 2. How assets reference profiles

Assets reference profiles via their dispatch view:

| View | Relation | Profile type |
|------|----------|-------------|
| `Generation.DispatchView` / `Generation.DispatchView` | `hasAvailabilityProfile → Profile` | Capacity factor |
| `HydroGenerationUnit.DispatchView` | `hasRunOfRiverInflowProfile → Profile` | Run-of-river inflow/availability |
| `ReservoirStorageUnit.DispatchView` | `hasNaturalInflowProfile → Profile` | Natural reservoir inflow |
| `Demand.DispatchView` | `hasDemandProfile → Profile` | Negative values (withdrawal convention) |

Example:

```python
# TimestampSeries entity
model.add_entity("TimestampSeries", "ts.2030")
model.add_attribute("ts.2030", "start_datetime", "2030-01-01T00:00:00")
model.add_attribute("ts.2030", "resolution",     "PT1H")
model.add_attribute("ts.2030", "length",         8760)
model.add_attribute("ts.2030", "timezone",       "UTC")

# Profile entity
model.add_entity("Profile", "profile.onwind.ch0")
model.add_attribute("profile.onwind.ch0", "profile_type", "as_capacity_factor")
model.add_attribute("profile.onwind.ch0", "profile_unit", "pu")
model.add_relation("profile.onwind.ch0", "hasTimestampSeries", "ts.2030")

# Link from Generation.DispatchView or Generation.DispatchView
model.add_relation("dispatch.gen.onwind.01.ch0",
                   "hasAvailabilityProfile", "profile.onwind.ch0")
```

---

## 3. Profile type conventions

### `as_capacity_factor` (PyPSA)

Dimensionless [0, 1] capacity factor. Timeseries is interpreted as:

```
P(t) = nominal_power_capacity × profile(t)
```

### `as_normalized_annual_energy`

Profile values sum to 1 over the full year. Timeseries is interpreted as:

```
P(t) = annual energy quantity × profile(t)
# e.g. annual_energy_demand, annual_natural_inflow_energy, or
# a technology-specific annual availability value
```

### `as_SI`

Absolute values in SI units (MW, MWh, etc.).

---

## 4. HDF5 storage

Profiles are stored in a flat key-value HDF5 file alongside the CESDM model:

### CESDM hierarchical HDF5 (`export_hdf5`)

```
profiles.h5
├── timestamps/
│   └── ts.2030/          ← TimestampSeries entity id
│       attrs: start_datetime, resolution, length, timezone
└── profiles/
    └── profile.onwind.ch0/
        └── values         ← float64 array, shape (8760,)
            attrs: profile_type, profile_unit
```

---

## 5. Profile id conventions

Profile ids follow the asset id they belong to:

```
profile.{carrier_slug}.{node_suffix}     ← generation availability
profile.demand.{node_suffix}             ← demand profile
profile.inflow.{carrier_slug}.{node_suffix}  ← storage inflow
```

Examples:
```
profile.onwind.ch051.6603                wind farm at NUTS3 ch051
profile.demand.ch051.6603                demand at same node
profile.inflow.hydro.ch051.6603          hydro inflow at same node
```

