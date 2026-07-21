# The object-oriented proxy API (`cesdm.proxy`)

Most CESDM code should never have to think about representation-view
class strings or write raw low-level relation calls directly. This is
a thin object-oriented wrapper over the existing schema-driven
engine — the schema itself is completely unchanged.

## The shape

```python
model = build_model_from_yaml("schemas")
bus = model.add_bus("bus.1", nominal_voltage=380)

gen = model.add_generator(id="gen1", technology="Generation.Nuclear.LWR")
gen.dispatch.nominal_power_capacity = 1600
gen.dispatch.maximum_generation = 1550
gen.connect(bus)

model.validate_or_raise()
```

`add_generator`/`add_bus`/... create the entity and wire up the views/
relations that go with it in one call. See
[`docs/getting_started.md`](../getting_started.md) for the same model
built with lower-level calls instead, for comparison.

## `AssetProxy`: the object every builder returns

Every builder function (`add_bus`, `add_generator`, `create_demand_unit`,
...) returns an `AssetProxy` — a plain string (the entity id) with
extra behaviour attached. Because it *is* a string, it works anywhere
a plain entity id is expected: as a dict key, compared with `==`
against a string, passed into any other method, printed, hashed.

`model.asset(entity_id)` wraps an already-existing entity id in an
`AssetProxy` too, for when you have a bare id (e.g. from an import or
a query) and want the same convenient interface.

### Setting an asset's own fields

Most operational data lives on views (`gen.dispatch.
nominal_power_capacity = 1600`), but an asset's own identity fields —
`name`, `description`, `long_name` — are set the same direct way:

```python
region_ch = model.add_geographical_region("region.ch", name="Switzerland")
bus.name = "Bus 1"
bus.locatedIn = region_ch  # relations too, not just attributes
```

A typo raises immediately, with a spelling suggestion, instead of
silently doing nothing.

## `ViewProxy`: views as properties

`asset.dispatch`, `asset.powerflow`, `asset.dynamic`, `asset.topology`,
`asset.planning`, `asset.spatial`, `asset.technical`, `asset.avr`,
`asset.governor`, `asset.pss` each give you the matching
representation view for that asset — created automatically the first
time you access it. You never need to know or type the concrete view
class name (`Generation.DispatchView`, `HydroGenerationUnit.
DispatchView`, ...) yourself; the right one is resolved from the
asset's type automatically.

If a property name is misspelled, or the asset genuinely doesn't have
a view of that kind (e.g. `bus.dynamic` — an electrical bus has no
dynamic-simulation view), you get a clear error naming what's actually
available instead of a confusing failure.

Attribute access on a view is checked the same way — an unknown name
raises immediately, with a spelling suggestion, rather than silently
doing nothing:

```pycon
>>> gen.dispatch.nominal_power_capaciyt = 1600  # typo
AttributeError: 'nominal_power_capaciyt' is not an attribute or
relation of 'Generation.DispatchView'. Did you mean:
nominal_power_capacity?
```

### Automatic unit attachment

Setting a plain scalar (`gen.dispatch.nominal_power_capacity = 1600`,
not a `(value, unit)` tuple) automatically attaches the right unit for
you **when the attribute has exactly one valid unit**. A handful of
attributes genuinely accept more than one unit (e.g. `reservoir_volume`
can be GWh, TWh, hm³, or m³) — for those, set the unit explicitly with
a `(value, unit)` tuple instead, since guessing would be worse than
asking.

## `connect()`

```python
gen.connect(bus)            # single-port connection (generators, demand, ...)
line.connect(bus1, bus2)    # two-port connection (lines, transformers, ...)
```

One or two arguments connects the right way automatically.

## Static type-checking

In your editor (Pyright/Pylance), `model.asset(entity_id)` and some
builder results type as the generic `AssetProxy`, so `.dispatch.x`
won't be checked against the specific entity class. Use
`asset_as(entity_id, SpecificProxyClass)` when you want that checked
too:

```python
from cesdm.generated_proxies import GenerationUnitProxy

gen = model.asset_as("gen1", GenerationUnitProxy)
gen.dispatch.nominal_power_capacity = 1600   # now type-checks
```

`asset_as` also accepts a tuple of classes for the rare case where an
entity could genuinely be one of a few different types.

Type stubs under `typings/` (regenerated with `cesdm-update-generated`
after any schema change) give full editor autocomplete and type
checking across the whole proxy API.

## Current limitations

- No fluent method-chaining yet (`model.add_generator(...).at(bus).
  capacity(400)`) — use the keyword-argument style shown above.
- No `.static` property yet for asset ownership/business metadata
  (e.g. `gen.static.owner = "Axpo"`).
- `add_generator(technology=...)` needs the full technology id
  (`"Generation.Thermal.Gas.CCGT"`), not a short abbreviation like
  `"CCGT"`.
