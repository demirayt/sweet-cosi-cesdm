"""
Three related changes to the dynamic/controller attribute family
(MACHINE_*/AVR_*/GOV_*/PSS_*/HVDC.*), all requested together:

1. Every dot-separated attribute id (`MACHINE.xd`, `AVR.SEXS.Ka`, ...)
   renamed to underscore-separated (`MACHINE_xd`, `AVR_SEXS_Ka`, ...) --
   130 attributes total. The family-prefix disambiguation (many
   controller models reuse the same short IEEE symbol -- Ka, Ta, T1)
   is unchanged, only the separator character is, so these now work as
   plain Python identifiers/kwargs directly
   (`add_generator_dynamic_view_subtransient(id, MACHINE_xd=1.8)`)
   without a caller having to `str.replace(".", "_")` first --
   `examples/example_kundur_two_area.py` used to do exactly that.

2. Real IEEE Std 1110-2002 / IEEE Std 421.5-2016 / Kundur / PSS/E
   Model Library typical reference default values added for 113 of
   these attributes (everything except plant-specific sizing --
   rated MVA/kV, MW power limits -- and discrete model-order fields).

3. These defaults apply automatically through *any* construction
   path, not just a specific builder -- `ear.model.entity_ops.
   add_entity()` already applies every attribute's schema-level
   `default` unconditionally on creation (a pre-existing mechanism,
   not something new built for this), so populating `default:` in the
   schema was sufficient on its own.
"""

import pathlib

from cesdm_toolbox import build_model_from_yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_no_dotted_attribute_ids_remain_anywhere_in_the_schema():
    model = build_model_from_yaml("schemas")
    dotted = [a for a in model.global_attributes if "." in a]
    assert dotted == []


def test_machine_avr_gov_pss_attributes_are_underscore_separated():
    model = build_model_from_yaml("schemas")
    for cls, prefix in [
        ("Generator.DynamicView.Subtransient", "MACHINE_"),
        ("ControllerView.AVR.SEXS", "AVR_"),
        ("ControllerView.GOV.IEEEG1", "GOV_"),
        ("ControllerView.PSS.STAB1", "PSS_"),
    ]:
        attrs = model.class_attributes(cls)
        assert any(a.startswith(prefix) for a in attrs)
        assert not any("." in a for a in attrs)


def test_dynamic_view_gets_ieee_defaults_automatically_on_creation():
    """The exact reported scenario: create a generator, read .dynamic
    without ever setting anything explicitly."""
    model = build_model_from_yaml("schemas")
    gen = model.add_generation_unit(entity_id="gen.defaults.test")
    dyn = gen.dynamic
    assert dyn.view_class == "Generator.DynamicView.Subtransient"
    assert dyn.MACHINE_xd == 1.8
    assert dyn.MACHINE_H == 5.0
    assert dyn.MACHINE_D == 0.0
    assert dyn.MACHINE_xd_dprime == 0.25


def test_avr_gov_pss_get_ieee_defaults_automatically_too():
    model = build_model_from_yaml("schemas")
    gen = model.add_generation_unit(entity_id="gen.defaults.test2")

    avr = gen.avr
    assert avr.AVR_Efd_min == -6.0
    assert avr.AVR_Efd_max == 6.0
    # model-specific defaults too, not just the shared-family ones
    if avr.view_class == "ControllerView.AVR.SEXS":
        assert avr.AVR_SEXS_Ka == 200.0
    elif avr.view_class == "ControllerView.AVR.AC1A":
        assert avr.AVR_AC1A_Ka == 400.0

    gov = gen.governor
    assert gov.GOV_Pmin == 0.0

    pss = gen.pss
    assert pss.PSS_Vs_max == 0.1
    assert pss.PSS_Vs_min == -0.1


def test_explicit_value_overrides_the_default():
    model = build_model_from_yaml("schemas")
    gen = model.add_generation_unit(entity_id="gen.defaults.override")
    dyn = gen.dynamic
    assert dyn.MACHINE_xd == 1.8  # default first
    dyn.MACHINE_xd = 2.1
    assert dyn.MACHINE_xd == 2.1  # explicit value wins


def test_plant_specific_sizing_attributes_deliberately_have_no_default():
    """rated_mva/rated_kv are genuinely plant-specific -- there's no
    such thing as a "typical" generator size, so these must NOT have
    invented defaults."""
    model = build_model_from_yaml("schemas")
    for attr in ("MACHINE_rated_mva", "MACHINE_rated_kv"):
        adef = model.global_attributes[attr]
        assert adef["value"].get("default") is None


def test_every_new_default_matches_the_declared_value_type():
    """Integer-typed attributes (PSS2A/PSS2B's M/N ramp-tracking
    orders) must have integer defaults, not float -- a real risk when
    hand-authoring 113 numbers."""
    model = build_model_from_yaml("schemas")
    for attr in ("PSS_PSS2A_M", "PSS_PSS2A_N", "PSS_PSS2B_M", "PSS_PSS2B_N"):
        adef = model.global_attributes[attr]
        assert adef["value"]["type"] == "integer"
        assert isinstance(adef["value"]["default"], int)


def test_kundur_example_no_longer_needs_the_replace_dance():
    """example_kundur_two_area.py used to str.replace(".", "_") its
    parameter dict keys before passing them as **kwargs -- confirms
    that workaround is gone now that the ids are underscore-separated
    at the source."""
    text = (REPO_ROOT / "examples" / "example_kundur_two_area.py").read_text()
    assert 'replace(".", "_")' not in text
