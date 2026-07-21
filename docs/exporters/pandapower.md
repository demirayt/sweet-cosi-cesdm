# pandapower export

CESDM can export the common power-flow core to a pandapower network.

## Supported mapping

| CESDM concept | pandapower table |
|---|---|
| `ElectricalBus` | `net.bus` |
| `ElectricalBus.PowerFlowView` with slack type | `net.ext_grid` |
| `DemandUnit` + `Demand.PowerFlowView` | `net.load` |
| generation assets + `Generator.PowerFlowView` | `net.gen` |
| `TransmissionLine` + `TransmissionLine.PowerFlowView` | `net.line` |

## Usage

```python
from tools.export_pandapower import export_pandapower_net

pp_net = export_pandapower_net(model, name="CESDM export", base_mva=100.0)
```

The exporter requires pandapower:

```bash
pip install -e ".[pandapower]"
```

## Verification

```python
from tools.export_pandapower import verify_pandapower_export

result = verify_pandapower_export(
    pp_net,
    expected_buses=3,
    expected_lines=2,
    min_generators=1,
    min_loads=1,
)

if not result["ok"]:
    raise RuntimeError(result["errors"])
```

## Limitations

The export is intentionally conservative. It focuses on buses, loads,
generators, slack buses and transmission lines. Rich CESDM semantics without a
pandapower equivalent remain in CESDM and are not represented in the exported
pandapower network.

## Example

A complete `CESDM -> pandapower` (and `-> MATPOWER`) example is available in:

```bash
pip install -e ".[pandapower,matpower]"
python examples/example_cesdm_to_pandapower_and_matpower.py
```

The MATPOWER-to-pandapower example runs a pandapower AC power flow on the exported network and checks that it converges.

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
