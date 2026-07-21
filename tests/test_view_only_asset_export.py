"""
An asset can legitimately carry zero direct attributes/relations of
its own while all its real data lives in an attached representation
view (e.g. a GenerationUnit whose only content is a
GenerationUnit.DispatchResultView) — this is the normal shape of
CESDM's asset/identity vs. representation-view separation, not an
edge case.

export_yaml_hierarchical() used to drop such an asset (and its
attached views) from the export entirely, because it checked whether
the asset's own block was empty *before* looking up and attaching its
views. Found while validating the results-view restructuring (see
CHANGELOG.md); fixed in
cesdm.domain.model.hierarchical_yaml.export_yaml_hierarchical.
"""

from cesdm_toolbox import build_model_from_yaml


def _build_view_only_asset_model():
    model = build_model_from_yaml("schemas")
    model.add_entity("GenerationUnit", "gen.view_only")
    model.add_entity("Storage.DispatchView", "gen.view_only.dv")
    model.add_relation("gen.view_only.dv", "representsAsset", "gen.view_only")
    model.add_attribute("gen.view_only.dv", "nominal_power_capacity", 10.0)
    return model


def test_view_only_asset_survives_hierarchical_export(tmp_path):
    model = _build_view_only_asset_model()
    out_path = tmp_path / "view_only.yaml"
    model.export_yaml_hierarchical(str(out_path))

    text = out_path.read_text(encoding="utf-8")
    assert "gen.view_only" in text
    assert "Storage.DispatchView" in text
    assert "nominal_power_capacity" in text


def test_view_only_asset_round_trips(tmp_path):
    model = _build_view_only_asset_model()
    out_path = tmp_path / "view_only.yaml"
    model.export_yaml_hierarchical(str(out_path))

    model2 = build_model_from_yaml("schemas")
    summary = model2.import_yaml_hierarchical(str(out_path))

    assert "gen.view_only" in model2.entities.get("GenerationUnit", {})
    views = model2.views_for_asset("gen.view_only")
    assert "Storage.DispatchView" in views
    assert not summary["unknowns"]


def test_truly_empty_entity_still_skipped(tmp_path):
    """An entity with no attributes, relations, or views should still be omitted."""
    model = build_model_from_yaml("schemas")
    model.add_entity("GeographicalRegion", "region.empty")
    out_path = tmp_path / "empty.yaml"
    model.export_yaml_hierarchical(str(out_path))

    text = out_path.read_text(encoding="utf-8")
    assert "region.empty" not in text
