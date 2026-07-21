# Glossary

All technical terms that appear in the CESDM documentation — explained in
plain language.

---

**Attribute**
A named property of an entity with a value and a unit.
Example: `nominal_power_capacity = 450 MW`. Attributes describe what
an entity is like.

**AVR** (Automatic Voltage Regulator)
Voltage controller of a generator. Keeps the generator terminal voltage
at a setpoint by adjusting the excitation current. Part of the dynamic
model parameters.

**Bus / Grid node** (ElectricalBus)
A point in the electricity network where energy is injected, withdrawn,
or forwarded. The "junction" of the network graph.

**CarrierDomain** (Carrier domain)
A network that transports exactly one energy carrier. The electricity domain
transports electricity, the gas domain transports gas. Assets that connect
two domains are called conversion units.

**Capacity factor**
The ratio of actual energy produced to the maximum possible energy
(if the plant ran at full power the entire time). A capacity factor of 0.3
means the plant produced 30% of its theoretical maximum.

**ConversionUnit** (Conversion asset)
An asset that transforms one energy carrier into another.
Examples: heat pump (electricity → heat), electrolyser (electricity → hydrogen),
gas turbine (gas → electricity).

**DemandUnit** (Demand asset)
A consumer in the energy system. Withdraws energy from the network.

**dispatchable**
A power plant whose output the operator can freely choose (within technical
limits). Opposite: `nondispatchable`.

**EnergyCarrier** (Energy carrier)
A transported commodity inside an explicit network: electricity, natural gas, hydrogen, heat, CO₂, etc. Wind, solar irradiation and water inflow are `NaturalResource`, not `EnergyCarrier`.

**Entity**
A named, uniquely identified object in the energy system: power plant,
grid node, storage facility, region, energy carrier, and so on.

**Frictionless Data Package**
An open standard for self-describing data packages. Consists of CSV tables
and a JSON description file.

**GenerationUnit** (Generation asset)
An asset that feeds energy from an external source into the system.
Examples: wind farm, photovoltaics, nuclear power plant.

**GeographicalRegion**
A geographic region in the model (country, canton, NUTS region).

**GOV** (Turbine Governor)
Turbine speed controller. Keeps grid frequency (50 Hz) constant.

**HDF5**
File format for large numerical datasets. An HDF5 file can store millions
of numerical values efficiently and with compression.

**Interconnector**
A connection between two grid nodes, typically in different countries.
Transfers electricity across borders.

**ISO 8601**
International standard for date and time formats. `PT1H` means "one hour"
(P = Period, T = Time, 1H = 1 Hour). PT15M = 15 minutes. PT30M = 30 minutes.


**NaturalResource**
An exogenous resource that enters the model from outside the explicit carrier network. Examples: wind, solar irradiation, river inflow and reservoir water. Assets link to these with `hasInputResource` or `storesResource`.

**NUTS**
Nomenclature of Territorial Units for Statistics — the European territorial
classification system. NUTS3 = district, NUTS2 = region, NUTS1 = federal
state or large region.

**nondispatchable**
A generation asset whose output depends on an external source (wind, sun).
The operator can shut it down, but cannot produce beyond what the resource
provides.

**NTC** (Net Transfer Capacity)
Maximum electrical power that can be transferred across a border.

**per unit (pu)**
Normalised dimensionless unit. 1.0 pu = the rated/nominal value.
Example: 1.05 pu voltage = 5% above rated voltage.

**PQ bus**
A grid node in a load flow calculation where active and reactive power are
given (typical: load bus, passive network node).

**Profile**
A metadata entity describing a time series (type, unit, time axis). The
actual numerical values are stored in a separate HDF5 file.

**PSS** (Power System Stabilizer)
Network oscillation damper. Damps slow power oscillations (0.1–2 Hz)
between generators and network regions.

**PV bus** (NOT photovoltaics!)
A grid node in a load flow calculation where active power and voltage are
given (typical: generator bus with voltage control).
Not to be confused with a photovoltaic plant.

**Relation**
A named, directed link between two entities.
Example: "power plant is connected to grid node".

**representsAsset**
The central relation in CESDM that links a view to the asset it describes.

**Schema**
A rulebook in a YAML file that defines which entity types, attributes, and
relations exist and which values are valid.

**Slack bus**
The reference node in a load flow calculation. Holds voltage and phase angle
fixed and absorbs all power imbalances.

**StorageUnit** (Storage asset)
An asset that shifts energy in time. Examples: battery, pumped hydro,
thermal storage.

**TimestampSeries**
An entity that describes the time axis: start date, resolution, length, timezone.

**Topology view**
Describes where an asset is connected in the network (to which node).

**TransmissionLine**
An electrical overhead line or cable between two grid nodes.

**YAML**
A simple, human-readable text format for structured data.
Used for CESDM schema files and model files.
