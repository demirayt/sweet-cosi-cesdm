"""
Reported directly, with a real Pyright error: `m.add_generator_dynamic_
view_subtransient(entity_id="gen.sub")` demanded MACHINE_H, MACHINE_xd,
and ten other attributes as mandatory keyword arguments, even though
they'd just been given real IEEE/PSS-E default values in the schema.

Root cause: tools/generate_convenience_api.py's render_method() decided
Python parameter optionality purely from the schema's `required:` flag,
never checking whether the attribute also had a `default:` value. 81
attributes across the whole schema had this exact pattern (required:
true *and* a default) -- most of them the MACHINE_*/AVR_*/GOV_*/PSS_*
ones from the previous change, but not only those. A `required: true`
attribute genuinely means "this must eventually have a value for
validation to pass" -- which a default already guarantees at creation
time (ear.model.entity_ops.add_entity() applies every attribute's
default unconditionally) -- so treating it as "must always be passed
explicitly by the caller" too was simply wrong once a default existed.

Fixed: a field is now Python-optional (`= None` in the generated
signature) if it has a schema default, regardless of `required:`.
Relations are unaffected (a relation target can't be "defaulted"), so
representsAsset and similar still correctly stay mandatory.
"""

from cesdm_toolbox import build_model_from_yaml


def test_machine_attributes_with_defaults_are_python_optional():
    """The exact reported scenario."""
    model = build_model_from_yaml("schemas")
    gen = model.add_generation_unit(entity_id="gen.1")
    dyn = model.add_generator_dynamic_view_subtransient(
        entity_id="dyn.1",
        MACHINE_rated_mva=900.0, MACHINE_rated_kv=20.0, MACHINE_model="subtransient_6th",
        representsAsset=gen,
    )
    assert dyn.MACHINE_H == 5.0
    assert dyn.MACHINE_xd == 1.8
    assert dyn.MACHINE_D == 0.0


def test_avr_sexs_constructor_needs_only_representsasset():
    """Every AVR.SEXS attribute has a default -- the only truly
    required parameter left should be the relation."""
    model = build_model_from_yaml("schemas")
    gen = model.add_generation_unit(entity_id="gen.2")
    avr = model.add_controller_view_avr_sexs(entity_id="avr.1", representsAsset=gen)
    assert avr.AVR_SEXS_Ka == 200.0
    assert avr.AVR_Efd_min == -6.0


def test_plant_specific_attributes_without_a_default_stay_mandatory():
    """MACHINE_rated_mva/kv/model genuinely have no sensible default
    (there's no "typical" generator size) -- these must still be
    required, unlike the ones this fix makes optional."""
    model = build_model_from_yaml("schemas")
    gen = model.add_generation_unit(entity_id="gen.3")
    try:
        model.add_generator_dynamic_view_subtransient(entity_id="dyn.2", representsAsset=gen)
        assert False, "should have raised for missing required params"
    except TypeError as exc:
        assert "MACHINE_rated_mva" in str(exc)


def test_explicit_value_still_overrides_the_default_through_the_generated_constructor():
    model = build_model_from_yaml("schemas")
    gen = model.add_generation_unit(entity_id="gen.4")
    dyn = model.add_generator_dynamic_view_subtransient(
        entity_id="dyn.3",
        MACHINE_rated_mva=100.0, MACHINE_rated_kv=15.0, MACHINE_model="classical",
        MACHINE_xd=2.5,  # explicit override
        representsAsset=gen,
    )
    assert dyn.MACHINE_xd == 2.5
    assert dyn.MACHINE_H == 5.0  # not overridden -> still the default


def test_no_generated_constructor_marks_a_defaulted_attribute_as_mandatory():
    """Systematic sweep across the whole schema, not just the one
    reported class -- 81 attributes had this exact bug pattern."""
    import re

    text = open("cesdm/domain/model/generated_builders.py").read()
    model = build_model_from_yaml("schemas")
    violations = []
    # Use the generated method->class mapping the module itself exposes.
    from cesdm.domain.model.generated_builders import GeneratedBuildersMixin
    for method_name, class_name in GeneratedBuildersMixin.GENERATED_ADD_METHODS.items():
        class_def = model.classes[class_name]
        attrs, _ = model._collect_inherited_fields(class_def)
        defaulted_but_required_ids = {
            name for name, d in attrs.items()
            if getattr(d, "default", None) is not None and bool(getattr(d, "required", False))
        }
        if not defaulted_but_required_ids:
            continue
        m = re.search(rf"    def {re.escape(method_name)}\(.*?\) -> ", text, re.DOTALL)
        assert m, method_name
        sig_text = m.group(0)
        for attr_id in defaulted_but_required_ids:
            # a mandatory (non-optional) parameter looks like "    attr_id: Any,"
            # -- an optional one has "| None = None" on the same line.
            pattern = re.compile(rf"^\s+{re.escape(attr_id)}: .*$", re.MULTILINE)
            line_match = pattern.search(sig_text)
            assert line_match, f"{method_name}: {attr_id} not found in signature"
            if "= None" not in line_match.group(0):
                violations.append((method_name, attr_id))

    assert not violations, violations
