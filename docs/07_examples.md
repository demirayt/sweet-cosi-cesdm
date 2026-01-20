# Worked Example: Switzerland (CH) and Neighbours (Electricity Only)

This worked example is a **step-by-step walkthrough** of the repository’s
`example_ch_and_neighbours.py` script, showing how to build a small European
electricity model by calling CESDM’s core methods **one by one**:

- `add_entity(...)`
- `add_attribute(...)`
- `add_relation(...)`

The example is intentionally **didactic** (illustrative numbers) and focuses on
**structure and validation**, not data realism.

---

## Overview of the system

We model:

- One **EnergySystemModel** container: `CH_NEIGHBOURS`
- One **EnergyDomain**: `ELEC` (electricity)
- Four **EnergyCarrier** definitions: `Electricity`, `Gas`, `Water`, `Uranium`
- Six **GeographicalRegion** objects: CH, DE, FR, IT, AT, LI
- Six **ElectricityNode** electricity buses: one per country
- Six **EnergyDemand** objects: one aggregated annual demand per country
- Generator fleets per country as **EnergyConversionTechnology1x1**:
  - Gas → Electricity (all countries)
  - Water → Electricity (all countries)
  - Uranium → Electricity (where applicable)
- Cross-border interconnectors as **NetTransferCapacity** from CH to each neighbour

---

## Step 1: Create the top-level container

```python
m.add_entity(entity_class="EnergySystemModel", entity_id="CH_NEIGHBOURS")
m.add_attribute(entity_id="CH_NEIGHBOURS", attribute_id="long_name", value="CH + neighbours (electricity only) demo")
m.add_attribute(entity_id="CH_NEIGHBOURS", attribute_id="co2_price", value=120.0)
```

---

## Step 2: Define carriers (Electricity, Gas, Water, Uranium)

Each energy carrier is a first-class entity of type `EnergyCarrier`.

```python
# Electricity
m.add_entity(entity_class="EnergyCarrier", entity_id="Electricity")
m.add_attribute(entity_id="Electricity", attribute_id="name", value="Electricity")
m.add_attribute(entity_id="Electricity", attribute_id="energy_carrier_type", value="DOMAIN")
m.add_attribute(entity_id="Electricity", attribute_id="energy_carrier_cost", value=0.0)
m.add_attribute(entity_id="Electricity", attribute_id="co2_emission_intensity", value=0.0)

# Gas
m.add_entity(entity_class="EnergyCarrier", entity_id="Gas")
m.add_attribute(entity_id="Gas", attribute_id="name", value="Gas")
m.add_attribute(entity_id="Gas", attribute_id="energy_carrier_type", value="FUEL")
m.add_attribute(entity_id="Gas", attribute_id="energy_carrier_cost", value=50.0)
m.add_attribute(entity_id="Gas", attribute_id="co2_emission_intensity", value=0.20)

# Water
m.add_entity(entity_class="EnergyCarrier", entity_id="Water")
m.add_attribute(entity_id="Water", attribute_id="name", value="Water")
m.add_attribute(entity_id="Water", attribute_id="energy_carrier_type", value="RESOURCE")
m.add_attribute(entity_id="Water", attribute_id="energy_carrier_cost", value=5.0)
m.add_attribute(entity_id="Water", attribute_id="co2_emission_intensity", value=0.0)

# Uranium
m.add_entity(entity_class="EnergyCarrier", entity_id="Uranium")
m.add_attribute(entity_id="Uranium", attribute_id="name", value="Uranium")
m.add_attribute(entity_id="Uranium", attribute_id="energy_carrier_type", value="FUEL")
m.add_attribute(entity_id="Uranium", attribute_id="energy_carrier_cost", value=10.0)
m.add_attribute(entity_id="Uranium", attribute_id="co2_emission_intensity", value=0.0)
```

---

## Step 3: Define the electricity domain

The `EnergyDomain` groups carriers and is used to tag nodes and interconnectors.

```python
m.add_entity(entity_class="EnergyDomain", entity_id="ELEC")
m.add_attribute(entity_id="ELEC", attribute_id="name", value="Electricity")
m.add_relation(entity_id="ELEC", relation_id="hasEnergyCarrier", target_entity_id="Electricity")
```

---

## Step 4: Add regions (GeographicalRegion)

```python
m.add_entity(entity_class="GeographicalRegion", entity_id="R_CH")
m.add_attribute(entity_id="R_CH", attribute_id="name", value="Switzerland")

m.add_entity(entity_class="GeographicalRegion", entity_id="R_DE")
m.add_attribute(entity_id="R_DE", attribute_id="name", value="Germany")

m.add_entity(entity_class="GeographicalRegion", entity_id="R_FR")
m.add_attribute(entity_id="R_FR", attribute_id="name", value="France")

m.add_entity(entity_class="GeographicalRegion", entity_id="R_IT")
m.add_attribute(entity_id="R_IT", attribute_id="name", value="Italy")

m.add_entity(entity_class="GeographicalRegion", entity_id="R_AT")
m.add_attribute(entity_id="R_AT", attribute_id="name", value="Austria")

m.add_entity(entity_class="GeographicalRegion", entity_id="R_LI")
m.add_attribute(entity_id="R_LI", attribute_id="name", value="Liechtenstein")
```

---

## Step 5: Add nodes (ElectricityNode)

Each node is linked to:
- the electricity domain (`isInEnergyDomain`)
- its geographical region (`isInGeographicalRegion`)

```python
m.add_entity(entity_class="ElectricityNode", entity_id="N_CH")
m.add_attribute(entity_id="N_CH", attribute_id="name", value="CH electricity bus")
m.add_attribute(entity_id="N_CH", attribute_id="nominal_voltage", value=220.0)
m.add_relation(entity_id="N_CH", relation_id="isInEnergyDomain", target_entity_id="ELEC")
m.add_relation(entity_id="N_CH", relation_id="isInGeographicalRegion", target_entity_id="R_CH")

m.add_entity(entity_class="ElectricityNode", entity_id="N_DE")
m.add_attribute(entity_id="N_DE", attribute_id="name", value="DE electricity bus")
m.add_attribute(entity_id="N_DE", attribute_id="nominal_voltage", value=220.0)
m.add_relation(entity_id="N_DE", relation_id="isInEnergyDomain", target_entity_id="ELEC")
m.add_relation(entity_id="N_DE", relation_id="isInGeographicalRegion", target_entity_id="R_DE")

m.add_entity(entity_class="ElectricityNode", entity_id="N_FR")
m.add_attribute(entity_id="N_FR", attribute_id="name", value="FR electricity bus")
m.add_attribute(entity_id="N_FR", attribute_id="nominal_voltage", value=220.0)
m.add_relation(entity_id="N_FR", relation_id="isInEnergyDomain", target_entity_id="ELEC")
m.add_relation(entity_id="N_FR", relation_id="isInGeographicalRegion", target_entity_id="R_FR")

m.add_entity(entity_class="ElectricityNode", entity_id="N_IT")
m.add_attribute(entity_id="N_IT", attribute_id="name", value="IT electricity bus")
m.add_attribute(entity_id="N_IT", attribute_id="nominal_voltage", value=220.0)
m.add_relation(entity_id="N_IT", relation_id="isInEnergyDomain", target_entity_id="ELEC")
m.add_relation(entity_id="N_IT", relation_id="isInGeographicalRegion", target_entity_id="R_IT")

m.add_entity(entity_class="ElectricityNode", entity_id="N_AT")
m.add_attribute(entity_id="N_AT", attribute_id="name", value="AT electricity bus")
m.add_attribute(entity_id="N_AT", attribute_id="nominal_voltage", value=220.0)
m.add_relation(entity_id="N_AT", relation_id="isInEnergyDomain", target_entity_id="ELEC")
m.add_relation(entity_id="N_AT", relation_id="isInGeographicalRegion", target_entity_id="R_AT")

m.add_entity(entity_class="ElectricityNode", entity_id="N_LI")
m.add_attribute(entity_id="N_LI", attribute_id="name", value="LI electricity bus")
m.add_attribute(entity_id="N_LI", attribute_id="nominal_voltage", value=220.0)
m.add_relation(entity_id="N_LI", relation_id="isInEnergyDomain", target_entity_id="ELEC")
m.add_relation(entity_id="N_LI", relation_id="isInGeographicalRegion", target_entity_id="R_LI")
```

---

## Step 6: Add loads (EnergyDemand)

```python
m.add_entity(entity_class="EnergyDemand", entity_id="L_CH")
m.add_attribute(entity_id="L_CH", attribute_id="name", value="CH aggregate load")
m.add_attribute(entity_id="L_CH", attribute_id="annual_energy_demand", value=60e6)
m.add_relation(entity_id="L_CH", relation_id="isConnectedToNode", target_entity_id="N_CH")

m.add_entity(entity_class="EnergyDemand", entity_id="L_DE")
m.add_attribute(entity_id="L_DE", attribute_id="name", value="DE aggregate load")
m.add_attribute(entity_id="L_DE", attribute_id="annual_energy_demand", value=500e6)
m.add_relation(entity_id="L_DE", relation_id="isConnectedToNode", target_entity_id="N_DE")

m.add_entity(entity_class="EnergyDemand", entity_id="L_FR")
m.add_attribute(entity_id="L_FR", attribute_id="name", value="FR aggregate load")
m.add_attribute(entity_id="L_FR", attribute_id="annual_energy_demand", value=450e6)
m.add_relation(entity_id="L_FR", relation_id="isConnectedToNode", target_entity_id="N_FR")

m.add_entity(entity_class="EnergyDemand", entity_id="L_IT")
m.add_attribute(entity_id="L_IT", attribute_id="name", value="IT aggregate load")
m.add_attribute(entity_id="L_IT", attribute_id="annual_energy_demand", value=300e6)
m.add_relation(entity_id="L_IT", relation_id="isConnectedToNode", target_entity_id="N_IT")

m.add_entity(entity_class="EnergyDemand", entity_id="L_AT")
m.add_attribute(entity_id="L_AT", attribute_id="name", value="AT aggregate load")
m.add_attribute(entity_id="L_AT", attribute_id="annual_energy_demand", value=70e6)
m.add_relation(entity_id="L_AT", relation_id="isConnectedToNode", target_entity_id="N_AT")

m.add_entity(entity_class="EnergyDemand", entity_id="L_LI")
m.add_attribute(entity_id="L_LI", attribute_id="name", value="LI aggregate load")
m.add_attribute(entity_id="L_LI", attribute_id="annual_energy_demand", value=1e6)
m.add_relation(entity_id="L_LI", relation_id="isConnectedToNode", target_entity_id="N_LI")
```

---


## Step 7: Add generator fleets (EnergyConversionTechnology1x1)

Generator fleets are represented with `EnergyConversionTechnology1x1` entities.
Each fleet converts **one input carrier** into **one output carrier** and injects
electricity into a **ElectricityNode** (`isOutputNodeOf`).

In `example_ch_and_neighbours.py`, each country gets:

- one **gas** fleet: Gas → Electricity
- one **hydro** fleet: Water → Electricity (with an annual resource potential)
- a **nuclear** fleet: Uranium → Electricity (only where capacity > 0)

Below, *all* generator fleets from the script are shown **one by one** (entities,
attributes, relations).

---

### Note on hydro modelling: run-of-river vs reservoir hydro

In this example file, hydro generation is represented as an **energy conversion**
(`EnergyConversionTechnology1x1`: Water → Electricity) with an
`annual_resource_potential`. This corresponds to **run-of-river** (or more
generally, energy-limited generation) where water availability limits *how much*
can be produced, but there is **no explicit storage state** (no reservoir level
or state-of-charge).

If you want to model **hydro reservoirs** (i.e., water can be stored and shifted
over time), CESDM would typically represent the reservoir as an
**`EnergyStorageTechnology`**, because a reservoir introduces an inter-temporal
energy state (stored water / potential energy) and charging–discharging decisions.

A practical modelling guideline is:

- **Run-of-river hydro** → `EnergyConversionTechnology1x1` (Water → Electricity)
- **Reservoir hydro / pumped storage** → `EnergyStorageTechnology` (storage with state)

> 💡 In CESDM terms: if water affects *when* electricity can be produced, you need storage.



> 💡 Naming convention  
> `G_<COUNTRY>_<TECH>` where TECH is `GAS`, `HYD`, or `NUC`.

---

### Switzerland (CH)

#### CH gas fleet (Gas → Electricity)

```python
m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_CH_GAS")
m.add_attribute(entity_id="G_CH_GAS", attribute_id="name", value="CH gas fleet")
m.add_attribute(entity_id="G_CH_GAS", attribute_id="energy_conversion_efficiency", value=0.55)
m.add_attribute(entity_id="G_CH_GAS", attribute_id="generator_technology_type", value="gas")
m.add_attribute(entity_id="G_CH_GAS", attribute_id="nominal_power_capacity", value=3000.0)
m.add_attribute(entity_id="G_CH_GAS", attribute_id="input_origin", value="exogenous")

m.add_relation(entity_id="G_CH_GAS", relation_id="isOutputNodeOf", target_entity_id="N_CH")
m.add_relation(entity_id="G_CH_GAS", relation_id="hasInputEnergyCarrier", target_entity_id="Gas")
m.add_relation(entity_id="G_CH_GAS", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
```

#### CH hydro fleet (Water → Electricity)

```python
m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_CH_HYD")
m.add_attribute(entity_id="G_CH_HYD", attribute_id="name", value="CH hydro fleet")
m.add_attribute(entity_id="G_CH_HYD", attribute_id="energy_conversion_efficiency", value=0.90)
m.add_attribute(entity_id="G_CH_HYD", attribute_id="generator_technology_type", value="hydro")
m.add_attribute(entity_id="G_CH_HYD", attribute_id="nominal_power_capacity", value=8000.0)
m.add_attribute(entity_id="G_CH_HYD", attribute_id="annual_resource_potential", value=40000000.0)
m.add_attribute(entity_id="G_CH_HYD", attribute_id="input_origin", value="exogenous")

m.add_relation(entity_id="G_CH_HYD", relation_id="isOutputNodeOf", target_entity_id="N_CH")
m.add_relation(entity_id="G_CH_HYD", relation_id="hasInputEnergyCarrier", target_entity_id="Water")
m.add_relation(entity_id="G_CH_HYD", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
```

#### CH nuclear fleet (Uranium → Electricity)

```python
m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_CH_NUC")
m.add_attribute(entity_id="G_CH_NUC", attribute_id="name", value="CH nuclear fleet")
m.add_attribute(entity_id="G_CH_NUC", attribute_id="energy_conversion_efficiency", value=0.33)
m.add_attribute(entity_id="G_CH_NUC", attribute_id="generator_technology_type", value="nuclear")
m.add_attribute(entity_id="G_CH_NUC", attribute_id="nominal_power_capacity", value=2000.0)
m.add_attribute(entity_id="G_CH_NUC", attribute_id="input_origin", value="exogenous")

m.add_relation(entity_id="G_CH_NUC", relation_id="isOutputNodeOf", target_entity_id="N_CH")
m.add_relation(entity_id="G_CH_NUC", relation_id="hasInputEnergyCarrier", target_entity_id="Uranium")
m.add_relation(entity_id="G_CH_NUC", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
```

---

### Germany (DE)

#### DE gas fleet (Gas → Electricity)

```python
m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_DE_GAS")
m.add_attribute(entity_id="G_DE_GAS", attribute_id="name", value="DE gas fleet")
m.add_attribute(entity_id="G_DE_GAS", attribute_id="energy_conversion_efficiency", value=0.55)
m.add_attribute(entity_id="G_DE_GAS", attribute_id="generator_technology_type", value="gas")
m.add_attribute(entity_id="G_DE_GAS", attribute_id="nominal_power_capacity", value=6000.0)
m.add_attribute(entity_id="G_DE_GAS", attribute_id="input_origin", value="exogenous")

m.add_relation(entity_id="G_DE_GAS", relation_id="isOutputNodeOf", target_entity_id="N_DE")
m.add_relation(entity_id="G_DE_GAS", relation_id="hasInputEnergyCarrier", target_entity_id="Gas")
m.add_relation(entity_id="G_DE_GAS", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
```

#### DE hydro fleet (Water → Electricity)

```python
m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_DE_HYD")
m.add_attribute(entity_id="G_DE_HYD", attribute_id="name", value="DE hydro fleet")
m.add_attribute(entity_id="G_DE_HYD", attribute_id="energy_conversion_efficiency", value=0.90)
m.add_attribute(entity_id="G_DE_HYD", attribute_id="generator_technology_type", value="hydro")
m.add_attribute(entity_id="G_DE_HYD", attribute_id="nominal_power_capacity", value=2000.0)
m.add_attribute(entity_id="G_DE_HYD", attribute_id="annual_resource_potential", value=10000000.0)
m.add_attribute(entity_id="G_DE_HYD", attribute_id="input_origin", value="exogenous")

m.add_relation(entity_id="G_DE_HYD", relation_id="isOutputNodeOf", target_entity_id="N_DE")
m.add_relation(entity_id="G_DE_HYD", relation_id="hasInputEnergyCarrier", target_entity_id="Water")
m.add_relation(entity_id="G_DE_HYD", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
```

---

### France (FR)

#### FR gas fleet (Gas → Electricity)

```python
m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_FR_GAS")
m.add_attribute(entity_id="G_FR_GAS", attribute_id="name", value="FR gas fleet")
m.add_attribute(entity_id="G_FR_GAS", attribute_id="energy_conversion_efficiency", value=0.55)
m.add_attribute(entity_id="G_FR_GAS", attribute_id="generator_technology_type", value="gas")
m.add_attribute(entity_id="G_FR_GAS", attribute_id="nominal_power_capacity", value=4000.0)
m.add_attribute(entity_id="G_FR_GAS", attribute_id="input_origin", value="exogenous")

m.add_relation(entity_id="G_FR_GAS", relation_id="isOutputNodeOf", target_entity_id="N_FR")
m.add_relation(entity_id="G_FR_GAS", relation_id="hasInputEnergyCarrier", target_entity_id="Gas")
m.add_relation(entity_id="G_FR_GAS", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
```

#### FR hydro fleet (Water → Electricity)

```python
m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_FR_HYD")
m.add_attribute(entity_id="G_FR_HYD", attribute_id="name", value="FR hydro fleet")
m.add_attribute(entity_id="G_FR_HYD", attribute_id="energy_conversion_efficiency", value=0.90)
m.add_attribute(entity_id="G_FR_HYD", attribute_id="generator_technology_type", value="hydro")
m.add_attribute(entity_id="G_FR_HYD", attribute_id="nominal_power_capacity", value=2000.0)
m.add_attribute(entity_id="G_FR_HYD", attribute_id="annual_resource_potential", value=15000000.0)
m.add_attribute(entity_id="G_FR_HYD", attribute_id="input_origin", value="exogenous")

m.add_relation(entity_id="G_FR_HYD", relation_id="isOutputNodeOf", target_entity_id="N_FR")
m.add_relation(entity_id="G_FR_HYD", relation_id="hasInputEnergyCarrier", target_entity_id="Water")
m.add_relation(entity_id="G_FR_HYD", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
```

#### FR nuclear fleet (Uranium → Electricity)

```python
m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_FR_NUC")
m.add_attribute(entity_id="G_FR_NUC", attribute_id="name", value="FR nuclear fleet")
m.add_attribute(entity_id="G_FR_NUC", attribute_id="energy_conversion_efficiency", value=0.33)
m.add_attribute(entity_id="G_FR_NUC", attribute_id="generator_technology_type", value="nuclear")
m.add_attribute(entity_id="G_FR_NUC", attribute_id="nominal_power_capacity", value=4000.0)
m.add_attribute(entity_id="G_FR_NUC", attribute_id="input_origin", value="exogenous")

m.add_relation(entity_id="G_FR_NUC", relation_id="isOutputNodeOf", target_entity_id="N_FR")
m.add_relation(entity_id="G_FR_NUC", relation_id="hasInputEnergyCarrier", target_entity_id="Uranium")
m.add_relation(entity_id="G_FR_NUC", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
```

---

### Italy (IT)

#### IT gas fleet (Gas → Electricity)

```python
m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_IT_GAS")
m.add_attribute(entity_id="G_IT_GAS", attribute_id="name", value="IT gas fleet")
m.add_attribute(entity_id="G_IT_GAS", attribute_id="energy_conversion_efficiency", value=0.55)
m.add_attribute(entity_id="G_IT_GAS", attribute_id="generator_technology_type", value="gas")
m.add_attribute(entity_id="G_IT_GAS", attribute_id="nominal_power_capacity", value=5000.0)
m.add_attribute(entity_id="G_IT_GAS", attribute_id="input_origin", value="exogenous")

m.add_relation(entity_id="G_IT_GAS", relation_id="isOutputNodeOf", target_entity_id="N_IT")
m.add_relation(entity_id="G_IT_GAS", relation_id="hasInputEnergyCarrier", target_entity_id="Gas")
m.add_relation(entity_id="G_IT_GAS", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
```

#### IT hydro fleet (Water → Electricity)

```python
m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_IT_HYD")
m.add_attribute(entity_id="G_IT_HYD", attribute_id="name", value="IT hydro fleet")
m.add_attribute(entity_id="G_IT_HYD", attribute_id="energy_conversion_efficiency", value=0.90)
m.add_attribute(entity_id="G_IT_HYD", attribute_id="generator_technology_type", value="hydro")
m.add_attribute(entity_id="G_IT_HYD", attribute_id="nominal_power_capacity", value=2000.0)
m.add_attribute(entity_id="G_IT_HYD", attribute_id="annual_resource_potential", value=18000000.0)
m.add_attribute(entity_id="G_IT_HYD", attribute_id="input_origin", value="exogenous")

m.add_relation(entity_id="G_IT_HYD", relation_id="isOutputNodeOf", target_entity_id="N_IT")
m.add_relation(entity_id="G_IT_HYD", relation_id="hasInputEnergyCarrier", target_entity_id="Water")
m.add_relation(entity_id="G_IT_HYD", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
```

---

### Austria (AT)

#### AT gas fleet (Gas → Electricity)

```python
m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_AT_GAS")
m.add_attribute(entity_id="G_AT_GAS", attribute_id="name", value="AT gas fleet")
m.add_attribute(entity_id="G_AT_GAS", attribute_id="energy_conversion_efficiency", value=0.55)
m.add_attribute(entity_id="G_AT_GAS", attribute_id="generator_technology_type", value="gas")
m.add_attribute(entity_id="G_AT_GAS", attribute_id="nominal_power_capacity", value=1000.0)
m.add_attribute(entity_id="G_AT_GAS", attribute_id="input_origin", value="exogenous")

m.add_relation(entity_id="G_AT_GAS", relation_id="isOutputNodeOf", target_entity_id="N_AT")
m.add_relation(entity_id="G_AT_GAS", relation_id="hasInputEnergyCarrier", target_entity_id="Gas")
m.add_relation(entity_id="G_AT_GAS", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
```

#### AT hydro fleet (Water → Electricity)

```python
m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_AT_HYD")
m.add_attribute(entity_id="G_AT_HYD", attribute_id="name", value="AT hydro fleet")
m.add_attribute(entity_id="G_AT_HYD", attribute_id="energy_conversion_efficiency", value=0.90)
m.add_attribute(entity_id="G_AT_HYD", attribute_id="generator_technology_type", value="hydro")
m.add_attribute(entity_id="G_AT_HYD", attribute_id="nominal_power_capacity", value=2000.0)
m.add_attribute(entity_id="G_AT_HYD", attribute_id="annual_resource_potential", value=12000000.0)
m.add_attribute(entity_id="G_AT_HYD", attribute_id="input_origin", value="exogenous")

m.add_relation(entity_id="G_AT_HYD", relation_id="isOutputNodeOf", target_entity_id="N_AT")
m.add_relation(entity_id="G_AT_HYD", relation_id="hasInputEnergyCarrier", target_entity_id="Water")
m.add_relation(entity_id="G_AT_HYD", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
```

---

### Liechtenstein (LI)

#### LI gas fleet (Gas → Electricity)

```python
m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_LI_GAS")
m.add_attribute(entity_id="G_LI_GAS", attribute_id="name", value="LI gas fleet")
m.add_attribute(entity_id="G_LI_GAS", attribute_id="energy_conversion_efficiency", value=0.55)
m.add_attribute(entity_id="G_LI_GAS", attribute_id="generator_technology_type", value="gas")
m.add_attribute(entity_id="G_LI_GAS", attribute_id="nominal_power_capacity", value=200.0)
m.add_attribute(entity_id="G_LI_GAS", attribute_id="input_origin", value="exogenous")

m.add_relation(entity_id="G_LI_GAS", relation_id="isOutputNodeOf", target_entity_id="N_LI")
m.add_relation(entity_id="G_LI_GAS", relation_id="hasInputEnergyCarrier", target_entity_id="Gas")
m.add_relation(entity_id="G_LI_GAS", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
```

#### LI hydro fleet (Water → Electricity)

```python
m.add_entity(entity_class="EnergyConversionTechnology1x1", entity_id="G_LI_HYD")
m.add_attribute(entity_id="G_LI_HYD", attribute_id="name", value="LI hydro fleet")
m.add_attribute(entity_id="G_LI_HYD", attribute_id="energy_conversion_efficiency", value=0.90)
m.add_attribute(entity_id="G_LI_HYD", attribute_id="generator_technology_type", value="hydro")
m.add_attribute(entity_id="G_LI_HYD", attribute_id="nominal_power_capacity", value=200.0)
m.add_attribute(entity_id="G_LI_HYD", attribute_id="annual_resource_potential", value=500000.0)
m.add_attribute(entity_id="G_LI_HYD", attribute_id="input_origin", value="exogenous")

m.add_relation(entity_id="G_LI_HYD", relation_id="isOutputNodeOf", target_entity_id="N_LI")
m.add_relation(entity_id="G_LI_HYD", relation_id="hasInputEnergyCarrier", target_entity_id="Water")
m.add_relation(entity_id="G_LI_HYD", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
```


## Step 8: Add interconnectors (NetTransferCapacity)

Interconnectors connect **CH** to each neighbour using `NetTransferCapacity`.

### Example: CH–DE NTC

```python
m.add_entity(entity_class="NetTransferCapacity", entity_id="NTC_CH_DE")
m.add_attribute(entity_id="NTC_CH_DE", attribute_id="name", value="NTC CH-DE")
m.add_attribute(entity_id="NTC_CH_DE", attribute_id="maximum_power_flow_1_to_2", value=6000.0)
m.add_attribute(entity_id="NTC_CH_DE", attribute_id="maximum_power_flow_2_to_1", value=6000.0)

m.add_relation(entity_id="NTC_CH_DE", relation_id="isFromNodeOf", target_entity_id="N_CH")
m.add_relation(entity_id="NTC_CH_DE", relation_id="isToNodeOf", target_entity_id="N_DE")
m.add_relation(entity_id="NTC_CH_DE", relation_id="isInEnergyDomain", target_entity_id="ELEC")
```

The script repeats this pattern for FR, IT, AT, and LI with different capacities.

---

## Step 9: Validate and export

```python
errors = m.validate()
if errors:
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

m.export_yaml("ch_and_neighbours.yaml")
```

---

## Key takeaway

This example shows the most explicit way of using CESDM:
you can construct a full multi-region electricity model **purely by calling**
`add_entity`, `add_attribute`, and `add_relation`.

---

## Optional extension: representing hydro reservoirs (storage)

The base example (`example_ch_and_neighbours.py`) does **not** include storage.
Hydro is modelled as conversion (Water → Electricity), corresponding to
run-of-river or energy-limited generation.

If your CESDM schemas include `EnergyStorageTechnology`, reservoir hydro can be
modelled explicitly as **storage**, introducing an inter-temporal energy state
(reservoir level).

> ⚠️ This section is optional and schema-dependent.  
> If `EnergyStorageTechnology` is not defined in your schemas, validation will fail.

---

### Conceptual role of reservoir hydro

A hydro reservoir:
- Stores potential energy (water) over time
- Can shift electricity generation temporally
- Requires a state of charge (reservoir level)

In CESDM, this corresponds naturally to an `EnergyStorageTechnology`.

---

### Example: CH hydro reservoir (storage)

```python
# Create reservoir storage
m.add_entity(entity_class="EnergyStorageTechnology", entity_id="S_CH_HYD")

# Attributes (state and power limits) — names must match your schema
m.add_attribute(entity_id="S_CH_HYD", attribute_id="name", value="CH hydro reservoir")
m.add_attribute(entity_id="S_CH_HYD", attribute_id="energy_storage_capacity", value=20000000.0)
m.add_attribute(entity_id="S_CH_HYD", attribute_id="charging_power_capacity", value=5000.0)
m.add_attribute(entity_id="S_CH_HYD", attribute_id="discharging_power_capacity", value=5000.0)
m.add_attribute(entity_id="S_CH_HYD", attribute_id="charging_efficiency", value=0.95)
m.add_attribute(entity_id="S_CH_HYD", attribute_id="discharging_efficiency", value=0.90)
m.add_attribute(entity_id="S_CH_HYD", attribute_id="initial_state_of_charge", value=0.50)

# Relations — names must match your schema
m.add_relation(entity_id="S_CH_HYD", relation_id="isInGeographicalRegion", target_entity_id="R_CH")
m.add_relation(entity_id="S_CH_HYD", relation_id="isInEnergyDomain", target_entity_id="ELEC")
m.add_relation(entity_id="S_CH_HYD", relation_id="hasInputEnergyCarrier", target_entity_id="Water")
m.add_relation(entity_id="S_CH_HYD", relation_id="hasOutputEnergyCarrier", target_entity_id="Electricity")
m.add_relation(entity_id="S_CH_HYD", relation_id="isOutputNodeOf", target_entity_id="N_CH")
```

---

### When to use `EnergyStorageTechnology`

Use storage **only if** you need:
- Inter-temporal optimisation (shifting generation across time)
- Reservoir level constraints
- Seasonal or pumped storage behaviour

If water availability only limits *how much* electricity can be produced (without
time-shifting), the conversion-based modelling used in the main example is
sufficient.
