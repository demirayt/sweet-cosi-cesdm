"""
create_generation_unit_from_technology() had three related bugs, all found
by hand-testing while evaluating a proposed API-ergonomics redesign
(see CHANGELOG.md):

1. Routing bug: generation_asset_class_from_technology() correctly
   returns the same CESDM entity class ("GenerationUnit") for wind,
   solar, thermal, and nuclear technologies (CESDM has no separate
   schema subclasses for these). The consuming code treated that as a
   distinguishing signal across four `if cls == "GenerationUnit":`
   branches -- so only the first one was ever reachable, and every
   non-hydro technology silently got routed through
   add_solar_generator() regardless of what was actually requested.

2. _view_id()'s id-prefix mapping had 5 dict entries for the same key
   ("Generation.DispatchView"), one intended per technology family --
   dict literals silently let later duplicate keys win, so every
   non-hydro generator's auto-generated view id claimed to be
   "solar_dispatch_view" regardless of its real technology.

3. create_generation_unit_from_technology's thermal branch always passed
   fuel_carrier_id=input_carrier_id (None unless the caller explicitly
   supplied one), clobbering add_thermal_generator's own sensible
   default ("carrier.fuel.fossil.gas.natural_gas", the canonical id --
   originally the non-canonical "carrier.natural_gas", fixed later)
   every time it was called through the technology-routing entry point.
"""

from cesdm_toolbox import build_model_from_yaml


def _model_with_bus():
    model = build_model_from_yaml("schemas")
    model.add_entity("EnergySystemModel", "sys1")
    model.add_entity("ElectricalBus", "bus.1")
    return model


def test_family_classifier_distinguishes_technologies():
    model = _model_with_bus()
    cases = {
        "Generation.Nuclear.LWR": "nuclear",
        "Generation.Thermal.Gas.CCGT": "thermal",
        "Generation.Renewable.Wind.Onshore": "wind",
        "Generation.Renewable.Solar.PV": "solar",
        "Generation.Renewable.Hydro.Reservoir": "hydro",
        "something_unrecognized": "generic",
    }
    for tech, expected_family in cases.items():
        assert model._generator_family_from_technology(None, tech) == expected_family


def test_each_technology_gets_its_own_hasTechnology_not_always_solar():
    model = _model_with_bus()
    technologies = [
        "Generation.Nuclear.LWR",
        "Generation.Thermal.Gas.CCGT",
        "Generation.Renewable.Wind.Onshore",
        "Generation.Renewable.Solar.PV",
    ]
    for tech in technologies:
        eid = f"gen.{tech}"
        model.create_generation_unit_from_technology(eid, technology=tech, bus_id="bus.1", nominal_power_capacity=100)
        assert model.get_relation_targets(eid, "hasTechnology") == [tech], (
            f"requested {tech!r} but got {model.get_relation_targets(eid, 'hasTechnology')!r}"
        )


def test_hydro_still_gets_hydro_generation_unit_class():
    model = _model_with_bus()
    eid = model.create_generation_unit_from_technology(
        "gen.hydro", technology="Generation.Renewable.Hydro.Reservoir",
        bus_id="bus.1", nominal_power_capacity=200,
    )
    assert model.entity_class(eid) == "HydroGenerationUnit"


def test_wind_gets_wind_resource_not_solar():
    model = _model_with_bus()
    eid = model.create_generation_unit_from_technology(
        "gen.wind", technology="Generation.Renewable.Wind.Onshore",
        bus_id="bus.1", nominal_power_capacity=50,
    )
    assert model.get_relation_targets(eid, "hasInputResource") == ["resource.renewable.wind"]


def test_view_id_prefix_is_not_always_solar():
    model = _model_with_bus()
    eid = model.create_generation_unit_from_technology(
        "gen.nuclear", technology="Generation.Nuclear.LWR",
        bus_id="bus.1", nominal_power_capacity=1600,
    )
    dv_id = model.views_for_asset(eid)["Generation.DispatchView"]
    assert "solar" not in dv_id


def test_thermal_gets_default_gas_carrier_when_not_specified():
    """input_carrier_id being unspecified (None) must not clobber
    add_thermal_generator's own default of
    carrier.fuel.fossil.gas.natural_gas (the canonical id -- fixed
    from the non-canonical "carrier.natural_gas" after that turned up
    as an orphaned, wrongly-attached entity in the README's own quick
    start example; see CHANGELOG.md)."""
    model = _model_with_bus()
    eid = model.create_generation_unit_from_technology(
        "gen.thermal", technology="Generation.Thermal.Gas.CCGT",
        bus_id="bus.1", nominal_power_capacity=400,
    )
    assert model.get_relation_targets(eid, "hasInputCarrier") == ["carrier.fuel.fossil.gas.natural_gas"]


def test_thermal_respects_explicit_input_carrier_override():
    model = _model_with_bus()
    model.ensure_carrier("carrier.hydrogen")
    eid = model.create_generation_unit_from_technology(
        "gen.h2_thermal", technology="Generation.Thermal.Hydrogen.CCGT",
        bus_id="bus.1", nominal_power_capacity=400,
        input_carrier_id="carrier.hydrogen",
    )
    assert model.get_relation_targets(eid, "hasInputCarrier") == ["carrier.hydrogen"]
