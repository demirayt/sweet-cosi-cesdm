# Representation Views

Representation Views are the core mechanism that allows CESDM to describe the
same energy-system asset from different modelling perspectives.

This chapter is written for the current CESDM schema style, where representation
classes use names such as:

- `SinglePort.TopologyView`
- `TwoPort.TopologyView`
- `TwoPort.TopologyView`
- `Generation.DispatchView`
- `Storage.DispatchView`
- `Demand.DispatchView`
- `Conversion.DispatchView`
- `TransmissionLine.PowerFlowView`
- `Transformer.PowerFlowView`
- `Interconnector.PowerFlowView`

---

## Why Representation Views are needed

An energy-system asset can be used by many different types of models.

For example, a generator may be used in:

- a dispatch model,
- a power-flow model,
- a dynamic simulation,
- an investment planning model,
- a result-analysis workflow.

Each modelling perspective requires different information.

| Perspective | Typical information |
|---|---|
| Topology | where the asset connects to the network |
| Dispatch | operational capacity, cost, efficiency, profiles |
| Power flow | electrical parameters, limits, voltage-related data |
| Dynamics | machine parameters, AVR, governor, PSS |
| Planning | investment cost, lifetime, candidate status |
| Results | generation, flows, prices, state of charge, emissions |

If all of these parameters were placed directly on the asset entity, classes
such as `GenerationUnit`, `StorageUnit`, or `ConversionUnit` would become large,
ambiguous, and tool-specific.

Representation Views avoid this problem by separating:

```text
asset identity
    from
model-specific representation
```

The asset describes **what exists**. The Representation View describes **how the
asset is used in a particular modelling context**.

---

## Basic pattern

Every Representation View is a normal CESDM entity. It has its own id, class,
attributes, and relations. It points to the asset it describes using the
`representsAsset` relation.

```python
model.add_entity("Generation.DispatchView", "dispatch.gen.pv.rooftop")
model.add_relation(
    "dispatch.gen.pv.rooftop",
    "representsAsset",
    "gen.pv.rooftop",
)
```

Conceptually:

```text
GenerationUnit: gen.pv.rooftop
      │
      ├── SinglePort.TopologyView: topology.gen.pv.rooftop
      │       atNode → bus.electricity.main
      │
      └── Generation.DispatchView: dispatch.gen.pv.rooftop
              nominal_power_capacity = 15.0
              hasAvailabilityProfile → profile.pv.capacity_factor
```

The `representsAsset` relation is the stable link between the physical asset and
all model-specific views.

---

## Recommended entity id convention

The schema defines class names. Entity ids are chosen by the model author.

A practical convention is:

```text
topology.<asset_id>
dispatch.<asset_id>
pf.<asset_id>
dynamic.<asset_id>
planning.<asset_id>
result.<run_id>.<asset_id>
```

Examples:

```text
topology.gen.pv.rooftop
dispatch.gen.pv.rooftop
pf.line.1
dispatch.storage.battery.home
result.run2030.gen.pv.rooftop
```

This keeps ids readable while preserving the explicit class name in the entity
record.

---

## Current view families

The current schemas organise representation views into several families:

```text
RepresentationView
    ├── Topology views
    ├── Dispatch views
    ├── Power-flow views
    ├── Dynamic views
    ├── Planning views
    └── Result views
```

The following sections describe the important current view concepts.

---

### Topology Views

Topology views describe how assets connect to network nodes.

#### `SinglePort.TopologyView`

Use `SinglePort.TopologyView` for assets with one network connection point.

Typical represented assets:

- `GenerationUnit`
- `StorageUnit`
- `DemandUnit`
- shunt-like assets
- external grid-like assets

Example:

```python
model.add_entity("GenerationUnit", "gen.pv.rooftop")

model.add_entity("SinglePort.TopologyView", "topology.gen.pv.rooftop")
model.add_relation("topology.gen.pv.rooftop", "representsAsset", "gen.pv.rooftop")
model.add_relation("topology.gen.pv.rooftop", "atNode", "bus.electricity.main")
```

Conceptually:

```text
gen.pv.rooftop
      │
      └── SinglePort.TopologyView
              atNode → bus.electricity.main
```

Use this when the asset behaves as a one-port injection, withdrawal, or storage
element at a node.

---

#### `TwoPort.TopologyView`

Use `TwoPort.TopologyView` for assets connecting two nodes
(transmission lines, transformers, interconnectors).

Typical represented assets:

- `TransmissionLine`
- `Transformer`
- `Interconnector`
- switch-like or link-like assets

Example:

```python
model.add_entity("TransmissionLine", "line.1")

model.add_entity("TwoPort.TopologyView", "topology.line.1")
model.add_relation("topology.line.1", "representsAsset", "line.1")
model.add_relation("topology.line.1", "fromNode", "bus.1")
model.add_relation("topology.line.1", "toNode", "bus.2")
```

Conceptually:

```text
line.1
      │
      └── TwoPort.TopologyView
              fromNode → bus.1
              toNode   → bus.2
```

---

#### `TwoPort.TopologyView`

Use `TwoPort.TopologyView` for assets with more than two connection points.

Typical represented assets:

- multi-carrier conversion units,
- CHP units,
- heat pumps,
- electrolysers,
- multi-terminal systems.

In the current CESDM conversion-unit design, detailed port semantics are usually
represented with explicit `ConversionPort` entities. Therefore
`TwoPort.TopologyView` can be used as a high-level topology representation
where needed, but the port-level carrier and node structure belongs to
`ConversionPort`.

---

### ConversionUnit and ConversionPort

The current schemas model conversion assets using:

```text
ConversionUnit
      ├── ConversionPort input
      ├── ConversionPort output
      └── Conversion.DispatchView
```

The `ConversionUnit` itself should remain lightweight. Input/output carriers,
nodes, conversion ratios, and output limits are represented by `ConversionPort`.

Example heat pump:

```python
model.add_entity("ConversionUnit", "conv.heatpump.1")

model.add_entity("ConversionPort", "port.heatpump.1.electricity_in")
model.add_attribute("port.heatpump.1.electricity_in", "port_direction", "input")
model.add_attribute("port.heatpump.1.electricity_in", "flow_coefficient", -1.0)
model.add_attribute("port.heatpump.1.electricity_in", "is_reference_port", True)
model.add_relation("port.heatpump.1.electricity_in", "belongsToUnit", "conv.heatpump.1")
model.add_relation("port.heatpump.1.electricity_in", "atNode", "bus.electricity.main")
model.add_relation("port.heatpump.1.electricity_in", "hasCarrier", "carrier.electricity")

model.add_entity("ConversionPort", "port.heatpump.1.heat_out")
model.add_attribute("port.heatpump.1.heat_out", "port_direction", "output")
model.add_attribute("port.heatpump.1.heat_out", "flow_coefficient", 3.0)
model.add_attribute("port.heatpump.1.heat_out", "maximum_output_power", 12.0)
model.add_relation("port.heatpump.1.heat_out", "belongsToUnit", "conv.heatpump.1")
model.add_relation("port.heatpump.1.heat_out", "atNode", "bus.heat.main")
model.add_relation("port.heatpump.1.heat_out", "hasCarrier", "carrier.heat")
```

The important rule is:

> Carrier-specific conversion semantics belong to `ConversionPort`, not to
> `Conversion.DispatchView`.

This means attributes such as electrical efficiency, thermal efficiency, heat
output limit, or COP-like behaviour should be expressed through port attributes
such as `flow_coefficient` and `maximum_output_power`.

---

### Dispatch Views

Dispatch views describe operational optimisation parameters.

They are typically used by:

- economic dispatch models,
- unit commitment models,
- operational planning tools,
- flexibility models,
- capacity adequacy workflows.

---

#### Specialised generation dispatch views

Use the concrete generation dispatch view whenever the asset technology is known: `Generation.DispatchView`, `Generation.DispatchView`, `Generation.DispatchView`, `Generation.DispatchView`, `HydroGenerationUnit.DispatchView`, or `Generation.DispatchView` only for fallback/abstract generation.

Example:

```python
model.add_entity("Generation.DispatchView", "dispatch.gen.pv.rooftop")
model.add_relation("dispatch.gen.pv.rooftop", "representsAsset", "gen.pv.rooftop")
model.add_attribute("dispatch.gen.pv.rooftop", "nominal_power_capacity", 15.0)
model.add_attribute("dispatch.gen.pv.rooftop", "maximum_generation", 15.0)
model.add_attribute("dispatch.gen.pv.rooftop", "variable_operating_cost", 0.0)
```

Typical attributes depend on the specialised view. Variable renewables use `nominal_power_capacity` plus `hasAvailabilityProfile`; thermal and nuclear views add ramping, efficiency and unit-commitment parameters; hydro uses `machine_role`, turbine/pump efficiencies and reservoir relations.

The current schema expects `dispatch_type` values such as:

```text
dispatchable
nondispatchable
must_run
```

Use `nondispatchable` for variable renewable generation such as PV or wind when
the output follows an availability profile.

---

#### `Storage.DispatchView`

Use `Storage.DispatchView` for storage operational parameters.

Example:

```python
model.add_entity("Storage.DispatchView", "dispatch.storage.battery.home")
model.add_relation("dispatch.storage.battery.home", "representsAsset", "storage.battery.home")
model.add_attribute("dispatch.storage.battery.home", "nominal_power_capacity", 5.0)
model.add_attribute("dispatch.storage.battery.home", "energy_storage_capacity", 13.5)
model.add_attribute("dispatch.storage.battery.home", "maximum_charging_power", 5.0)
model.add_attribute("dispatch.storage.battery.home", "charging_efficiency", 0.95)
model.add_attribute("dispatch.storage.battery.home", "discharging_efficiency", 0.95)
model.add_attribute("dispatch.storage.battery.home", "minimum_state_of_charge", 0.1)
model.add_attribute("dispatch.storage.battery.home", "maximum_state_of_charge", 1.0)
```

Typical attributes include:

- `nominal_power_capacity`
- `energy_storage_capacity`
- `maximum_charging_power`
- `maximum_discharging_power`
- `charging_efficiency`
- `discharging_efficiency`
- `minimum_state_of_charge`
- `maximum_state_of_charge`

---

#### `Demand.DispatchView`

Use `Demand.DispatchView` for demand-side operational parameters.

Example:

```python
model.add_entity("Demand.DispatchView", "dispatch.demand.household")
model.add_relation("dispatch.demand.household", "representsAsset", "demand.household")
model.add_attribute("dispatch.demand.household", "annual_energy_demand", 4500.0)
model.add_attribute("dispatch.demand.household", "maximum_energy_demand", 8.0)
```

Typical attributes include:

- `annual_energy_demand`
- `maximum_energy_demand`
- demand profile relations,
- flexibility-related parameters where defined by the schema.

---

#### `Conversion.DispatchView`

Use `Conversion.DispatchView` for the operational representation of a
`ConversionUnit`.

Example:

```python
model.add_entity("Conversion.DispatchView", "dispatch.conv.heatpump.1")
model.add_relation("dispatch.conv.heatpump.1", "representsAsset", "conv.heatpump.1")
```

This view should remain generic. Do not add carrier-specific conversion
semantics here. Instead, use `ConversionPort`.

---


### ElectricalBus.PowerFlowView

Use `ElectricalBus.PowerFlowView` to specify the power-flow model type for a network node.

The `powerflow_bus_type` attribute (required) determines which quantities are
fixed and which are solved at the node:

| Value | Fixed | Solved | Typical use |
|---|---|---|---|
| `slack` | V, θ | P, Q | Reference bus (one per island) |
| `PV` | P, V | Q, θ | Generator bus with AVR voltage control |
| `PQ` | P, Q | V, θ | Load bus, passive network node |

```python
model.add_entity("ElectricalBus.PowerFlowView", "pf.bus.1")
model.add_relation("pf.bus.1", "representsAsset", "bus.1")
model.add_attribute("pf.bus.1", "powerflow_bus_type", "slack")
model.add_attribute("pf.bus.1", "voltage_magnitude_setpoint", 1.03)  # pu
model.add_attribute("pf.bus.1", "voltage_angle_setpoint", 0.0)       # degrees
```

Voltage setpoints and initial conditions belong on `ElectricalBus.PowerFlowView`, not on
the `ElectricalBus` entity or on `Generator.PowerFlowView`.

---

### Power-flow Views

Power-flow views describe parameters required for network analysis.

Power-flow views use PascalCase names:

```text
TransmissionLine.PowerFlowView
Transformer.PowerFlowView
Interconnector.PowerFlowView
Generator.PowerFlowView
Demand.PowerFlowView
ElectricalBus.PowerFlowView
```

---

#### `TransmissionLine.PowerFlowView`

Use this view for line parameters used in power-flow calculations.

Example:

```python
model.add_entity("TransmissionLine.PowerFlowView", "pf.line.1")
model.add_relation("pf.line.1", "representsAsset", "line.1")
model.add_attribute("pf.line.1", "series_resistance_per_km", 0.01)
model.add_attribute("pf.line.1", "series_reactance_per_km", 0.1)
model.add_attribute("pf.line.1", "thermal_capacity_rating", 1000.0)
```

Typical information includes:

- resistance,
- reactance,
- susceptance,
- line length,
- thermal limit.

---

#### `Transformer.PowerFlowView`

Use this view for transformer power-flow parameters.

Example:

```python
model.add_entity("Transformer.PowerFlowView", "pf.transformer.1")
model.add_relation("pf.transformer.1", "representsAsset", "transformer.1")
```

Typical information includes:

- rated primary voltage,
- rated secondary voltage,
- short-circuit voltage,
- tap settings,
- thermal capacity.

---

#### `Interconnector.PowerFlowView`

Use this view for interconnector power-flow or transfer-capacity parameters.

Example:

```python
model.add_entity("Interconnector.PowerFlowView", "pf.interconnector.ch.fr")
model.add_relation("pf.interconnector.ch.fr", "representsAsset", "interconnector.ch.fr")
model.add_attribute("pf.interconnector.ch.fr", "maximum_power_flow_from_to", 1200.0)
model.add_attribute("pf.interconnector.ch.fr", "maximum_power_flow_to_from", 1000.0)
```



---

### Dynamic Views

Dynamic views describe time-domain dynamic behaviour. In the current schemas,
the dynamic generator model and its controllers are themselves represented as
Representation Views. They are not generic controller entities with arbitrary
relations; they use concrete schema-defined view classes and relation names.

The current dynamic representation family includes:

```text
DynamicView
    └── Generator.DynamicView.Subtransient

ControllerView
    ├── ControllerView.AVR
    │       ├── ControllerView.AVR.SEXS
    │       ├── ControllerView.AVR.IEEET1
    │       ├── ControllerView.AVR.AC1A
    │       └── ControllerView.AVR.ST1A
    │
    ├── ControllerView.GOV
    │       ├── ControllerView.GOV.IEEEG1
    │       ├── ControllerView.GOV.GGOV1
    │       └── ControllerView.GOV.HYGOV
    │
    └── ControllerView.PSS
            ├── ControllerView.PSS.STAB1
            ├── ControllerView.PSS.PSS2A
            └── ControllerView.PSS.PSS2B
```

The concrete machine view is currently named:

```text
Generator.DynamicView.Subtransient
```

It represents a `GenerationUnit` modelled as a subtransient synchronous machine.
Typical machine attributes use the `MACHINE.` prefix, for example:

```text
MACHINE_rated_mva
MACHINE_rated_kv
MACHINE_model
MACHINE_H
MACHINE_D
MACHINE_xd
MACHINE_xq
MACHINE_xd_prime
MACHINE_xq_prime
MACHINE_xd_dprime
MACHINE_xq_dprime
MACHINE_Td0_prime
MACHINE_Tq0_prime
MACHINE_Td0_dprime
MACHINE_Tq0_dprime
MACHINE_ra
MACHINE_xl
```

A correct schematic structure is therefore:

```text
GenerationUnit: gen.g1
      │
      ├── Generator.DynamicView.Subtransient: dynamic.machine.gen.g1
      │       representsAsset             → gen.g1
      │       hasAutomaticVoltageRegulator → dynamic.avr.gen.g1
      │       hasTurbineGovernor          → dynamic.gov.gen.g1
      │       hasPowerSystemStabilizer    → dynamic.pss.gen.g1
      │
      ├── ControllerView.AVR.ST1A: dynamic.avr.gen.g1
      │       representsAsset → gen.g1
      │
      ├── ControllerView.GOV.IEEEG1: dynamic.gov.gen.g1
      │       representsAsset → gen.g1
      │
      └── ControllerView.PSS.PSS2A: dynamic.pss.gen.g1
              representsAsset → gen.g1
```

Note the exact relation names:

```text
hasAutomaticVoltageRegulator
hasTurbineGovernor
hasPowerSystemStabilizer
```

Do not use invented relation names such as `hasController`, `hasExciter`,
or `hasGov` — only the three names above are declared in `relations.yaml`.

Example in Python:

```python
# Physical generator asset
model.add_entity("GenerationUnit", "gen.g1")
model.add_attribute("gen.g1", "name", "Synchronous generator G1")

# Subtransient machine dynamic representation
model.add_entity("Generator.DynamicView.Subtransient", "dynamic.machine.gen.g1")
model.add_relation("dynamic.machine.gen.g1", "representsAsset", "gen.g1")
model.add_attribute("dynamic.machine.gen.g1", "MACHINE_rated_mva", 900.0)
model.add_attribute("dynamic.machine.gen.g1", "MACHINE_rated_kv", 20.0)
model.add_attribute("dynamic.machine.gen.g1", "MACHINE_model", "subtransient_6th")
model.add_attribute("dynamic.machine.gen.g1", "MACHINE_H", 6.5)
model.add_attribute("dynamic.machine.gen.g1", "MACHINE_xd", 1.8)
model.add_attribute("dynamic.machine.gen.g1", "MACHINE_xq", 1.7)
model.add_attribute("dynamic.machine.gen.g1", "MACHINE_xd_prime", 0.3)
model.add_attribute("dynamic.machine.gen.g1", "MACHINE_xd_dprime", 0.25)
model.add_attribute("dynamic.machine.gen.g1", "MACHINE_xq_dprime", 0.25)
model.add_attribute("dynamic.machine.gen.g1", "MACHINE_Td0_prime", 8.0)
model.add_attribute("dynamic.machine.gen.g1", "MACHINE_Td0_dprime", 0.03)
model.add_attribute("dynamic.machine.gen.g1", "MACHINE_Tq0_dprime", 0.05)

# AVR controller view
model.add_entity("ControllerView.AVR.ST1A", "dynamic.avr.gen.g1")
model.add_relation("dynamic.avr.gen.g1", "representsAsset", "gen.g1")
model.add_attribute("dynamic.avr.gen.g1", "AVR_ST1A_Ka", 200.0)
model.add_attribute("dynamic.avr.gen.g1", "AVR_ST1A_Ta", 0.02)
model.add_attribute("dynamic.avr.gen.g1", "AVR_Va_min", -5.0)
model.add_attribute("dynamic.avr.gen.g1", "AVR_Va_max", 5.0)
model.add_attribute("dynamic.avr.gen.g1", "AVR_Efd_min", -5.0)
model.add_attribute("dynamic.avr.gen.g1", "AVR_Efd_max", 5.0)

# Governor controller view
model.add_entity("ControllerView.GOV.IEEEG1", "dynamic.gov.gen.g1")
model.add_relation("dynamic.gov.gen.g1", "representsAsset", "gen.g1")
model.add_attribute("dynamic.gov.gen.g1", "GOV_IEEEG1_R", 0.05)
model.add_attribute("dynamic.gov.gen.g1", "GOV_IEEEG1_T1", 0.5)
model.add_attribute("dynamic.gov.gen.g1", "GOV_IEEEG1_T3", 3.0)
model.add_attribute("dynamic.gov.gen.g1", "GOV_Pmax", 1.0)
model.add_attribute("dynamic.gov.gen.g1", "GOV_Pmin", 0.0)

# PSS controller view
model.add_entity("ControllerView.PSS.PSS2A", "dynamic.pss.gen.g1")
model.add_relation("dynamic.pss.gen.g1", "representsAsset", "gen.g1")
model.add_attribute("dynamic.pss.gen.g1", "PSS_PSS2A_Ks1", 10.0)
model.add_attribute("dynamic.pss.gen.g1", "PSS_PSS2A_Ks2", 1.0)
model.add_attribute("dynamic.pss.gen.g1", "PSS_PSS2A_Tw1", 2.0)
model.add_attribute("dynamic.pss.gen.g1", "PSS_PSS2A_Tw3", 2.0)
model.add_attribute("dynamic.pss.gen.g1", "PSS_PSS2A_T1", 0.1)
model.add_attribute("dynamic.pss.gen.g1", "PSS_PSS2A_T2", 0.03)
model.add_attribute("dynamic.pss.gen.g1", "PSS_Vs_max", 0.2)
model.add_attribute("dynamic.pss.gen.g1", "PSS_Vs_min", -0.2)

# Link controllers to the machine view with typed relations
model.add_relation(
    "dynamic.machine.gen.g1",
    "hasAutomaticVoltageRegulator",
    "dynamic.avr.gen.g1",
)
model.add_relation(
    "dynamic.machine.gen.g1",
    "hasTurbineGovernor",
    "dynamic.gov.gen.g1",
)
model.add_relation(
    "dynamic.machine.gen.g1",
    "hasPowerSystemStabilizer",
    "dynamic.pss.gen.g1",
)
```

This design keeps dynamic simulation data separate from dispatch and power-flow
data while still linking all dynamic views back to the same `GenerationUnit`.

---

### Planning Views

Planning views describe long-term investment and lifecycle assumptions.

Typical information includes:

- investment cost,
- fixed operation and maintenance cost,
- technical lifetime,
- commissioning year,
- decommissioning year,
- candidate/extendable status,
- expansion limits.

Planning data may also be stored in technology types when it represents default
assumptions shared by many assets.

---

### Result Views

Result views describe outputs from simulations or optimisations.

Examples include:

- generation results,
- storage results,
- demand results,
- interconnector results,
- nodal price results,
- dispatch profiles.

Result views should be treated as output artefacts. They are usually generated
by a model run rather than manually authored as input data.

---

### Views and Profiles

Profiles are used when a representation needs time-varying data.

Example for PV availability:

```python
model.add_entity("Profile", "profile.pv.capacity_factor")
model.add_attribute("profile.pv.capacity_factor", "profile_type", "as_capacity_factor")
model.add_attribute("profile.pv.capacity_factor", "profile_unit", "p.u.")
model.add_relation("dispatch.gen.pv.rooftop", "hasAvailabilityProfile", "profile.pv.capacity_factor")
```

The current schema expects `profile_type` values such as:

```text
as_SI
as_capacity_factor
as_normalized_annual_energy
```

---

### Multi-group modelling with views

Representation Views are especially useful when different groups contribute
different parts of a model.

Example:

```text
Group A: topology team
    provides SinglePort.TopologyView and TwoPort.TopologyView

Group B: dispatch team
    provides specialised generation DispatchViews, Storage/Reservoir DispatchViews, Demand.DispatchView

Group C: network analysis team
    provides TransmissionLine.PowerFlowView, Transformer.PowerFlowView,
    Interconnector.PowerFlowView

Group D: dynamic simulation team
    provides dynamic views and controller models

Group E: planning team
    provides planning views and technology library entries
```

All groups refer to the same asset ids.

```text
gen.pv.rooftop
      ├── topology.gen.pv.rooftop
      ├── dispatch.gen.pv.rooftop
      └── planning.gen.pv.rooftop
```

The asset is the shared identity anchor. Views are independent contributions
attached to that anchor.

---

### Finding views for an asset

A useful generic helper is:

```python
def get_representations_for_asset(model, asset_id):
    result = []

    for class_name, group in model.entities.items():
        for entity_id, entity in group.items():
            data = getattr(entity, "data", {})
            relation = data.get("representsAsset")

            if not relation:
                continue

            targets = relation.get("target_entity_ids", [])
            if asset_id in targets:
                result.append((entity_id, class_name))

    return result
```

Example:

```python
for view_id, view_class in get_representations_for_asset(model, "gen.pv.rooftop"):
    print(view_id, view_class)
```

Possible output:

```text
topology.gen.pv.rooftop SinglePort.TopologyView
dispatch.gen.pv.rooftop Generation.DispatchView
```

This pattern is useful for:

- exporters,
- validators,
- GUIs,
- reports,
- debugging.

---

### Views in YAML exports

In `yaml_hierarchical`, views may be grouped near their represented asset to
make the file easier to read.

In `yaml_flat`, views are stored as normal entities with explicit
`representsAsset` relations.

Example flat structure:

```yaml
entities:
  - id: gen.pv.rooftop
    class: GenerationUnit

  - id: topology.gen.pv.rooftop
    class: SinglePort.TopologyView
    relations:
      representsAsset:
        - gen.pv.rooftop
      atNode:
        - bus.electricity.main

  - id: dispatch.gen.pv.rooftop
    class: Generation.DispatchView
    relations:
      representsAsset:
        - gen.pv.rooftop
      hasAvailabilityProfile:
        - profile.pv.capacity_factor
    attributes:
      nominal_power_capacity: 15.0
```

In Frictionless exports, representation views can be stored as tabular
resources. The `representsAsset` field acts as the foreign key back to the
asset.

---

### Current view reference

| View class | Typical represented asset | Purpose |
|---|---|---|
| `SinglePort.TopologyView` | `GenerationUnit`, `StorageUnit`, `DemandUnit` | One-port topology |
| `TwoPort.TopologyView` | `TransmissionLine`, `Transformer`, `Interconnector` | Two-node topology |
| `TwoPort.TopologyView` | `ConversionUnit` | Multi-port topology where needed |
| `Generation.DispatchView` / `Generation.DispatchView` | `GenerationUnit` / `GenerationUnit` | Variable renewable dispatch and availability profiles |
| `Generation.DispatchView` / `Generation.DispatchView` | `GenerationUnit` / `GenerationUnit` | Dispatchable generator parameters |
| `HydroGenerationUnit.DispatchView` | `HydroGenerationUnit` | Hydro turbine/pump dispatch parameters |
| `ReservoirStorageUnit.DispatchView` | `ReservoirStorageUnit` | Reservoir energy/water state and inflow |
| `Generation.DispatchView` | `GenerationUnit` | Fallback generation dispatch parameters |
| `Storage.DispatchView` | `StorageUnit` | Storage dispatch parameters |
| `Demand.DispatchView` | `DemandUnit` | Demand dispatch parameters |
| `Conversion.DispatchView` | `ConversionUnit` | Generic conversion dispatch representation |
| `TransmissionLine.PowerFlowView` | `TransmissionLine` | Line power-flow parameters |
| `Transformer.PowerFlowView` | `Transformer` | Transformer power-flow parameters |
| `Interconnector.PowerFlowView` | `Interconnector` | Interconnector transfer or power-flow parameters |
| `Generator.DynamicView.Subtransient` | `GenerationUnit` | Subtransient synchronous-machine dynamic model |
| `ControllerView.AVR.*` | `GenerationUnit` | AVR / excitation-system controller views |
| `ControllerView.GOV.*` | `GenerationUnit` | Turbine-governor controller views |
| `ControllerView.PSS.*` | `GenerationUnit` | Power-system stabilizer controller views |
| Planning views | Assets or technology types | Long-term investment/planning parameters |
| Result views | Assets, nodes, or model runs | Outputs from simulations or optimisation |

---

## Summary

Representation Views allow CESDM to describe the same energy system from
multiple modelling perspectives.

The key rules are:

1. Keep asset entities lightweight.
2. Link every view to its asset using `representsAsset`.
3. Use `SinglePort.TopologyView` (single-node) and `TwoPort.TopologyView`
   (two-node) for topology. Use `ElectricalBus.PowerFlowView` for bus type and
   voltage initial conditions.
4. Use specialised dispatch views for known technologies; use `Generation.DispatchView` only for fallback generation. Use `Storage.DispatchView`, `ReservoirStorageUnit.DispatchView`, `Demand.DispatchView`, and `Conversion.DispatchView` where appropriate.
5. Use `TransmissionLine.PowerFlowView`, `Transformer.PowerFlowView`, and
   `Interconnector.PowerFlowView` for power-flow-related data.
6. Use `ConversionPort` for conversion-unit carriers, nodes, directions,
   coefficients, and output limits.
7. Use valid schema enum values such as `nondispatchable` and
   `as_capacity_factor`.
8. Do not use obsolete class names from older CESDM versions.

The schema files remain the source of truth. Documentation and examples should
always use the exact class names, attributes, relations, and enum values defined
there.
