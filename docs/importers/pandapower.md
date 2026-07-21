# pandapower import

CESDM includes a first pandapower importer in:

```text
tools/import_pandapower.py
```

The importer maps the power-flow core of a pandapower `net` object into CESDM:

| pandapower table | CESDM representation |
|---|---|
| `net.bus` | `ElectricalBus` + optional `ElectricalBus.PowerFlowView` |
| `net.load` | `DemandUnit` + `SinglePort.TopologyView` + `Demand.PowerFlowView` |
| `net.gen`, `net.sgen` | `GenerationUnit` + `SinglePort.TopologyView` + `Generator.PowerFlowView` |
| `net.ext_grid` | slack/reference generation-like source + bus power-flow view |
| `net.line` | `TransmissionLine` + `TwoPort.TopologyView` + `TransmissionLine.PowerFlowView` |

Install the optional dependency with:

```bash
pip install -e ".[pandapower]"
```

Example:

```python
from tools.import_pandapower import import_pandapower_net

model = import_pandapower_net(net, schema_dir="schemas")
model.validate_or_raise()
```

A complete runnable example is available in:

```text
examples/example_cesdm_to_pandapower_and_matpower.py
```

The MATPOWER-to-pandapower example runs a pandapower AC power flow on the exported network and checks that it converges.

## Line parameter convention

pandapower stores line parameters as physical values:

- `r_ohm_per_km`,
- `x_ohm_per_km`,
- `c_nf_per_km`,
- `length_km`.

The CESDM pandapower importer preserves these values as physical parameters. During MATPOWER export they are converted to MATPOWER per-unit branch totals on `baseMVA`, defaulting to `100.0` MVA.

## Line charging convention

pandapower stores line charging as capacitance `c_nf_per_km`. CESDM stores `shunt_susceptance_per_km` instead. The importer/exporter therefore converts between capacitance and susceptance using:

```text
B [S/km] = 2 * pi * f * C [F/km]
B [microS/km] = B [S/km] * 1e6
```

The default frequency is 50 Hz.


### Transformer handling

MATPOWER represents both ordinary AC lines and two-winding transformers in the `branch` matrix. In CESDM, branches with `TAP == 0` or `TAP == 1` are treated as `TransmissionLine`, while branches with `TAP != 0` and `TAP != 1` are treated as `Transformer`. When exporting back to MATPOWER, both `TransmissionLine` and `Transformer` entities are written to `mpc.branch`; transformers keep their non-nominal tap ratio and phase-shift angle.


## Static shunts

pandapower `net.shunt` entries are represented in CESDM as `ShuntUnit` entities with a `SinglePort.TopologyView` and `Shunt.PowerFlowView`. The importer maps `p_mw` to `active_power_injection` and `q_mvar` to `reactive_power_injection`. The exporter maps these values back to pandapower `net.shunt`.


### Frequency handling for pandapower line charging

pandapower stores line charging as capacitance (`c_nf_per_km`), while CESDM stores `shunt_susceptance_per_km` in `microS/km`. The conversion uses `B = 2*pi*f*C`. Importers prefer `net.f_hz`; exporters accept `frequency_hz` and write it to the pandapower network.
