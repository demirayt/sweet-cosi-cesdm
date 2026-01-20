# System Example Description: Switzerland (CH) and Neighbouring Countries

This worked example describes and constructs a **stylised electricity system**
covering Switzerland and its neighbouring countries. It combines:

- A **conceptual system description**
- **Tabulated input data**
- A **step-by-step CESDM construction walkthrough**

The example is based on `example_ch_and_neighbours.py` and focuses on
**structure and schema usage**, not data realism.

---

## 1. System scope and intent

The system represents:

- A single **electricity energy domain**
- Six countries: CH, DE, FR, IT, AT, LI
- Aggregated annual demand and generation capacities
- Cross-border electricity trade via Net Transfer Capacities (NTCs)
- Hydro generation and storage

The example demonstrates:
- Multi-region modelling
- Conversion and storage technologies
- Explicit spatial structure
- Schema-driven validation

---

## 2. Geographical regions

Each country is represented as a `GeographicalRegion`.

| Code | Country |
|------|---------|
| CH | Switzerland |
| DE | Germany |
| FR | France |
| IT | Italy |
| AT | Austria |
| LI | Liechtenstein |

---

## 3. Energy carriers

| Carrier | Type | Description |
|--------|------|-------------|
| Electricity | DOMAIN | Delivered electricity |
| Gas | FUEL | Fossil fuel for thermal generation |
| Water | RESOURCE | Renewable hydro resource |
| Uranium | FUEL | Nuclear fuel |

---

## 4. Electricity network (ElectricityNode)

Each region is represented by one aggregated electricity node.

| Node ID | Region | Nominal voltage (kV) |
|--------|--------|----------------------|
| N_CH | CH | 220 |
| N_DE | DE | 220 |
| N_FR | FR | 220 |
| N_IT | IT | 220 |
| N_AT | AT | 220 |
| N_LI | LI | 220 |

---

## 5. Electricity demand (EnergyDemand)

Annual aggregated electricity demand per country.

| Load ID | Region | Annual demand (GWh) |
|--------|--------|---------------------|
| L_CH | CH | 60 000 |
| L_DE | DE | 500 000 |
| L_FR | FR | 450 000 |
| L_IT | IT | 300 000 |
| L_AT | AT | 70 000 |
| L_LI | LI | 1 000 |

---

## 6. Generation technologies (EnergyConversionTechnology1x1)

### Gas-fired generation (Gas → Electricity)

| Entity ID | Region | Capacity (MW) | Efficiency |
|----------|--------|---------------|------------|
| G_CH_GAS | CH | 3 000 | 0.55 |
| G_DE_GAS | DE | 6 000 | 0.55 |
| G_FR_GAS | FR | 4 000 | 0.55 |
| G_IT_GAS | IT | 5 000 | 0.55 |
| G_AT_GAS | AT | 1 000 | 0.55 |
| G_LI_GAS | LI | 200 | 0.55 |

### Run-of-river hydro (Water → Electricity)

| Entity ID | Region | Capacity (MW) | Annual potential (GWh) |
|----------|--------|---------------|------------------------|
| G_CH_HYD | CH | 8 000 | 40 000 |
| G_DE_HYD | DE | 2 000 | 10 000 |
| G_FR_HYD | FR | 2 000 | 15 000 |
| G_IT_HYD | IT | 2 000 | 18 000 |
| G_AT_HYD | AT | 2 000 | 12 000 |
| G_LI_HYD | LI | 200 | 500 |

### Nuclear generation (Uranium → Electricity)

| Entity ID | Region | Capacity (MW) | Efficiency |
|----------|--------|---------------|------------|
| G_CH_NUC | CH | 2 000 | 0.33 |
| G_FR_NUC | FR | 4 000 | 0.33 |

---

## 7. Storage technologies (EnergyStorageTechnology)

Switzerland includes one aggregated hydro reservoir.

| Attribute | Value |
|----------|-------|
| Entity ID | S_CH_HYD |
| Storage capacity | 20 000 GWh |
| Charging power | 5 000 MW |
| Discharging power | 5 000 MW |
| Charging efficiency | 0.95 |
| Discharging efficiency | 0.90 |
| Initial state of charge | 50 % |

This storage enables **inter-temporal shifting** of hydro energy.

---

## 8. Cross-border transmission (NetTransferCapacity)

| Interconnector | From | To | Capacity (MW) |
|----------------|------|----|---------------|
| NTC_CH_DE | CH | DE | 6 000 |
| NTC_CH_FR | CH | FR | 6 000 |
| NTC_CH_IT | CH | IT | 6 000 |
| NTC_CH_AT | CH | AT | 6 000 |
| NTC_CH_LI | CH | LI | 1 000 |

---

## 9. Mapping to CESDM concepts

| System element | CESDM entity |
|---------------|-------------|
| Country | GeographicalRegion |
| Electricity bus | ElectricityNode |
| Demand | EnergyDemand |
| Generation | EnergyConversionTechnology1x1 |
| Hydro reservoir | EnergyStorageTechnology |
| Interconnector | NetTransferCapacity |

---

## 10. Next steps

After defining the system conceptually and numerically, the following sections
of this example show **how each entity, attribute, and relation is created
explicitly using CESDM’s API** and validated against the schemas.
