"""
AssetProxy.__setattr__ -- direct attribute/relation assignment on
asset proxies (`bus.name = "..."`, `bus.locatedIn = region`), not just
on the view proxies returned by `.dispatch`/`.powerflow`/etc.

Before this, AssetProxy (a `str` subclass) had no custom __setattr__
at all, so `bus.name = "X"` silently succeeded as a completely ordinary
Python instance attribute -- stored in the (otherwise-unused)
instance's own __dict__, readable back via `bus.name` from the very
same object, but never touching the model's actual data at all. A
typo (`bus.nam = "X"`) would "succeed" identically, with zero
indication anything was wrong -- the value would just silently vanish
from any export. See CHANGELOG.md.
"""

from cesdm_toolbox import build_model_from_yaml
import pytest


def _model():
    model = build_model_from_yaml("schemas")
    model.add_entity("EnergySystemModel", "sys1")
    return model


def test_setting_name_persists_to_the_model_not_just_the_instance():
    model = _model()
    bus = model.add_bus("bus.1", nominal_voltage=380)
    bus.name = "Mein Bus"
    assert model.get_attribute_value(bus, "name") == "Mein Bus"
    # Reading it back through a *fresh* AssetProxy wrapping the same id
    # confirms it's real model data, not stuck on this one Python object.
    assert model.asset("bus.1").name == "Mein Bus"


def test_unknown_attribute_raises_instead_of_silently_creating_a_python_attribute():
    model = _model()
    bus = model.add_bus("bus.1", nominal_voltage=380)
    with pytest.raises(AttributeError, match="nam"):
        bus.nam = "Typo"
    assert "nam" not in bus.__dict__
    assert model.get_attribute_value(bus, "nam") is None


def test_unknown_attribute_error_suggests_the_correct_name():
    model = _model()
    bus = model.add_bus("bus.1", nominal_voltage=380)
    with pytest.raises(AttributeError, match="Did you mean: name"):
        bus.nam = "Typo"


def test_setting_a_relation_directly_routes_through_the_model():
    model = _model()
    model.add_entity("GeographicalRegion", "region.ch")
    bus = model.add_bus("bus.1", nominal_voltage=380)
    bus.locatedIn = "region.ch"
    assert model.get_relation_targets(bus, "locatedIn") == ["region.ch"]


def test_setting_an_attribute_with_a_single_registered_unit_auto_attaches_it():
    model = _model()
    bus = model.add_bus("bus.1")
    bus.nominal_voltage = 380.0
    raw = model.entity_data(bus)["nominal_voltage"]
    assert isinstance(raw, dict) and raw.get("unit") == "kV"


def test_internal_model_attribute_still_settable_at_construction():
    """The one legitimate internal attribute (_model, set in __new__)
    must still work -- this is what makes AssetProxy constructible at
    all, so a regression here would break every builder."""
    model = _model()
    bus = model.add_bus("bus.1", nominal_voltage=380)
    assert bus._model is model


def test_model_asset_returns_class_specific_generated_proxy():
    """model.asset() used to always return the generic AssetProxy, even
    though the model knows the entity's real class and
    cesdm.generated_proxies already has a specific proxy subclass for
    every schema class (the same one every add_<EntityClass>() builder
    already returns) -- asked directly: shouldn't model.asset("dem.ch")
    give back a DemandUnitProxy? It should, and now does, by reusing
    the same _entity_proxy() helper _relation_value() already used for
    resolving relation targets to their specific proxy type."""
    from cesdm.generated_proxies import DemandUnitProxy, GenerationUnitProxy

    model = _model()
    model.create_demand_unit("dem.1", carrier_id=None)
    demand = model.asset("dem.1")
    assert type(demand).__name__ == "DemandUnitProxy"
    assert isinstance(demand, DemandUnitProxy)
    assert demand == "dem.1"  # still a plain string everywhere it matters

    bus = model.add_bus("bus.1", nominal_voltage=380)
    gen = model.create_generation_unit("gen.1", bus_id=bus)
    rewrapped = model.asset(gen)  # re-wrapping an already-typed proxy
    assert isinstance(rewrapped, GenerationUnitProxy)


def test_model_asset_falls_back_to_plain_assetproxy_for_unknown_class():
    """A defensive fallback -- an entity id with no corresponding
    generated proxy (or that doesn't exist) must not raise, just fall
    back to the generic AssetProxy."""
    model = _model()
    result = model.asset("nonexistent.entity.id")
    assert type(result).__name__ == "AssetProxy"
