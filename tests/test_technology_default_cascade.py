"""
Model.get_effective_attribute_value() and its wiring into ViewProxy:
the "instance overrides technology-template default" cascade that
GeneratorType/StorageType's own schema descriptions already promised
("Each GenerationUnit then sets only instance-specific overrides...")
but nothing previously implemented. tools/import_flexeco.py had
already reinvented an equivalent local fallback (`_sv()`) before this
existed as a shared, reusable method. See CHANGELOG.md.
"""

import pytest

from cesdm_toolbox import build_model_from_yaml


@pytest.fixture(scope="module")
def model_with_library():
    model = build_model_from_yaml("schemas")
    model.import_library("library/default_library")
    model.add_entity("EnergySystemModel", "sys1")
    model.add_bus("bus.1", nominal_voltage=380)
    return model


def test_cascade_resolves_technology_default_when_unset(model_with_library):
    gen = model_with_library.add_generator(
        id="gen.cascade.1", technology="Generation.Thermal.Gas.CCGT.Present2", bus="bus.1")
    # never explicitly set -- must resolve from the GeneratorType library entity
    assert gen.dispatch.energy_conversion_efficiency == pytest.approx(0.58)
    assert gen.dispatch.variable_operating_cost is not None


def test_explicit_override_takes_priority_over_cascade(model_with_library):
    gen = model_with_library.add_generator(
        id="gen.cascade.2", technology="Generation.Thermal.Gas.CCGT.Present2", bus="bus.1")
    gen.dispatch.energy_conversion_efficiency = 0.62
    assert gen.dispatch.energy_conversion_efficiency == 0.62


def test_cascade_returns_none_without_library_loaded():
    """Without import_library(), the technology entity is a bare stub
    (just a name) -- the cascade must not crash, just return None,
    same as any other unset attribute."""
    model = build_model_from_yaml("schemas")
    model.add_entity("EnergySystemModel", "sys1")
    model.add_bus("bus.1", nominal_voltage=380)
    gen = model.add_generator(id="gen.cascade.3", technology="Generation.Thermal.Gas.CCGT.Present2", bus="bus.1")
    assert gen.dispatch.energy_conversion_efficiency is None


def test_non_overlapping_attribute_unaffected_by_cascade(model_with_library):
    """nominal_power_capacity has no GeneratorType counterpart -- must
    behave exactly as a plain instance attribute, no cascade involved."""
    gen = model_with_library.add_generator(
        id="gen.cascade.4", technology="Generation.Thermal.Gas.CCGT.Present2", bus="bus.1")
    assert gen.dispatch.nominal_power_capacity is None
    gen.dispatch.nominal_power_capacity = 400
    assert gen.dispatch.nominal_power_capacity == 400.0


def test_get_effective_attribute_value_direct_call(model_with_library):
    gen = model_with_library.add_generator(
        id="gen.cascade.5", technology="Generation.Thermal.Gas.CCGT.Present2", bus="bus.1")
    dv_id = gen.dispatch.id
    val = model_with_library.get_effective_attribute_value(dv_id, "energy_conversion_efficiency")
    assert val == pytest.approx(0.58)


def test_cascade_default_when_neither_instance_nor_technology_has_it(model_with_library):
    gen = model_with_library.add_generator(
        id="gen.cascade.6", technology="Generation.Thermal.Gas.CCGT.Present2", bus="bus.1")
    dv_id = gen.dispatch.id
    val = model_with_library.get_effective_attribute_value(
        dv_id, "energy_conversion_efficiency_typo_field", default="fallback")
    assert val == "fallback"
