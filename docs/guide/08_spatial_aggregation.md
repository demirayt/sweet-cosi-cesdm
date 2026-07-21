# Spatial Aggregation — From Fine to Coarse

## What is spatial aggregation?

A detailed European network model can contain several thousand grid nodes,
tens of thousands of power plants, and hundreds of thousands of time-series
values. Many studies do not need this level of detail.

**Spatial aggregation** merges nodes that are geographically close together —
for example, all nodes in a canton or in a country. The result is a smaller,
faster model that preserves the essential physical and economic properties of
the original.

---

## Aggregation levels

| Level | Description | Typical node count (Europe) |
|---|---|---|
| `disaggregated` | No aggregation — geographic selection only | 3 000 – 8 000 |
| `nuts3` | District level (e.g. Zurich district, Bern district) | ~1 300 |
| `nuts2` | Regional level (e.g. Eastern Switzerland) | ~300 |
| `nuts1` | Federal state / large region | ~100 |
| `country` | Country level (CH, DE, FR, …) | ~35 |

> **What are NUTS codes?**
> NUTS (Nomenclature of Territorial Units for Statistics) is the European
> territorial classification system.
> Example: `CH051` = Zurich district (NUTS3)
> Truncate to `CH05` → NUTS2 (Eastern Switzerland)
> Truncate to `CH0` → NUTS1 (large Swiss region)
> Truncate to `CH` → country (Switzerland)

---

## How does the node assignment work?

Every grid node in the CESDM model has coordinates (`latitude`, `longitude`)
and is linked to a NUTS3 region. The tool reads this information automatically —
no manual mapping table is required.

---

## Keeping or merging voltage levels

In reality, each region has multiple voltage levels (380 kV, 220 kV, 110 kV).
The tool can keep these separate or merge them:

**Keep separate** (default setting):
```
node.ch051.380   ← all 380 kV nodes in Zurich district
node.ch051.220   ← all 220 kV nodes in Zurich district
node.ch051.110   ← all 110 kV nodes in Zurich district
```
→ Transformer links between voltage levels are preserved.
→ Recommended for load flow studies.

**Merge together**:
```
node.ch051       ← all nodes in Zurich district, all voltages combined
```
→ Simpler model.
→ Recommended for long-term capacity planning studies.

---

## Aggregation rules by asset type

### Generation units

Units with the same technology at the same aggregated node are merged:

- **Capacity** → summed (450 MW + 300 MW = 750 MW)
- **Efficiency** → capacity-weighted average
- **Variable cost** → capacity-weighted average
- **Time-series profile** → energy-weighted sum, then re-normalised

> **Why energy-weighted for renewables?**
> Wind farms in a region often have different wind conditions. A small farm
> at a very windy site should influence the aggregated profile more than a
> large farm at a less windy site. Weighting by annual energy — rather than
> installed capacity — captures this correctly.

### Demand (load)

- **Annual energy demand** → summed
- **Load profile** → demand-weighted sum, then re-normalised

### Storage

- **Power and capacity** → summed
- **Efficiencies** → capacity-weighted average
- **Natural inflow profile** (hydropower) → inflow-volume-weighted sum, then re-normalised

### Lines and connections

A line has two endpoints. After aggregation, three cases can occur:

| Case | What happens |
|---|---|
| Both ends in **different** aggregated nodes | Line is kept; parallel lines are merged |
| Both ends in the **same** aggregated node | Line is removed (a loop with no function) |
| One end lies **outside** the selected region | Line is removed |

For merged lines:
- Thermal capacity rating → summed
- Reactance → capacity-weighted average (for simplified load flow)

---

## Running the tool

```bash
python tools/aggregate_cesdm_yaml_subset.py \
    --schemas  schemas/           \
    --yaml     model.yaml         \
    --h5       profiles.h5        \
    --outdir   results/ch         \
    --level    nuts2              \
    --keep     CH                 \
    --split-voltage
```

**The most important options:**

| Option | Meaning |
|---|---|
| `--level nuts2` | Aggregate to NUTS2 level |
| `--keep CH` | Keep only Swiss nodes |
| `--keep CH DE AT FR IT` | Keep nodes in five countries |
| `--keep` (no argument) | Keep everything |
| `--split-voltage` | Keep voltage levels separate (default) |
| `--no-split-voltage` | Merge all voltages |

---

## Output files

After aggregation, the output folder contains:

```
results/ch/
    aggregated_cesdm_nuts2.yaml    ← aggregated CESDM model
    profiles/
        profiles.h5                ← aggregated time-series profiles
    subset_summary.txt             ← summary (node count, asset count, …)
    aggregation_log.txt            ← detailed run log
```

The aggregated YAML model is a fully valid CESDM model that can be used
in the same way as the original.

---

## Known limitations

**Intra-regional network congestion is lost.** If a region has internal
network bottlenecks, the aggregated model will not be aware of them — it
assumes that energy can flow freely within a region.

**Reactance calculation is an approximation.** The capacity-weighted average
reactance of parallel lines is an approximation. For most planning studies
this is accurate enough.
