# `tutorial_ch_neighbours.py` — Step by Step

## Why this example matters

This is the longest and most narrated example — a simplified 2030
electricity system for Switzerland and its four neighbours (Germany,
France, Italy, Austria), built specifically to show all **three
layers** of the CESDM API side by side, so the relationship between
them is visible in one running script rather than three separate
files. The script prints its own step markers as it runs, so this doc
is a map through it rather than a full re-narration — read the
source's own `STEP` comments alongside this for the complete picture.

---

## The three layers, in one example

**1. Generated `add_<EntityClass>()` constructors** — one per schema
class, fully typed. Give you an entity with its identity set, nothing
more:

```python
model.add_geographical_region("region.ch", name="Switzerland")
model.add_generation_unit("gen.1", hasTechnology=GeneratorTypes.GENERATION_NUCLEAR_LWR)
```

**2. Hand-written composite builders** (`add_generator`, `add_bus`,
`add_reservoir_hydro`, ...) — build on layer 1 to do the common,
multi-step thing in one call: create the entity, connect it to a bus,
pick the right dispatch view, apply technology defaults:

```python
gen = model.add_generator(id="gen.1", technology=GeneratorTypes.GENERATION_NUCLEAR_LWR, bus=bus)
```

**3. Direct proxy attribute/relation assignment** — every object layers
1 and 2 return is a live, typed handle back into the model:

```python
gen.name = "Beznau II"
gen.dispatch.nominal_power_capacity = 1600
gen.connect(bus)
```

`GeneratorTypes.*`/`EnergyCarriers.*`/`NaturalResources.*` (from
`cesdm.default_library`) are typed constants for every technology/
carrier/resource id in the library — your editor autocompletes valid
ids and flags an unknown one immediately, instead of only finding out
via `validate()` later.

---

## Step by step

| Step | What it builds | Worth noticing |
|---|---|---|
| 0 | Load schema + technology library | `103 entity classes available`, `9 carriers, 52 technology types pre-loaded` |
| 1 | System container, carriers, carrier domain | CO2 price and fuel costs set once at the system level |
| 2 | 5 geographic regions | CH, DE, FR, IT, AT |
| 3 | 5 electricity buses | each gets a spatial (lat/lon) view too |
| 4 | 5 demand units | **the deliberate typo demo** — see below |
| 5 | 11 generators | **the technology-fallback demo** — see below |
| 6 | Hydro portfolio | 7 hydro units, 6 reservoirs — run-of-river, reservoir, open-loop PHS, closed-loop PHS all in one system |
| 7 | 8 cross-border interconnectors | CH's real neighbours, each with an NTC-style transfer limit |

### Step 4's typo demonstration

```python
demands_asset = m.asset_as("dem.ch", DemandUnitProxy)
demands_asset.dispatch.anual_energy_demand = 1.0  # <- missing 'n'
```

```
-> caught immediately: 'anual_energy_demand' is not an attribute or
relation of 'Demand.DispatchView'. Did you mean: annual_energy_demand,
maximum_energy_demand?
```

`asset_as(entity_id, DemandUnitProxy)` is used here specifically so
`.dispatch` type-checks correctly in an editor too, not just at
runtime — see [`docs/architecture/proxy_api.md`](../docs/architecture/proxy_api.md).

### Step 5's technology-template fallback

Every generator sets `nominal_power_capacity` explicitly but
deliberately never sets `energy_conversion_efficiency`:

```
energy_conversion_efficiency was never set on 'CH Gas CCGT' -- reads
back as 0.6 anyway, resolved from its GeneratorType technology
template.
```

Reading an attribute that was never set on the instance falls back to
the `GeneratorType` the generator's `hasTechnology` points at — one of
the 52 pre-loaded technology templates from Step 0.

---

## Result

```
VALIDATION
  Model validated successfully -- every relation and attribute
  satisfies the schema's own rules.

MODEL OVERVIEW
  model.summary():
    GenerationUnit           18
    TransmissionElement       8
    StorageUnit               6
    DemandUnit                5
```

(`GenerationUnit` totals 18 because `HydroGenerationUnit` — a
subclass — rolls up into it; `model.summary(detailed=True)` breaks
the subclasses out separately.)

---

## Run it yourself

```bash
python examples/tutorial_ch_neighbours.py
```
