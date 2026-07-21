"""
Most functions in builders.py directly constructed the generic
`AssetProxy(self, entity_id)` instead of using `_entity_proxy(self,
entity_id)` -- the mechanism (cesdm/proxy.py) that resolves an entity
id to its actual, specific generated proxy class (DemandUnitProxy,
TransmissionLineProxy, HydroGenerationUnitProxy, ...), the same one
`ensure_entity()`/`asset()` already use correctly.

Found via a direct report: "create_demand_unit retourniert AssetProxy
und nicht DemandUnitProxy" -- a systematic sweep of the whole file
found the same pattern in ~20 functions total, including several
layers deep (add_wind_generator etc. delegate to create_generation_unit,
which itself was affected) and a few that called ensure_entity()
(already correctly typed) and then discarded that return value in
favour of a bare id string (create_timestamp_series, create_profile,
attach_profile).
"""

from cesdm_toolbox import build_model_from_yaml
from cesdm.generated_proxies import (
    DemandUnitProxy, TransmissionLineProxy, HVDCLinkProxy,
    GenerationUnitProxy, HydroGenerationUnitProxy, StorageUnitProxy,
    ReservoirStorageUnitProxy, TimestampSeriesProxy, ProfileProxy,
)


def _model_with_bus():
    model = build_model_from_yaml("schemas")
    model.import_library("library/default_library")
    model.add_entity("EnergySystemModel", "sys1")
    bus1 = model.add_bus("bus.1", nominal_voltage=380)
    bus2 = model.add_bus("bus.2", nominal_voltage=380)
    return model, bus1, bus2


def test_create_demand_unit_returns_demand_unit_proxy():
    model, bus1, _ = _model_with_bus()
    demand = model.create_demand_unit("demand.1", bus_id=bus1)
    assert isinstance(demand, DemandUnitProxy)
    demand.dispatch.maximum_energy_demand = 250  # only resolves via the specific proxy


def test_create_transmission_line_returns_transmission_line_proxy():
    model, bus1, bus2 = _model_with_bus()
    line = model.create_transmission_line("line.1", bus1, bus2)
    assert isinstance(line, TransmissionLineProxy)


def test_create_hvdc_link_returns_hvdc_link_proxy():
    model, bus1, bus2 = _model_with_bus()
    link = model.create_hvdc_link("link.1", bus1, bus2)
    assert isinstance(link, HVDCLinkProxy)


def test_generation_wrapper_functions_return_generation_unit_proxy():
    model, bus1, _ = _model_with_bus()
    for i, fn in enumerate([
        lambda: model.add_wind_generator(f"wind.{i}", bus_id=bus1, nominal_power_capacity=100),
        lambda: model.add_solar_generator(f"solar.{i}", bus_id=bus1, nominal_power_capacity=100),
        lambda: model.add_thermal_generator(f"thermal.{i}", bus_id=bus1, nominal_power_capacity=100),
        lambda: model.add_nuclear_generator(f"nuclear.{i}", bus_id=bus1, nominal_power_capacity=1000),
    ]):
        result = fn()
        assert isinstance(result, GenerationUnitProxy), f"index {i}: got {type(result)}"


def test_add_hydro_generator_returns_hydro_generation_unit_proxy():
    model, bus1, _ = _model_with_bus()
    gen = model.add_hydro_generator("hydro.1", bus_id=bus1, nominal_power_capacity=100)
    assert isinstance(gen, HydroGenerationUnitProxy)


def test_add_run_of_river_returns_hydro_generation_unit_proxy():
    model, bus1, _ = _model_with_bus()
    gen = model.add_run_of_river("ror.1", bus_id=bus1, nominal_power_capacity=50)
    assert isinstance(gen, HydroGenerationUnitProxy)


def test_create_generation_unit_from_technology_returns_correct_proxy_for_every_family():
    """The dispatcher itself -- must correctly propagate whichever
    family-specific builder it routed to, not downgrade to a generic
    AssetProxy at its own return point."""
    model, bus1, _ = _model_with_bus()
    gas = model.create_generation_unit_from_technology(
        "gas.1", technology="Generation.Thermal.Gas.CCGT.Present2", bus_id=bus1)
    assert isinstance(gas, GenerationUnitProxy)

    hydro = model.create_generation_unit_from_technology(
        "hydro.2", technology="Generation.Renewable.Hydro.Reservoir", bus_id=bus1)
    assert isinstance(hydro, HydroGenerationUnitProxy)


def test_create_storage_unit_returns_storage_unit_proxy():
    model, bus1, _ = _model_with_bus()
    storage = model.create_storage_unit("storage.1", bus_id=bus1)
    assert isinstance(storage, StorageUnitProxy)


def test_add_reservoir_storage_returns_reservoir_storage_unit_proxy():
    model, _, _ = _model_with_bus()
    reservoir = model.add_reservoir_storage("reservoir.1")
    assert isinstance(reservoir, ReservoirStorageUnitProxy)


def test_add_reservoir_hydro_returns_correct_proxy_pair():
    model, bus1, _ = _model_with_bus()
    reservoir, gen = model.add_reservoir_hydro("gen.1", "reservoir.1", bus_id=bus1,
                                               nominal_power_capacity=50)
    assert isinstance(reservoir, ReservoirStorageUnitProxy)
    assert isinstance(gen, HydroGenerationUnitProxy)


def test_phs_functions_return_correct_proxy_pairs():
    model, bus1, _ = _model_with_bus()
    reservoir, gen = model.add_phs_closed_loop("gen.phs1", "upper.1", bus_id=bus1,
                                               nominal_power_capacity=50)
    assert isinstance(reservoir, ReservoirStorageUnitProxy)
    assert isinstance(gen, HydroGenerationUnitProxy)

    reservoir2, gen2 = model.add_phs_open_loop("gen.phs2", "upper.2", bus_id=bus1,
                                               nominal_power_capacity=50)
    assert isinstance(reservoir2, ReservoirStorageUnitProxy)
    assert isinstance(gen2, HydroGenerationUnitProxy)


def test_create_timestamp_series_returns_typed_proxy_not_bare_string():
    """Previously called ensure_entity() (already correctly typed) and
    discarded the result for a bare id string."""
    model, _, _ = _model_with_bus()
    ts = model.create_timestamp_series("ts.1", start_datetime="2030-01-01T00:00:00",
                                       resolution="PT1H", length=8760)
    assert isinstance(ts, TimestampSeriesProxy)


def test_create_profile_returns_typed_proxy_not_bare_string():
    model, _, _ = _model_with_bus()
    ts = model.create_timestamp_series("ts.1", start_datetime="2030-01-01T00:00:00",
                                       resolution="PT1H", length=8760)
    profile = model.create_profile("profile.1", timestamp_series_id=ts)
    assert isinstance(profile, ProfileProxy)


def test_attach_profile_functions_return_typed_profile_proxy():
    model, bus1, _ = _model_with_bus()
    gen = model.add_wind_generator("wind.1", bus_id=bus1, nominal_power_capacity=100)
    ts = model.create_timestamp_series("ts.1", start_datetime="2030-01-01T00:00:00",
                                       resolution="PT1H", length=8760)
    attached = model.attach_availability_profile(gen, "profile.1", create=True,
                                                 timestamp_series_id=ts)
    assert isinstance(attached, ProfileProxy)
