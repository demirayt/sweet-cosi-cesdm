"""Example: small CESDM power-flow case -> MATPOWER and pandapower.

The example builds a tiny load-flow model directly in CESDM format,
using the object-oriented proxy API (`model.add_bus(...)`,
`gen.powerflow.x = y`, `gen.connect(bus)`, ...) -- see
docs/architecture/proxy_api.md. See docs/getting_started.md for the
same style of model built with lower-level EAR calls instead.

* 2 electrical buses
* 1 slack generator on bus 1
* 1 load on bus 2
* 1 transmission line between the buses

It then exports the same CESDM model to MATPOWER and pandapower.

Install optional dependencies first:

    pip install -e ".[pandapower,matpower]"

Run from the repository root:

    python examples/example_cesdm_to_pandapower_and_matpower.py
"""

from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cesdm_toolbox import build_model_from_yaml
from tools.export_matpower import export_matpower_case, verify_matpower_export, write_matpower_case
from tools.export_pandapower import export_pandapower_net, verify_pandapower_export


def build_two_bus_cesdm_case(schema_dir: Path):
    """Create a minimal CESDM load-flow case.

    Network:

        generator/slack -- bus.1 -- line.1_2 -- bus.2 -- load
    """
    model = build_model_from_yaml(schema_dir)

    # Root/context entities.
    model.add_entity("EnergySystemModel", "model.two_bus")
    model.set_attribute_if_allowed("model.two_bus", "long_name", "Two-bus CESDM power-flow example")

    model.ensure_carrier("carrier.electricity", name="Electricity")

    domain = model.ensure_entity("CarrierDomain", "domain.electricity", name="Electricity")
    model.add_relation_if_allowed(domain, "hasCarrier", "carrier.electricity")

    model.ensure_entity("GeographicalRegion", "region.demo", name="Demo region")

    # Two electrical buses.  The IDs end in .1 and .2 so the MATPOWER exporter
    # writes bus_i = 1 and 2, never 0. add_bus() also creates the
    # ElectricalBus.PowerFlowView when voltage setpoints are given.
    bus_1 = model.add_bus(
        "bus.1", nominal_voltage=110.0, region_id="region.demo",
        carrier_domain_id="domain.electricity",
        voltage_magnitude_setpoint=1.02, voltage_angle_setpoint=0.0,
    )
    model.set_attribute_if_allowed(bus_1, "name", "Slack bus")

    bus_2 = model.add_bus(
        "bus.2", nominal_voltage=110.0, region_id="region.demo",
        carrier_domain_id="domain.electricity",
        voltage_magnitude_setpoint=1.00, voltage_angle_setpoint=0.0,
    )
    model.set_attribute_if_allowed(bus_2, "name", "Load bus")

    # One slack generator on bus 1. The bus type is stored on
    # Generator.PowerFlowView, not ElectricalBus.PowerFlowView.
    gen_1 = model.create_generation_unit("gen.1", bus_id=bus_1)
    model.set_attribute_if_allowed(gen_1, "name", "Slack generator")

    pv = gen_1.powerflow
    pv.powerflow_bus_type = "slack"
    pv.active_power_setpoint = 50.0
    pv.reactive_power_setpoint = 0.0
    pv.voltage_magnitude_setpoint = 1.02
    pv.voltage_angle_setpoint = 0.0
    pv.maximum_active_power_output = 100.0
    pv.minimum_active_power_output = 0.0
    pv.maximum_reactive_power_output = 50.0
    pv.minimum_reactive_power_output = -50.0

    gen_1.dispatch.generator_technology_type = "generic"
    gen_1.dispatch.nominal_power_capacity = 100.0
    gen_1.dispatch.maximum_generation = 100.0
    gen_1.dispatch.minimum_generation = 0.0

    # One load on bus 2.
    load_1 = model.create_demand_unit("load.1", bus_id=bus_2, carrier_id=None)
    model.set_attribute_if_allowed(load_1, "name", "Demo load")

    load_pv = load_1.powerflow
    load_pv.active_power_demand = 50.0
    load_pv.reactive_power_demand = 20.0

    # One line between the buses.  Physical CESDM units are used here:
    # Ohm/km and microS/km.
    line = model.create_transmission_line("line.1_2", bus_1, bus_2)
    model.set_attribute_if_allowed(line, "name", "Line 1-2")

    line_pv = line.powerflow
    line_pv.line_length = 10.0
    line_pv.series_resistance_per_km = 0.12
    line_pv.series_reactance_per_km = 0.40
    line_pv.shunt_susceptance_per_km = 3.0
    line_pv.thermal_capacity_rating = 100.0

    return model


def main() -> None:
    schema_dir = REPO_ROOT / "schemas"
    output_dir = REPO_ROOT / "output" / "two_bus_cesdm_to_matpower_and_pandapower"
    output_dir.mkdir(parents=True, exist_ok=True)

    model = build_two_bus_cesdm_case(schema_dir)
    model.validate_or_raise()

    print(model.summary())
    print()

    # Export CESDM -> MATPOWER.
    matpower_case = export_matpower_case(model, base_mva=100.0)
    matpower_result = verify_matpower_export(
        matpower_case,
        expected_buses=2,
        expected_branches=1,
        min_generators=1,
    )
    if not matpower_result["ok"]:
        raise SystemExit("MATPOWER verification failed:\n" + "\n".join(matpower_result["errors"]))
    matpower_path = write_matpower_case(
        matpower_case,
        output_dir / "two_bus_from_cesdm.m",
        function_name="two_bus_from_cesdm",
    )

    # Export CESDM -> pandapower.  This part needs the optional pandapower
    # dependency; MATPOWER export above works without it.
    try:
        pp_net = export_pandapower_net(
            model,
            name="Two-bus CESDM example",
            base_mva=100.0,
            frequency_hz=50.0,
        )
        pp_result = verify_pandapower_export(
            pp_net,
            expected_buses=2,
            expected_lines=1,
            expected_transformers=0,
            min_generators=1,
            min_loads=1,
            min_ext_grids=1,
        )
        if not pp_result["ok"]:
            raise SystemExit("pandapower verification failed:\n" + "\n".join(pp_result["errors"]))

        import pandapower as pp
        pp.runpp(pp_net, init="flat", calculate_voltage_angles=True)
        if not bool(getattr(pp_net, "converged", False)):
            raise RuntimeError("pandapower load flow did not converge.")
        pp.to_json(pp_net, str(output_dir / "two_bus_from_cesdm_pandapower.json"))
        pp_status = "pandapower network exported, verified, saved, and AC load flow converged"
    except ImportError:
        pp_status = "pandapower not installed; MATPOWER export was written, install pandapower to also write the pandapower JSON"

    model.export_yaml_model(output_dir / "two_bus_cesdm.yaml")

    print("✓ Two-bus CESDM model created")
    print("✓ CESDM model validated")
    print("✓ MATPOWER case exported and verified")
    print("✓ pandapower network exported and verified")
    print(f"✓ {pp_status}")
    print(f"MATPOWER case: {matpower_path}")
    print(f"CESDM YAML:     {output_dir / 'two_bus_cesdm.yaml'}")


if __name__ == "__main__":
    main()
