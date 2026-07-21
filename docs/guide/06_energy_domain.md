# Energy Domains as the Organising Principle of CESDM

One of the central design principles of CESDM is that an integrated
energy system is represented as a collection of **interconnected
CarrierDomains**, **EnergyCarriers**, and **NaturalResources** rather than simply as a collection of assets.

This perspective provides a physically meaningful abstraction that
clearly distinguishes between:

-   transporting energy carriers,
-   storing energy carriers or natural resources,
-   injecting or withdrawing energy from a network,
-   converting energy from one carrier into another,
-   using exogenous natural resources such as wind, solar irradiation and water inflow.

By organising the model around energy domains, CESDM provides a
consistent representation that can be applied to electricity systems,
gas networks, district heating systems, hydrogen infrastructures, hydro systems, and integrated multi-energy systems.

## CarrierDomains and EnergyCarriers

A **CarrierDomain** represents a network or infrastructure layer in
which a single type of energy is transported.

Examples include:

-   Electricity domain
-   Natural gas domain
-   Hydrogen domain
-   District heating domain
-   Steam domain

Each CarrierDomain is associated with exactly one **EnergyCarrier**.

The fundamental modelling rule of CESDM is:

> **Each CarrierDomain transports exactly one EnergyCarrier.**
> Natural resources are represented separately as `NaturalResource`; they are not
> attached to CarrierDomain.hasCarrier unless the resource has become an explicit
> transported carrier inside the model boundary.

This simple principle gives every network and every connection a clear
physical interpretation and greatly simplifies validation,
interoperability, and automated consistency checks.

## Assets interact with domains through ports

Assets exchange energy with CarrierDomains through ports.

A port is connected to exactly one CarrierDomain and therefore
implicitly to exactly one EnergyCarrier.

Consequently:

-   a port connected to an electricity domain can only exchange
    electricity,
-   a port connected to a gas domain can only exchange natural gas,
-   a port connected to a heat domain can only exchange heat,
-   a port connected to a hydrogen domain can only exchange hydrogen.

The CarrierDomain therefore determines which type of energy may flow
through the port.

## Transport occurs within a CarrierDomain

Transport assets operate entirely inside a single CarrierDomain.

Typical examples include:

-   electrical transmission and distribution lines,
-   gas pipelines,
-   hydrogen pipelines,
-   district heating pipes,
-   water channels, when water transport is explicitly modelled as infrastructure.

Similarly, Interconnectors connect different regions of the **same**
CarrierDomain while transporting the same EnergyCarrier.

No energy conversion takes place inside these assets. Their purpose is
purely spatial transport.

## Storage also remains inside a CarrierDomain

Generic StorageUnits usually belong to a single CarrierDomain.

A battery stores electricity, a gas cavern stores natural gas, and a
hot-water tank stores heat. These use `storesCarrier`.

Hydraulic reservoir storage is different: a `ReservoirStorageUnit` stores the
`NaturalResource` water and therefore uses `storesResource`. The associated
`HydroGenerationUnit` converts that water resource into electricity.

## ConversionUnits connect different CarrierDomains

While transport and storage remain inside a single CarrierDomain,
**ConversionUnits** connect different CarrierDomains.

They receive one or more EnergyCarriers through input ports and produce
one or more EnergyCarriers through output ports.

Typical examples are:

  Technology        Conversion
  ----------------- --------------------------
  Heat pump         Electricity → Heat
  Electrolyser      Electricity → Hydrogen
  Fuel cell         Hydrogen → Electricity
  CHP plant         Gas → Electricity + Heat
  Electric boiler   Electricity → Heat

The detailed interfaces are represented using `ConversionPort` entities,
which specify:

-   connected CarrierDomain,
-   EnergyCarrier,
-   input/output direction,
-   conversion coefficients,
-   operating limits,
-   and other port-specific parameters.

## GenerationUnits represent exogenous resources

Conceptually, a `GenerationUnit` can be regarded as a specialised form
of conversion.

Its defining characteristic is that the input is an exogenous
`NaturalResource` or an external fuel/carrier outside the chosen model boundary.

Examples include:

  Generation technology   Exogenous input       Output
  ----------------------- --------------------- ---------------------
  Photovoltaics           Solar radiation       Electricity
  Wind turbine            Wind resource         Electricity
  Nuclear power plant     Nuclear fuel          Electricity
  Run-of-river hydro      Natural inflow        Electricity
  Geothermal plant        Geothermal resource   Heat or electricity

The incoming resource is linked with `hasInputResource` when it is a true
NaturalResource, or with `hasInputCarrier` when the modeller wants to annotate
an external fuel carrier directly on the asset. The GenerationUnit injects the
produced energy directly into the corresponding CarrierDomain.

## Endogenous versus exogenous modelling

A major strength of CESDM is that the modelling boundary can be adapted
to the intended application.

### Gas turbine as a GenerationUnit

If the gas system is outside the scope of the study, a gas-fired power
plant may be represented as a `GenerationUnit`.

Gas consumption is implicit and may be annotated with `hasInputCarrier`; the gas network itself is outside the model boundary.

### Gas turbine as a ConversionUnit

If the gas infrastructure is modelled explicitly, the same physical
asset should instead be represented as a `ConversionUnit`.

In this case, natural gas becomes an endogenous EnergyCarrier that can
be:

-   produced,
-   imported,
-   transported,
-   stored,
-   exchanged,
-   and consumed.

The turbine converts energy from the Gas CarrierDomain into the
Electricity CarrierDomain.

This flexibility demonstrates that CESDM distinguishes between
**physical technology** and **modelling boundary**.

## A layered view of integrated energy systems

Within each CarrierDomain:

-   energy is transported,
-   energy is stored,
-   energy is injected,
-   energy is withdrawn.

Between CarrierDomains:

-   energy is converted by ConversionUnits.

GenerationUnits inject energy originating from exogenous resources or external fuels,
whereas ConversionUnits exchange endogenous EnergyCarriers between
explicitly modelled domains.

## Benefits of the CarrierDomain concept

The CarrierDomain philosophy provides several advantages:

-   Physical consistency through one carrier per domain.
-   Clear separation between transport, storage, and conversion.
-   Flexible modelling boundaries.
-   Technology-independent representation.
-   Straightforward extensibility to future carriers.
-   Improved interoperability between energy-system modelling tools.

## Summary

CESDM organises integrated energy systems as interacting CarrierDomains.

Transport assets and StorageUnits operate within a single domain.
ConversionUnits bridge different domains by transforming EnergyCarriers.
GenerationUnits represent a special case where the input is exogenous and therefore does not require an explicitly modelled upstream CarrierDomain. CESDM distinguishes `EnergyCarrier` from `NaturalResource` so that wind, solar and water inflow are not mistaken for transported commodities.

This layered philosophy provides a physically intuitive, scalable, and
flexible foundation for modelling integrated multi-energy systems.
