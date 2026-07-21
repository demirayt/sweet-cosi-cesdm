# Asset hierarchy and technology library

CESDM separates **asset classes** from **technology templates**.

- Asset classes describe what the physical or logical object is, for example `GenerationUnit`, `HydroGenerationUnit`, `DemandUnit`, `ConversionUnit`, `TransmissionLine` or `ReservoirStorageUnit`.
- Library types describe reusable technology assumptions, for example `Generation.Thermal.Gas.CCGT.New` or `Generation.Renewable.Hydro.RunOfRiver`.
- Concrete assets link to library types with `hasTechnology`.

This avoids creating one schema class per technology-library entry while still letting users browse assets through a clearer hierarchy:

```text
EnergyAssetInstance (abstract)
├── SupplyAsset (abstract)
│   ├── GenerationUnit
│   │   ├── GenerationUnit (abstract)
│   │   ├── GenerationUnit (abstract)
│   │   │   ├── HydroGenerationUnit
│   │   │   ├── GenerationUnit
│   │   │   └── GenerationUnit
│   │   └── GenerationUnit
│   └── ExternalSupply
├── DemandAsset (abstract)
│   └── DemandUnit
├── StorageAsset (abstract)
│   ├── StorageUnit
│   └── ReservoirStorageUnit
├── ConversionAsset (abstract)
│   └── ConversionUnit
├── TransportAsset (abstract)
│   └── TransmissionElement
│       ├── TransmissionLine
│       ├── Interconnector
│       ├── Transformer
│       └── HVDCLink
└── CompositeAsset (abstract)
    └── PumpedStoragePlant
```

`ConversionPort` is intentionally outside the asset hierarchy. It now derives from `Port`, because it is a structural interface of a conversion asset or component, not an asset with its own lifecycle.
