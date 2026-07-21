"""
Model.summary() -- the "let me see what's in this model" explorer
method, deferred in the original API-ergonomics proposal, built here
as the minimal version: asset counts, rolled up by top-level family by
default (HydroGenerationUnit counted under GenerationUnit), with a
detailed=True escape hatch and an as_dict=True programmatic form.
"""

from cesdm_toolbox import build_model_from_yaml


def _populated_model():
    model = build_model_from_yaml("schemas")
    model.import_library("library/default_library")
    model.add_entity("EnergySystemModel", "sys1")
    model.add_bus("bus.1", nominal_voltage=380)
    model.add_bus("bus.2", nominal_voltage=380)
    model.add_generator(id="gen.summary.1", technology="Generation.Thermal.Gas.CCGT.Present2", bus="bus.1")
    model.add_generator(id="gen.summary.2", technology="Generation.Renewable.Wind.Onshore", bus="bus.1")
    model.add_generator(id="gen.summary.3", technology="Generation.Renewable.Hydro.Reservoir", bus="bus.2")
    model.create_demand_unit("dem.summary.1", bus_id="bus.1")
    model.create_storage_unit("stor.summary.1", bus_id="bus.1")
    model.create_transmission_line("line.summary.1", "bus.1", "bus.2")
    return model


def test_summary_default_rolls_up_subclasses():
    model = _populated_model()
    counts = model.summary(as_dict=True)
    assert counts["GenerationUnit"] == 3  # 2 GenerationUnit + 1 HydroGenerationUnit
    assert "HydroGenerationUnit" not in counts  # rolled up, not separate


def test_summary_detailed_keeps_subclasses_separate():
    model = _populated_model()
    counts = model.summary(detailed=True, as_dict=True)
    assert counts["GenerationUnit"] == 2
    assert counts["HydroGenerationUnit"] == 1


def test_summary_excludes_non_asset_entities():
    """GeneratorType, views, EnergySystemModel, ElectricalBus (a domain
    node, not role=="asset") must not appear in the counts."""
    model = _populated_model()
    counts = model.summary(as_dict=True)
    assert "GeneratorType" not in counts
    assert "EnergySystemModel" not in counts
    assert not any("DispatchView" in k or "TopologyView" in k for k in counts)


def test_summary_string_form_is_formatted_and_sorted_by_count_desc():
    model = _populated_model()
    text = model.summary()
    assert isinstance(text, str)
    lines = text.splitlines()
    counts = [int(line.split()[-1]) for line in lines]
    assert counts == sorted(counts, reverse=True)


def test_summary_empty_model():
    model = build_model_from_yaml("schemas")
    assert model.summary() == "(no assets in this model)"
    assert model.summary(as_dict=True) == {}


def test_summary_total_matches_manual_count():
    model = _populated_model()
    counts = model.summary(as_dict=True)
    assert sum(counts.values()) == 6  # 3 generators + 1 demand + 1 storage + 1 line
