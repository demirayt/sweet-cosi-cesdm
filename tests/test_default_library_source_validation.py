"""
Two real bugs in the default library's source YAML, both found by a
user running real code (`model.add_generation_unit(hasTechnology=
"Generation.Nuclear.LWR")`) on their own machine, not by inspection:

1. library/default_library/generator_types/GeneratorType.yaml used
   `- id: label` for a human-readable descriptive name on 4 entries
   (both nuclear technologies, both PHS technologies) -- "label" is
   not a valid GeneratorType attribute at all. The correct attribute
   for this purpose is `long_name`.

2. Two of those same entries (the nuclear ones) also had
   `- id: minimum_generation` -- a real, valid attribute, but only on
   Generation.DispatchView (a per-asset operational parameter), not
   GeneratorType (the technology template) at all. A must-run minimum
   genuinely varies per specific plant, not per generic technology
   class, which is presumably exactly why the schema doesn't have it
   on GeneratorType -- removed from the library source rather than
   remapped to a different GeneratorType field, since inventing a
   mapping to a field that doesn't represent the same thing would
   have been worse than losing the (minor, always-overridable) default.

Both were only ever surfaced at the moment some *unrelated* caller
happened to reference that specific technology id via
ensure_default_library_entity() -- e.g. building a generation unit
with that hasTechnology -- with a confusing KeyError deep in
ear.model.entity_ops, not at library-generation time. Fixed the root
cause (the YAML) and added validate_against_schema() to tools/
generate_default_library.py, so this whole class of bug now fails
loudly at generation time instead.
"""

import subprocess
import sys
import pathlib

import pytest

from cesdm_toolbox import build_model_from_yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_nuclear_and_phs_technologies_have_no_invalid_attributes():
    """The exact reported scenario, for all four originally-affected
    technologies, not just the one in the bug report."""
    model = build_model_from_yaml("schemas")
    model.import_library("library/default_library")
    for tech in [
        "Generation.Nuclear.LWR",
        "Generation.Nuclear.SMR",
        "Generation.Renewable.Hydro.PHS.ClosedLoop",
        "Generation.Renewable.Hydro.PHS.OpenLoop",
    ]:
        gen = model.add_generation_unit(entity_id=f"test.{tech}", hasTechnology=tech)
        assert model.entity_class(str(gen)) == "GenerationUnit"


def test_nuclear_technologies_have_long_name_not_label():
    model = build_model_from_yaml("schemas")
    model.import_library("library/default_library")
    assert model.get_attribute_value("Generation.Nuclear.LWR", "long_name") == \
        "Nuclear Light Water Reactor (PWR/BWR)"
    assert model.get_attribute_value("Generation.Nuclear.SMR", "long_name") == \
        "Small Modular Reactor (<300 MWe)"


def test_every_default_library_class_is_fully_valid_against_the_schema():
    """Systematic sweep, not just the two entries originally reported --
    every attribute/relation id used anywhere in the library source
    must be real for its entity's actual class."""
    import yaml

    model = build_model_from_yaml("schemas")
    files = {
        "EnergyCarrier": "library/default_library/carriers/EnergyCarrier.yaml",
        "StorageType": "library/default_library/storage_types/StorageType.yaml",
        "NaturalResource": "library/default_library/resources/NaturalResource.yaml",
        "GeneratorType": "library/default_library/generator_types/GeneratorType.yaml",
    }
    errors = []
    for class_name, path in files.items():
        valid_attrs = set(model.class_attributes(class_name) or [])
        valid_rels = set(model.class_relations(class_name) or [])
        data = yaml.safe_load((REPO_ROOT / path).read_text())
        for entity_id, entry in data[class_name].items():
            for attr in entry.get("attributes", []):
                if attr["id"] not in valid_attrs:
                    errors.append(f"{class_name}:{entity_id}: bad attribute {attr['id']!r}")
            for rel in entry.get("relations", []):
                if rel["id"] not in valid_rels:
                    errors.append(f"{class_name}:{entity_id}: bad relation {rel['id']!r}")
    assert not errors, "\n".join(errors)


def test_generate_default_library_validation_catches_a_bad_attribute_id(tmp_path):
    """End-to-end: the generator itself must refuse to generate from a
    library source containing an invalid attribute id, with a clear
    message -- not silently produce broken output that only fails
    later, confusingly, in unrelated code."""
    library_dir = tmp_path / "library"
    (library_dir / "generator_types").mkdir(parents=True)
    (library_dir / "generator_types" / "GeneratorType.yaml").write_text(
        "GeneratorType:\n"
        "  Test.Bad:\n"
        "    attributes:\n"
        "    - id: name\n"
        "      value: Test\n"
        "    - id: totally_invalid_attribute\n"
        "      value: 1.0\n"
        "    relations: []\n"
    )
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "generate_default_library.py"),
         "--library", str(library_dir),
         "--schemas", str(REPO_ROOT / "schemas"),
         "--output", str(tmp_path / "default_library.py"),
         "--stub-output", str(tmp_path / "default_library.pyi")],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "totally_invalid_attribute" in result.stderr
    assert "Test.Bad" in result.stderr


def test_generate_default_library_validation_passes_on_real_library():
    """The real, current library source must pass validation cleanly --
    this is what actually runs in CI/before packaging, not just the
    ad-hoc Python check above."""
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "generate_default_library.py"),
         "--library", str(REPO_ROOT / "library" / "default_library"),
         "--schemas", str(REPO_ROOT / "schemas"),
         "--output", str(REPO_ROOT / "cesdm" / "default_library.py"),
         "--stub-output", str(REPO_ROOT / "typings" / "cesdm" / "default_library.pyi")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
