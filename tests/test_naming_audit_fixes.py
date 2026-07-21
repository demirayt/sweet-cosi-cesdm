"""
Guards the findings from the entity/attribute/relation naming and
description audit (see CHANGELOG.md):
- storage_technology_category was a dead, unused attribute confidently
  claiming to be "the single source of truth" for routing decisions
  that storage_technology_type actually handles in practice — removed.
- variable_operating_cost's description undersold its real, correct
  cross-domain scope (generation/storage/HVDC, not just demand).
- pumping_efficiency's description referenced storage_technology_category's
  now-removed enum values.
"""

from cesdm_toolbox import build_model_from_yaml


def test_storage_technology_category_removed():
    model = build_model_from_yaml(["schemas", "schemas_agentbased"])
    assert "storage_technology_category" not in model.global_attributes
    assert "storage_technology_type" in model.global_attributes


def test_variable_operating_cost_description_reflects_full_scope():
    model = build_model_from_yaml(["schemas", "schemas_agentbased"])
    desc = model.global_attributes["variable_operating_cost"]["description"].lower()
    assert "generation" in desc or "generic" in desc
    assert "demand" in desc  # still mentioned, just not exclusively


def test_pumping_efficiency_description_has_no_dangling_reference():
    model = build_model_from_yaml(["schemas", "schemas_agentbased"])
    desc = model.global_attributes["pumping_efficiency"]["description"]
    assert "phs_closed_loop" not in desc  # removed vocabulary, must not linger
    assert "phs_open_loop" not in desc
    assert "storage_technology_type" in desc  # points at the live attribute instead


def test_no_class_references_the_removed_attribute():
    """A stronger guarantee than "the registry doesn't have it" -- no
    class file anywhere declares it either."""
    model = build_model_from_yaml(["schemas", "schemas_agentbased"])
    for cname, cdef in model.classes.items():
        assert "storage_technology_category" not in (cdef.attributes or {})
