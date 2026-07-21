"""
Reorganizing cesdm/domain/model/builders.py around one clear rule:
a function belongs there only if it does something a single generated
add_<EntityClass>() call genuinely can't -- multi-entity/multi-view
composite construction, or real decision-making (technology
classification). Everything else moved out or was fixed:

1. Read-only query/lookup helpers (get_dispatch_view, get_topology_view,
   get_powerflow_view, views_for_asset, get_view, reservoir_for_hydro,
   hydro_units_for_reservoir) moved to accessors.py -- they don't build
   anything, they read existing structure, so mixing them into
   builders.py diluted exactly the "this file means construction"
   signal the reorganization is about.

2. connect_to_bus deleted -- a literal one-line alias for
   connect_single_port, with exactly one external caller
   (tools/import_flexeco.py), updated to call connect_single_port
   directly.

3. ensure_carrier/ensure_resource/ensure_technology fixed to return the
   typed proxy ensure_entity() already computes internally, instead of
   discarding it for a bare id string -- the one thing that made them
   genuinely differ from calling ensure_entity(<fixed class name>, ...)
   directly, and they weren't even doing that correctly before.
"""

from cesdm_toolbox import build_model_from_yaml
from cesdm.generated_proxies import EnergyCarrierProxy, NaturalResourceProxy, GeneratorTypeProxy


def _model():
    return build_model_from_yaml("schemas")


def test_moved_query_functions_still_work_from_accessors():
    model = _model()
    model.add_entity("EnergySystemModel", "sys1")
    bus = model.add_bus("bus.1", nominal_voltage=380)
    gen = model.create_generation_unit("gen.1", bus_id=bus, nominal_power_capacity=100)

    assert model.views_for_asset(gen)
    assert model.get_dispatch_view(gen) is not None
    assert model.get_topology_view(gen) is not None
    assert model.get_view(gen, suffix="DispatchView") is not None


def test_reservoir_hydro_query_helpers_still_work_from_accessors():
    model = _model()
    model.add_entity("EnergySystemModel", "sys1")
    bus = model.add_bus("bus.1", nominal_voltage=380)
    reservoir, gen = model.add_reservoir_hydro("gen.hydro.1", "reservoir.1", bus_id=bus,
                                               nominal_power_capacity=50)

    assert model.reservoir_for_hydro(gen) == reservoir
    assert gen in model.hydro_units_for_reservoir(reservoir)


def test_connect_to_bus_no_longer_exists():
    """Deleted -- was a literal one-line alias for connect_single_port."""
    model = _model()
    assert not hasattr(model, "connect_to_bus")


def test_ensure_carrier_returns_the_typed_proxy_not_a_bare_string():
    model = _model()
    carrier = model.ensure_carrier("carrier.test", name="Test Carrier")
    assert isinstance(carrier, EnergyCarrierProxy)
    assert carrier == "carrier.test"  # still usable as a plain string everywhere
    assert model.get_attribute_value(carrier, "name") == "Test Carrier"


def test_ensure_resource_returns_the_typed_proxy_not_a_bare_string():
    model = _model()
    resource = model.ensure_resource("resource.test", name="Test Resource")
    assert isinstance(resource, NaturalResourceProxy)
    assert resource == "resource.test"


def test_ensure_technology_returns_the_typed_proxy_not_a_bare_string():
    model = _model()
    tech = model.ensure_technology("Test.Technology")
    assert isinstance(tech, GeneratorTypeProxy)
    assert tech == "Test.Technology"


def test_ensure_carrier_return_value_supports_direct_attribute_assignment():
    """The whole point of returning a typed proxy instead of a bare
    string: it can be used with the object-oriented API immediately,
    not just re-passed around as an id."""
    model = _model()
    carrier = model.ensure_carrier("carrier.test2", name="Test")
    carrier.co2_emission_intensity = 0.5
    assert model.get_attribute_value(carrier, "co2_emission_intensity") == 0.5
