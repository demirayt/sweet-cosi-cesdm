"""
cesdm.proxy — the object-oriented ergonomics layer discussed with the
user (see CHANGELOG.md, "AssetProxy/ViewProxy object-oriented API").
Everything here is a thin wrapper over the existing low-level EAR API;
these tests exist to prove that wrapping is (a) correct and (b) 100%
backward compatible with code that treats a builder's return value as
a plain string id.
"""

import pytest

from cesdm_toolbox import build_model_from_yaml
from cesdm.proxy import AssetProxy, ViewProxy


def _model_with_bus():
    model = build_model_from_yaml("schemas")
    model.add_entity("EnergySystemModel", "sys1")
    model.add_entity("ElectricalBus", "bus.1")
    model.add_entity("ElectricalBus", "bus.2")
    return model


# ---------------------------------------------------------------------
# Backward compatibility: AssetProxy IS a plain string everywhere
# ---------------------------------------------------------------------

def test_asset_proxy_is_a_real_string_subclass():
    model = _model_with_bus()
    gen = model.add_generator(id="gen1", technology="Generation.Nuclear.LWR", bus="bus.1")
    assert isinstance(gen, str)
    assert isinstance(gen, AssetProxy)


def test_asset_proxy_equals_and_hashes_like_the_plain_id():
    model = _model_with_bus()
    gen = model.add_generator(id="gen1", technology="Generation.Nuclear.LWR", bus="bus.1")
    assert gen == "gen1"
    assert {gen: "value"}["gen1"] == "value"
    assert {"gen1": "value"}[gen] == "value"


def test_existing_low_level_methods_accept_asset_proxy_transparently():
    model = _model_with_bus()
    gen = model.add_generator(id="gen1", technology="Generation.Nuclear.LWR", bus="bus.1")
    # every one of these takes a plain entity-id string in the existing API
    assert model.entity_class(gen) == "GenerationUnit"
    assert model.has_entity(gen)
    assert model.get_relation_targets(gen, "hasTechnology") == ["Generation.Nuclear.LWR"]


def test_all_touched_builders_return_asset_proxy():
    model = _model_with_bus()
    gen = model.add_wind_generator("gen.w", bus_id="bus.1")
    storage = model.create_storage_unit("stor.1", bus_id="bus.1")
    demand = model.create_demand_unit("dem.1", bus_id="bus.1")
    line = model.create_transmission_line("line.1", "bus.1", "bus.2")
    hvdc = model.create_hvdc_link("hvdc.1", "bus.1", "bus.2")
    bus = model.add_bus("bus.3")
    for obj in (gen, storage, demand, line, hvdc, bus):
        assert isinstance(obj, AssetProxy)
        assert isinstance(obj, str)


# ---------------------------------------------------------------------
# The object-oriented API itself
# ---------------------------------------------------------------------

def test_add_generator_top_level_entry_point():
    model = _model_with_bus()
    gen = model.add_generator(id="gen1", technology="Generation.Nuclear.LWR", bus="bus.1")
    assert model.get_relation_targets(gen, "hasTechnology") == ["Generation.Nuclear.LWR"]
    assert model.get_topology_view(gen) is not None  # bus= wired the topology view


def test_dispatch_view_property_get_and_set():
    model = _model_with_bus()
    gen = model.add_generator(id="gen1", technology="Generation.Nuclear.LWR", bus="bus.1",
                              nominal_power_capacity=1600)
    assert isinstance(gen.dispatch, ViewProxy)
    assert gen.dispatch.nominal_power_capacity == 1600.0
    gen.dispatch.maximum_generation = 1550
    assert gen.dispatch.maximum_generation == 1550.0


def test_view_auto_attaches_unit_when_unambiguous():
    model = _model_with_bus()
    gen = model.add_generator(id="gen1", technology="Generation.Nuclear.LWR", bus="bus.1")
    gen.dispatch.nominal_power_capacity = 1600
    raw = model.entity_data(gen.dispatch.id)["nominal_power_capacity"]
    assert isinstance(raw, dict) and raw.get("unit") == "MW"


def test_view_setattr_rejects_unknown_attribute_with_suggestion():
    model = _model_with_bus()
    gen = model.add_generator(id="gen1", technology="Generation.Nuclear.LWR", bus="bus.1")
    with pytest.raises(AttributeError, match="nominal_power_capacity"):
        gen.dispatch.nominal_power_capaciyt = 100  # typo


def test_connect_single_port():
    model = _model_with_bus()
    gen = model.add_generator(id="gen1", technology="Generation.Nuclear.LWR")
    gen.connect("bus.1")
    assert "SinglePort.TopologyView" in model.views_for_asset(gen)


def test_connect_two_port():
    model = _model_with_bus()
    line = model.create_transmission_line("line.1", "bus.1", "bus.1")  # placeholder, real connect below
    line2 = AssetProxy(model, "line.2")
    model.add_entity("TransmissionLine", "line.2")
    line2.connect("bus.1", "bus.2")
    assert model.get_topology_view("line.2") is not None


def test_connect_wrong_arity_raises():
    model = _model_with_bus()
    gen = model.add_generator(id="gen1", technology="Generation.Nuclear.LWR")
    with pytest.raises(TypeError):
        gen.connect("bus.1", "bus.2", "bus.3")


def test_unknown_view_keyword_raises_clear_error():
    model = _model_with_bus()
    gen = model.add_generator(id="gen1", technology="Generation.Nuclear.LWR")
    with pytest.raises(AttributeError, match="dispatch"):
        gen.dispach  # typo -- must suggest "dispatch"


def test_asset_helper_wraps_existing_entity():
    model = _model_with_bus()
    model.add_entity("GenerationUnit", "gen.manual")
    wrapped = model.asset("gen.manual")
    assert isinstance(wrapped, AssetProxy)
    assert wrapped == "gen.manual"
    assert wrapped.entity_class == "GenerationUnit"


def test_full_end_to_end_scenario_validates():
    """Mirrors the user's own worked example (points 1-5 of the API proposal)."""
    model = _model_with_bus()
    gen = model.add_generator(id="gen1", technology="Generation.Nuclear.LWR")
    gen.dispatch.nominal_power_capacity = 1600
    gen.dispatch.maximum_generation = 1550
    gen.connect("bus.1")
    model.validate_or_raise()  # must not raise
