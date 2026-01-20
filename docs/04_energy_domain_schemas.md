# Energy Domain Schemas (CESDM)

This document describes the **energy-domain–specific schemas** provided by CESDM.
It explains the purpose, attributes, and relations of each core entity used to
build energy system models.

The focus is on **electricity, gas, heat, and multi-energy systems**, as used in
the provided examples.

---

## 1. EnergySystemModel

### Purpose
`EnergySystemModel` is the **root container** of a CESDM model.  
All other entities exist *within* this model.

### Typical attributes
| Attribute | Meaning |
|---------|--------|
| `long_name` | Human-readable model description |
| `co2_price` | CO₂ price applied to emissions (if used) |

---

## 2. EnergyDomain

### Purpose
An `EnergyDomain` groups components operating on the **same physical carrier**
(e.g. electricity, heat, gas).

### Typical attributes
| Attribute | Meaning |
|---------|--------|
| `name` | Domain name |

### Relations
| Relation | Target | Meaning |
|--------|--------|--------|
| `hasEnergyCarrier` | EnergyCarrier | Carrier defining the domain |

---

## 3. EnergyCarrier

### Purpose
`EnergyCarrier` represents a **physical energy carrier** such as electricity,
gas, heat, water, or hydrogen.

### Typical attributes
| Attribute | Meaning |
|---------|--------|
| `name` | Carrier name |
| `energy_carrier_type` | DOMAIN / FUEL / RESOURCE |
| `energy_carrier_cost` | Cost per energy unit |
| `co2_emission_intensity` | Emissions per energy unit |

---

## 4. GeographicalRegion

### Purpose
Represents a **spatial region** (country, zone, node aggregation).

### Typical attributes
| Attribute | Meaning |
|---------|--------|
| `name` | Region name |

---

## 5. EnergyNode / GridNode

### Purpose
Represents a **network node** where energy is exchanged.

### Typical attributes
| Attribute | Meaning |
|---------|--------|
| `name` | Node name |
| `nominal_voltage` | Voltage level (electricity only) |

### Relations
| Relation | Target | Meaning |
|--------|--------|--------|
| `isInEnergyDomain` | EnergyDomain | Domain of operation |
| `isInGeographicalRegion` | GeographicalRegion | Spatial location |

---

## 6. EnergyDemand

### Purpose
Represents **exogenous energy demand** connected to a node.

### Typical attributes
| Attribute | Meaning |
|---------|--------|
| `name` | Demand name |
| `annual_energy_demand` | Total annual demand |

### Relations
| Relation | Target | Meaning |
|--------|--------|--------|
| `isConnectedToNode` | EnergyNode | Where demand is drawn |

---

## 7. EnergyConversionTechnology1x1

### Purpose
Represents a technology converting **one input carrier to one output carrier**.

### Typical attributes
| Attribute | Meaning |
|---------|--------|
| `energy_conversion_efficiency` | Conversion efficiency |
| `nominal_power_capacity` | Installed capacity |
| `generator_technology_type` | Technology label |
| `annual_resource_potential` | Energy-limited potential |

### Relations
| Relation | Target | Meaning |
|--------|--------|--------|
| `hasInputEnergyCarrier` | EnergyCarrier | Input |
| `hasOutputEnergyCarrier` | EnergyCarrier | Output |
| `isOutputNodeOf` | EnergyNode | Injection node |

---

## 8. EnergyStorageTechnology

### Purpose
Represents technologies with **energy storage and temporal shifting** capability.

### Typical attributes
| Attribute | Meaning |
|---------|--------|
| `energy_storage_capacity` | Max stored energy |
| `charging_power_capacity` | Charging limit |
| `discharging_power_capacity` | Discharging limit |
| `charging_efficiency` | Charging efficiency |
| `discharging_efficiency` | Discharging efficiency |
| `initial_state_of_charge` | Initial SOC |

### Relations
| Relation | Target | Meaning |
|--------|--------|--------|
| `hasInputEnergyCarrier` | EnergyCarrier | Stored carrier |
| `hasOutputEnergyCarrier` | EnergyCarrier | Delivered carrier |
| `isOutputNodeOf` | EnergyNode | Discharge node |

---

## 9. NetTransferCapacity

### Purpose
Represents **transmission limits** between two nodes.

### Typical attributes
| Attribute | Meaning |
|---------|--------|
| `maximum_power_flow_1_to_2` | Forward capacity |
| `maximum_power_flow_2_to_1` | Reverse capacity |

### Relations
| Relation | Target | Meaning |
|--------|--------|--------|
| `isFromNodeOf` | EnergyNode | From |
| `isToNodeOf` | EnergyNode | To |

---

## 10. CombinedHeatandPowerPlant

### Purpose
Represents **multi-output conversion** (fuel → electricity + heat).

### Typical attributes
| Attribute | Meaning |
|---------|--------|
| `net_electrical_efficiency` | Electrical efficiency |
| `net_thermal_efficiency` | Thermal efficiency |
| `rated_electrical_power_capacity` | Electrical capacity |
| `rated_thermal_output_capacity` | Thermal capacity |

### Relations
| Relation | Target |
|--------|--------|
| `hasFuelCarrier` | EnergyCarrier |
| `hasElectricityAsCarrier` | EnergyCarrier |
| `hasHeatAsCarrier` | EnergyCarrier |
| `isFuelInputNodeOf` | EnergyNode |
| `isElectricityOutputNodeOf` | EnergyNode |
| `isHeatOutputNodeOf` | EnergyNode |

---

## Summary

This document provides a **conceptual reference** for the CESDM energy-domain
schemas and how they are used to build consistent, validated energy system models.
