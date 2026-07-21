"""
The proxy API's `.dispatch`/`.powerflow`/`.topology`/etc. resolution
used to be driven by a hardcoded Python dict (_VIEW_KEYWORDS) matching
substrings in class names. It's now driven entirely by an optional
`view_family` field in the schema YAML (see ear/entity_class.py and
ear/model/schema_loading.py) — a new view family works by tagging its
abstract root in YAML, with zero changes to cesdm/proxy.py. See
docs/architecture/proxy_api.md and CHANGELOG.md.
"""

import pathlib

import pytest
import yaml

from cesdm_toolbox import build_model_from_yaml
from cesdm.proxy import AssetProxy

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def model():
    return build_model_from_yaml("schemas")


# ---------------------------------------------------------------------
# view_family parsing and inheritance
# ---------------------------------------------------------------------

@pytest.mark.parametrize("root_class,expected_family", [
    ("OperationalDispatchView", "dispatch"),
    ("DispatchResultView", "dispatch"),
    ("PowerFlowView", "powerflow"),
    ("PowerFlowResultView", "powerflow"),
    ("DynamicView", "dynamic"),
    ("DynamicResultView", "dynamic"),
    ("NetworkTopologyView", "topology"),
    ("AssetPlanningView", "planning"),
    ("SpatialView", "spatial"),
    ("Generation.TechnicalView", "technical"),
])
def test_root_classes_declare_view_family(model, root_class, expected_family):
    assert model.classes[root_class].view_family == expected_family


@pytest.mark.parametrize("leaf_class,expected_family", [
    ("Generation.DispatchView", "dispatch"),
    ("HydroGenerationUnit.DispatchView", "dispatch"),
    ("GenerationUnit.DispatchResultView", "dispatch"),
    ("ElectricalBus.PowerFlowView", "powerflow"),
    ("ElectricalBus.PowerFlowResultView", "powerflow"),
    ("SinglePort.TopologyView", "topology"),
    ("TwoPort.TopologyView", "topology"),
    ("AssetLifecycleView", "planning"),  # inherits AssetPlanningView
    ("BusLocationView", "spatial"),
    ("NuclearGeneration.TechnicalView", "technical"),
])
def test_concrete_subclasses_inherit_view_family(model, leaf_class, expected_family):
    assert model.classes[leaf_class].view_family == expected_family


def test_non_view_classes_have_no_view_family(model):
    assert model.classes["GenerationUnit"].view_family is None
    assert model.classes["ElectricalBus"].view_family is None


def test_view_family_not_in_registered_top_level_metadata_keys_leaks_nowhere_else(model):
    """Guards the exact bug found while building this: view_family used
    to be silently dropped by _merge_common(), which only forwarded
    ("description", "parents", "abstract") from the raw YAML dict."""
    import inspect
    import ear.model.schema_loading as sl
    src = inspect.getsource(sl)
    assert '"description", "parents", "abstract", "view_family"' in src


# ---------------------------------------------------------------------
# Proxy resolution driven by view_family, not a hardcoded keyword dict
# ---------------------------------------------------------------------

def test_proxy_module_has_no_hardcoded_keyword_dict():
    import cesdm.proxy as proxy_mod
    assert not hasattr(proxy_mod, "_VIEW_KEYWORDS")


def test_all_ten_families_resolve_end_to_end(model):
    model.add_entity("EnergySystemModel", "sys1")
    bus = model.add_bus("bus.1", nominal_voltage=380)
    gen = model.add_generator(id="gen.vf.test", technology="Generation.Nuclear.LWR", bus=bus)

    gen.dispatch.nominal_power_capacity = 1600
    assert gen.dispatch.nominal_power_capacity == 1600.0

    assert gen.topology is not None

    gen.spatial.latitude = 47.37
    assert gen.spatial.latitude == 47.37

    gen.planning.commission_date = "2030-01-01"
    assert gen.planning.commission_date == "2030-01-01"

    assert gen.technical is not None  # Generation.TechnicalView


def test_unrecognized_keyword_falls_through_to_generic_error(model):
    model.add_entity("EnergySystemModel", "sys2")
    gen = model.add_generator(id="gen.vf.test2", technology="Generation.Nuclear.LWR")
    with pytest.raises(AttributeError, match="not a view, attribute, or relation"):
        gen.frobnicate


def test_recognized_family_but_unavailable_for_asset_gives_specific_error(model):
    model.add_entity("EnergySystemModel", "sys3")
    bus = model.add_bus("bus.vf.test3", nominal_voltage=380)
    bus_proxy = model.asset(bus)
    with pytest.raises(AttributeError, match="real view family in the schema"):
        bus_proxy.dynamic  # ElectricalBus has no dynamic view class


def test_typo_suggestion_still_works(model):
    model.add_entity("EnergySystemModel", "sys4")
    gen = model.add_generator(id="gen.vf.test4", technology="Generation.Nuclear.LWR")
    with pytest.raises(AttributeError, match="Did you mean: dispatch"):
        gen.dispach


# ---------------------------------------------------------------------
# The core claim: a brand new view family works via YAML alone
# ---------------------------------------------------------------------

def test_new_view_family_works_with_zero_python_changes(tmp_path):
    """Builds a throwaway scratch schema tree with a view_family the
    real schema and cesdm/proxy.py have never heard of, and proves it
    resolves correctly -- the actual point of making this schema-driven."""
    root = tmp_path / "scratch"
    (root / "core").mkdir(parents=True)
    (root / "views").mkdir()
    (root / "attributes").mkdir()
    (root / "relations").mkdir()

    (root / "core" / "SemanticEntity.yaml").write_text(
        "name: SemanticEntity\nabstract: true\nparents: []\ndescription: root\n"
        "attributes:\n- id: name\nrelations: []\n"
    )
    (root / "core" / "Thing.yaml").write_text(
        "name: Thing\nparents:\n- SemanticEntity\ndescription: test asset\n"
        "attributes: []\nrelations: []\n"
    )
    (root / "views" / "RepresentationView.yaml").write_text(
        "name: RepresentationView\nabstract: true\nparents:\n- SemanticEntity\n"
        "description: base view\nrelations:\n- id: representsAsset\n  required: true\n"
    )
    (root / "views" / "EconomicView.yaml").write_text(
        "name: EconomicView\nabstract: true\nparents:\n- RepresentationView\n"
        "view_family: economic\ndescription: a brand new family\n"
        "relations:\n- id: representsAsset\n  required: true\n  target: Thing\n"
    )
    (root / "views" / "Thing.EconomicView.yaml").write_text(
        "name: Thing.EconomicView\nparents:\n- EconomicView\n"
        "description: concrete economic view for Thing\n"
        "attributes:\n- id: irr\n"
        "relations:\n- id: representsAsset\n  required: true\n  target: Thing\n"
    )
    (root / "attributes" / "attributes.yaml").write_text(
        "attributes:\n  name:\n    description: name\n    value:\n      type: string\n"
        "  irr:\n    description: internal rate of return\n    value:\n      type: decimal\n"
    )
    (root / "relations" / "relations.yaml").write_text(
        "relations:\n  representsAsset:\n    description: links a view to its asset\n"
        "    target:\n    - Thing\n"
    )

    scratch_model = build_model_from_yaml(str(root))
    scratch_model.add_entity("Thing", "thing1")
    t = AssetProxy(scratch_model, "thing1")

    t.economic.irr = 0.08  # "economic" appears nowhere in cesdm/proxy.py
    assert t.economic.irr == 0.08
    assert t.economic.view_class == "Thing.EconomicView"  # concrete, not the abstract root


# ---------------------------------------------------------------------
# .dynamic resolving to a controller model instead of the machine model
#
# Reported directly by a user: gen.dynamic didn't give the machine's
# own electromechanical parameters -- it resolved to an AVR controller
# instead, arbitrarily (whichever concrete class happened to be first
# in iteration order). Root cause: Generator.DynamicView.Subtransient
# (the machine model) and every ControllerView.AVR.*/GOV.*/PSS.*
# concrete class all inherited view_family: dynamic from the same
# abstract root (DynamicView) -- twelve concrete classes sharing one
# family, with no principled way to prefer the machine model. Unlike
# the dispatch plan-vs-result ambiguity (a genuine "prefer the plan
# view" universal default exists there), a machine model and its AVR
# are not two representations of the same thing -- no tie-break could
# have been correct here. Fixed by giving AVR/GOV/PSS their own
# distinct families instead of sharing "dynamic".
# ---------------------------------------------------------------------

def test_dynamic_resolves_to_machine_model_not_a_controller():
    from cesdm_toolbox import build_model_from_yaml
    model = build_model_from_yaml("schemas")
    gen = model.add_generation_unit(entity_id="gen.dynamic.test")
    assert gen.dynamic.view_class == "Generator.DynamicView.Subtransient"
    machine_attrs = set(model.class_attributes(gen.dynamic.view_class))
    assert "MACHINE_xd" in machine_attrs
    assert "MACHINE_H" in machine_attrs


def test_avr_governor_pss_each_resolve_independently():
    """Previously unreachable via the proxy API at all -- only the raw
    entity API could construct/read these, specifically because of the
    view_family ambiguity this test locks in the fix for."""
    from cesdm_toolbox import build_model_from_yaml
    model = build_model_from_yaml("schemas")
    gen = model.add_generation_unit(entity_id="gen.controllers.test")

    assert gen.avr.view_class.startswith("ControllerView.AVR.")
    assert gen.governor.view_class.startswith("ControllerView.GOV.")
    assert gen.pss.view_class.startswith("ControllerView.PSS.")

    # all three, and the machine model, must be genuinely distinct views
    view_classes = {gen.dynamic.view_class, gen.avr.view_class,
                    gen.governor.view_class, gen.pss.view_class}
    assert len(view_classes) == 4


def test_avr_gov_pss_concrete_classes_have_correct_distinct_families():
    from cesdm_toolbox import build_model_from_yaml
    model = build_model_from_yaml("schemas")
    expectations = {
        "Generator.DynamicView.Subtransient": "dynamic",
        "ControllerView.AVR.AC1A": "avr",
        "ControllerView.AVR.SEXS": "avr",
        "ControllerView.AVR.ST1A": "avr",
        "ControllerView.AVR.IEEET1": "avr",
        "ControllerView.GOV.IEEEG1": "governor",
        "ControllerView.GOV.GGOV1": "governor",
        "ControllerView.GOV.HYGOV": "governor",
        "ControllerView.PSS.STAB1": "pss",
        "ControllerView.PSS.PSS2A": "pss",
        "ControllerView.PSS.PSS2B": "pss",
    }
    for cls_name, expected_family in expectations.items():
        assert model.classes[cls_name].view_family == expected_family, cls_name
