# MATPOWER export

CESDM includes a first MATPOWER exporter in:

```text
tools/export_matpower.py
```

The exporter creates a MATPOWER case dictionary and can write a MATLAB `.m` case file.
It currently supports the common power-flow core:

| CESDM | MATPOWER |
|---|---|
| `ElectricalBus` | `mpc.bus` |
| `DemandUnit` + `Demand.PowerFlowView` | bus `PD`, `QD` |
| generation assets + `Generator.PowerFlowView` | `mpc.gen` |
| `TransmissionLine` + `TransmissionLine.PowerFlowView` | `mpc.branch` |

Install optional MATPOWER/PYPOWER dependencies with:

```bash
pip install -e ".[matpower]"
```

Example:

```python
from tools.export_matpower import export_matpower_case, write_matpower_case

case = export_matpower_case(model, base_mva=100.0)
write_matpower_case(case, "output/case_cesdm.m")
```

A complete `pandapower -> CESDM -> MATPOWER` example is available in:

```text
examples/example_cesdm_to_pandapower_and_matpower.py
```

The MATPOWER-to-pandapower example runs a pandapower AC power flow on the exported network and checks that it converges.

## Per-unit branch parameters

MATPOWER branch columns `r`, `x`, and `b` are exported as **per-unit branch totals** on the MATPOWER system base `baseMVA`, which defaults to `100.0` MVA.

The exporter supports two CESDM line-parameter conventions:

1. **MATPOWER-origin per-unit values**

   When a model was imported from MATPOWER, the importer stores branch values with `unit="pu"`, `line_length = 1.0`, and `line_parameter_basis = "per_unit"` where the schema allows these metadata fields. The MATPOWER exporter then writes these values directly back as per-unit branch totals.

2. **Physical line values**

   When a model was imported from pandapower or built with physical line parameters, the exporter converts:

   - resistance from `Ohm/km` to per unit,
   - reactance from `Ohm/km` to per unit,
   - shunt susceptance in `microS/km` to MATPOWER branch charging `b` in per unit.

For the physical conversion the exporter uses:

```text
Z_base [ohm] = V_base[kV]^2 / S_base[MVA]
r_pu = R_ohm_total / Z_base
x_pu = X_ohm_total / Z_base
b_pu = B_siemens_total * Z_base
```

By default `S_base = baseMVA = 100.0` MVA.


### Transformer handling

MATPOWER represents both ordinary AC lines and two-winding transformers in the `branch` matrix. In CESDM, branches with `TAP == 0` or `TAP == 1` are treated as `TransmissionLine`, while branches with `TAP != 0` and `TAP != 1` are treated as `Transformer`. When exporting back to MATPOWER, both `TransmissionLine` and `Transformer` entities are written to `mpc.branch`; transformers keep their non-nominal tap ratio and phase-shift angle.


### Shunt handling

MATPOWER stores static bus shunts in the `bus` matrix columns `Gs` and `Bs`. CESDM represents these as `ShuntUnit` entities connected through `SinglePort.TopologyView` and parameterised by `Shunt.PowerFlowView`. During export, all `ShuntUnit` objects connected to a bus are aggregated back into the MATPOWER `Gs` and `Bs` columns.
