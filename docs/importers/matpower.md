# MATPOWER import

CESDM includes a pragmatic MATPOWER importer for the common power-flow core.

## Supported mapping

| MATPOWER field | CESDM mapping |
|---|---|
| `mpc.bus` | `ElectricalBus` plus optional `ElectricalBus.PowerFlowView` |
| bus `Pd`, `Qd` | `DemandUnit` plus `Demand.PowerFlowView` |
| `mpc.gen` | `GenerationUnit` plus topology, dispatch and power-flow views |
| `mpc.branch` | `TransmissionLine` plus topology and power-flow views |

## Usage

```python
from tools.import_matpower import load_matpower_case, import_matpower_case

case = load_matpower_case("case9.m")
model = import_matpower_case(case, schema_dir="schemas")
model.validate_or_raise()
```

The built-in loader reads ordinary MATPOWER `.m` files containing `mpc.bus`,
`mpc.gen`, `mpc.branch`, and optional `mpc.gencost` matrices.

## Example

```bash
python examples/example_cesdm_to_pandapower_and_matpower.py
```

This example performs:

```text
MATPOWER case
      ↓
CESDM import
      ↓
CESDM validation
      ↓
pandapower export
      ↓
structural verification
```

## Notes

MATPOWER branch impedances are stored in per-unit values. The importer preserves
these values in CESDM line power-flow attributes using `line_length = 1 km`, so the same numerical values can be reconstructed when exporting back to MATPOWER.

The MATPOWER-to-pandapower example runs a pandapower AC power flow on the exported network and checks that it converges.

## Branch parameter convention

MATPOWER stores branch `r`, `x`, and `b` as **per-unit branch totals** on `mpc.baseMVA`. CESDM stores line parameters physically:

- `series_resistance_per_km` in `Ohm/km`,
- `series_reactance_per_km` in `Ohm/km`,
- `shunt_susceptance_per_km` in `microS/km`.

Important: CESDM stores **shunt susceptance**, not shunt capacitance. Therefore, MATPOWER `b` is converted to physical susceptance using the voltage base and `baseMVA`:

```text
Z_base [Ohm] = V_base[kV]^2 / S_base[MVA]
R [Ohm]      = r_pu * Z_base
X [Ohm]      = x_pu * Z_base
B [S]        = b_pu / Z_base
B [microS]   = B [S] * 1e6
```

Because MATPOWER does not provide physical line lengths, the importer uses `line_length = 1 km` and stores the total physical branch values as per-km values. This preserves the MATPOWER values exactly for round-trip export while keeping CESDM units physically meaningful.


### Transformer handling

MATPOWER represents both ordinary AC lines and two-winding transformers in the `branch` matrix. In CESDM, branches with `TAP == 0` or `TAP == 1` are treated as `TransmissionLine`, while branches with `TAP != 0` and `TAP != 1` are treated as `Transformer`. When exporting back to MATPOWER, both `TransmissionLine` and `Transformer` entities are written to `mpc.branch`; transformers keep their non-nominal tap ratio and phase-shift angle.


## Static shunts

MATPOWER bus shunts are read from the `Gs` and `Bs` columns of the `bus` matrix. Non-zero shunts are imported as `ShuntUnit` entities with:

- `SinglePort.TopologyView.atNode` pointing to the corresponding `ElectricalBus`,
- `Shunt.PowerFlowView.active_power_injection` storing `Gs` in `MW`,
- `Shunt.PowerFlowView.reactive_power_injection` storing `Bs` in `MVAr`.

This keeps static shunts separate from ordinary load demand (`Pd`, `Qd`).
