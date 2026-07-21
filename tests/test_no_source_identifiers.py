from pathlib import Path

import yaml


REMOVED = {
    "source_carrier_identifier",
    "source_technology_identifier",
    "source_generator_type",
    "source_storage_type",
    "source_pypsa_name",
}


def test_source_specific_identifiers_are_absent_from_schema_and_python():
    root = Path(__file__).resolve().parents[1]

    for path in root.joinpath("schemas").rglob("*.yaml"):
        text = path.read_text(encoding="utf-8")
        for name in REMOVED:
            assert name not in text, f"{name} still present in {path}"

    for folder in ("tools", "examples"):
        for path in root.joinpath(folder).rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for name in REMOVED:
                assert name not in text, f"{name} still present in {path}"


def test_generation_dispatch_view_does_not_expose_source_identifiers():
    root = Path(__file__).resolve().parents[1]
    schema = yaml.safe_load(
        root.joinpath("schemas/views/dispatch/Generation.DispatchView.yaml").read_text(
            encoding="utf-8"
        )
    )
    attribute_ids = {item["id"] for item in schema.get("attributes", [])}
    assert REMOVED.isdisjoint(attribute_ids)
