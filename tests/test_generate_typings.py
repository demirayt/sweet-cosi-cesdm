"""
tools/generate_typings.py: generates editor-friendly .pyi stubs from
the schema tree + BuildersMixin's AST. Contributed and integrated —
see CHANGELOG.md for the full assessment, including a real
non-determinism/correctness bug found and fixed (candidate selection
for a view family with multiple valid concrete classes, e.g.
Generation.DispatchView vs GenerationUnit.DispatchResultView both
being view_family: dispatch, used to pick whichever Python's set
iteration happened to produce first).

These tests validate the generator runs cleanly against the real repo
and that its output is both syntactically valid and, for the specific
bug found, semantically correct -- not just "doesn't crash".
"""

import ast
import pathlib
import subprocess
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def generated_typings(tmp_path_factory):
    out = tmp_path_factory.mktemp("typings")
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "generate_typings.py"),
         "--schemas", str(REPO_ROOT / "schemas"),
         "--source-root", str(REPO_ROOT),
         "--output", str(out)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    return out


def test_generator_produces_expected_files(generated_typings):
    expected = [
        "cesdm/__init__.pyi",
        "cesdm/domain/__init__.pyi",
        "cesdm/domain/model/__init__.pyi",
        "cesdm/domain/model/core.pyi",
        "cesdm/helpers.pyi",
        "cesdm/proxy.pyi",
        "cesdm/generated_proxies.pyi",
        "cesdm_toolbox.pyi",
    ]
    for rel in expected:
        assert (generated_typings / rel).is_file(), rel


def test_every_generated_stub_is_syntactically_valid_python(generated_typings):
    for f in generated_typings.rglob("*.pyi"):
        try:
            ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError as e:
            pytest.fail(f"{f}: {e}")


def test_dispatch_family_resolves_to_plan_view_not_result_view(generated_typings):
    """Regression test for the real bug found integrating this tool:
    GenerationUnitProxy.dispatch used to resolve to
    GenerationUnitDispatchResultViewProxy (a Result view -- only
    exists after a dispatch run) rather than
    GenerationDispatchViewProxy (the plan/input view every freshly
    created GenerationUnit actually has), because multiple concrete
    view classes share view_family: dispatch and the original
    selection logic took "whichever Python's set iteration produced
    first" instead of a deterministic, sensible tie-break."""
    text = (generated_typings / "cesdm" / "generated_proxies.pyi").read_text()
    start = text.index("class GenerationUnitProxy(AssetProxy):")
    block = text[start:text.index("\n\n", start)]
    assert "dispatch: GenerationDispatchViewProxy" in block
    assert "ResultView" not in block.split("dispatch:")[1].split("\n")[0]


def test_core_stub_covers_builder_methods(generated_typings):
    text = (generated_typings / "cesdm" / "domain" / "model" / "core.pyi").read_text()
    for method in ("add_bus", "add_generator", "create_storage_unit",
                   "create_demand_unit", "create_transmission_line", "create_hvdc_link"):
        assert f"def {method}(" in text


def test_core_stub_covers_every_public_runtime_method(tmp_path):
    """The actual point of extending extract_methods() beyond
    BuildersMixin: every real, public, callable method CesdmModel has
    at runtime must appear in the generated stub. Regression test for
    the gap found by running Pyright against real usage (~60% of the
    public surface was invisible to editors, including summary(),
    get_effective_attribute_value(), import_library(), and the raw EAR
    primitives add_entity/add_attribute/add_relation -- all of which
    the README's own recommended quick-start example uses)."""
    import re
    import subprocess
    import sys as _sys

    from cesdm_toolbox import build_model_from_yaml

    model = build_model_from_yaml("schemas")
    runtime_methods = {
        m for m in dir(model) if not m.startswith("_") and callable(getattr(model, m))
    }

    out = tmp_path / "typings_coverage_check"
    subprocess.run(
        [_sys.executable, str(REPO_ROOT / "tools" / "generate_typings.py"),
         "--schemas", str(REPO_ROOT / "schemas"),
         "--source-root", str(REPO_ROOT),
         "--output", str(out)],
        check=True, capture_output=True,
    )
    text = (out / "cesdm" / "domain" / "model" / "core.pyi").read_text()
    stub_methods = {m.group(1) for m in re.finditer(r"    def (\w+)\(", text)}

    missing = sorted(runtime_methods - stub_methods)
    assert not missing, f"Methods missing from the generated stub: {missing}"


def test_generated_stubs_type_check_the_readme_quickstart_example(generated_typings):
    """Best-effort: if pyright is installed, actually run it against a
    snippet mirroring the README's recommended quick-start example, and
    assert the parts that ARE in BuildersMixin type-check cleanly.
    Skips gracefully if pyright isn't available (it's a dev-only tool,
    not a runtime dependency of this repo)."""
    pyright = None
    for candidate in ("pyright", sys.executable + " -m pyright"):
        try:
            subprocess.run(candidate.split() + ["--version"], capture_output=True, check=True)
            pyright = candidate
            break
        except Exception:
            continue
    if pyright is None:
        pytest.skip("pyright not installed")

    snippet = generated_typings.parent / "quickstart_snippet.py"
    snippet.write_text(
        "from cesdm_toolbox import build_model_from_yaml\n"
        "model = build_model_from_yaml('schemas')\n"
        "model.import_library('library/default_library')\n"
        "model.add_entity('EnergySystemModel', 'sys1')\n"
        "bus = model.add_bus('bus.1', nominal_voltage=380)\n"
        "gen = model.add_generator(id='gen1', technology='Generation.Nuclear.LWR', bus=bus)\n"
        "gen.dispatch.nominal_power_capacity = 1600\n"
        "gen.connect(bus)\n"
        "print(gen.dispatch.energy_conversion_efficiency)\n"
        "print(model.summary())\n"
        "model.validate_or_raise()\n"
    )
    pyrightconfig = generated_typings.parent / "pyrightconfig.json"
    pyrightconfig.write_text(
        '{"stubPath": "' + str(generated_typings).replace("\\", "\\\\") + '"}'
    )
    result = subprocess.run(
        pyright.split() + [str(snippet)],
        capture_output=True, text=True, cwd=str(generated_typings.parent),
    )
    assert "0 errors" in result.stdout, result.stdout


def test_generated_entity_proxies_and_builder_return_types_are_in_stubs(generated_typings):
    proxy_stub = (generated_typings / "cesdm" / "generated_proxies.pyi").read_text(encoding="utf-8")
    model_stub = (generated_typings / "cesdm" / "domain" / "model" / "core.pyi").read_text(encoding="utf-8")

    assert "class TimestampSeriesProxy(AssetProxy):" in proxy_stub
    assert ") -> TimestampSeriesProxy: ..." in model_stub


def test_relation_members_use_target_proxy_types(generated_typings):
    proxy_stub = (generated_typings / "cesdm" / "generated_proxies.pyi").read_text(encoding="utf-8")
    start = proxy_stub.index("class ElectricalBusProxy(AssetProxy):")
    block = proxy_stub[start:proxy_stub.index("\n\n", start)]
    assert "def locatedIn(self) -> GeographicalRegionProxy | None: ..." in block
    assert "def locatedIn(self, value: GeographicalRegionProxy | str) -> None: ..." in block
    assert "def belongsToCarrierDomain(self) -> CarrierDomainProxy | None: ..." in block
    assert "def belongsToCarrierDomain(self, value: CarrierDomainProxy | str) -> None: ..." in block


def test_runtime_relation_getter_returns_concrete_proxy():
    from cesdm.generated_proxies import GeographicalRegionProxy
    from cesdm_toolbox import build_model_from_yaml

    model = build_model_from_yaml("schemas")
    region = model.add_geographical_region("region.typed")
    bus = model.add_electrical_bus("bus.typed", locatedIn=region)

    assert isinstance(bus.locatedIn, GeographicalRegionProxy)
    assert bus.locatedIn.id == "region.typed"


def test_core_stub_declares_model_storage_attributes(generated_typings):
    text = (generated_typings / "cesdm" / "domain" / "model" / "core.pyi").read_text(encoding="utf-8")
    assert "classes: Dict[str, EntityClass]" in text
    assert "entities: Dict[str, Dict[str, Entity]]" in text
    assert "inheritance: Dict[str, Union[str, List[str], None]]" in text
    assert "schema_manifest: SchemaManifest" in text


# ---------------------------------------------------------------------
# generated_proxies.pyi vs proxy.pyi split, and the tuple-return-type
# bug found while investigating a real Pyright report on
# tutorial_ch_neighbours.py: "Cannot access attribute dispatch for
# class AssetProxy". Root causes, both real, both fixed:
#
# 1. Every per-entity proxy subclass (DemandUnitProxy, etc.) was
#    declared in proxy.pyi, but the *real* classes live in
#    cesdm/generated_proxies.py -- a separate runtime module. Anyone
#    importing the correct way (`from cesdm.generated_proxies import
#    DemandUnitProxy`, the same path cesdm.proxy._entity_proxy() itself
#    uses) got the real, type-annotation-free class instead of any
#    enriched stub, silently losing all `.dispatch` etc. typing.
#
# 2. add_reservoir_hydro/add_phs_open_loop/add_phs_closed_loop actually
#    return a *tuple* of two proxies, but RETURN_OVERRIDES had them
#    mapped to a single bare type -- Pyright then inferred
#    `reservoir, gen = m.add_reservoir_hydro(...)` as *string*
#    unpacking (iterating characters), typing both as `str`. Fixing
#    the override to the correct tuple type introduced a second bug:
#    the whole "tuple[...]" string got emitted as a literal import
#    name (invalid syntax), since the import-collection code assumed
#    every RETURN_OVERRIDES value was a bare identifier.
# ---------------------------------------------------------------------

def test_demand_unit_proxy_stub_lives_in_generated_proxies_not_proxy_pyi(generated_typings):
    proxy_stub = (generated_typings / "cesdm" / "proxy.pyi").read_text(encoding="utf-8")
    generated_stub = (generated_typings / "cesdm" / "generated_proxies.pyi").read_text(encoding="utf-8")
    assert "class DemandUnitProxy" not in proxy_stub
    assert "class DemandUnitProxy(AssetProxy):" in generated_stub
    assert "dispatch: DemandDispatchViewProxy" in generated_stub


def test_asset_as_and_dispatch_type_check_together_with_pyright(generated_typings):
    """The actual end-to-end regression: model.asset_as(id, DemandUnitProxy)
    followed by .dispatch.<real attribute> must type-check with 0
    errors, and the same with a deliberate typo must be flagged --
    exercising both the _T TypeVar declaration in core.pyi and the
    generated_proxies.pyi split together, the same way asking "does
    .dispatch type-check too?" on real example code caught this."""
    pyright = None
    for candidate in ("pyright", sys.executable + " -m pyright"):
        try:
            subprocess.run(candidate.split() + ["--version"], capture_output=True, check=True)
            pyright = candidate
            break
        except Exception:
            continue
    if pyright is None:
        pytest.skip("pyright not installed")

    good = generated_typings.parent / "asset_as_good.py"
    good.write_text(
        "from cesdm_toolbox import build_model_from_yaml\n"
        "from cesdm.generated_proxies import DemandUnitProxy\n"
        "model = build_model_from_yaml('schemas')\n"
        "model.create_demand_unit('dem.1', carrier_id=None)\n"
        "d = model.asset_as('dem.1', DemandUnitProxy)\n"
        "d.dispatch.annual_energy_demand = 1000\n"
    )
    bad = generated_typings.parent / "asset_as_bad.py"
    bad.write_text(
        "from cesdm_toolbox import build_model_from_yaml\n"
        "from cesdm.generated_proxies import DemandUnitProxy\n"
        "model = build_model_from_yaml('schemas')\n"
        "model.create_demand_unit('dem.1', carrier_id=None)\n"
        "d = model.asset_as('dem.1', DemandUnitProxy)\n"
        "d.dispatch.anual_energy_demand = 1000\n"  # typo
    )
    pyrightconfig = generated_typings.parent / "pyrightconfig.json"
    pyrightconfig.write_text('{"stubPath": "' + str(generated_typings).replace("\\", "\\\\") + '"}')

    good_result = subprocess.run(pyright.split() + [str(good)], capture_output=True, text=True,
                                 cwd=str(generated_typings.parent))
    assert "0 errors" in good_result.stdout, good_result.stdout

    bad_result = subprocess.run(pyright.split() + [str(bad)], capture_output=True, text=True,
                                cwd=str(generated_typings.parent))
    assert "anual_energy_demand" in bad_result.stdout, bad_result.stdout


def test_tuple_returning_composite_builders_have_correct_tuple_stub_type(generated_typings):
    """Regression test for the str-unpacking bug: these three functions
    return (ReservoirStorageUnitProxy, HydroGenerationUnitProxy), not a
    single proxy -- the stub must say so, or `a, b = model.add_reservoir_hydro(...)`
    gets silently (mis)inferred as unpacking a string."""
    text = (generated_typings / "cesdm" / "domain" / "model" / "core.pyi").read_text(encoding="utf-8")
    expected_return = "-> tuple[ReservoirStorageUnitProxy, HydroGenerationUnitProxy]:"
    for fn in ("add_reservoir_hydro", "add_phs_open_loop", "add_phs_closed_loop"):
        start = text.index(f"def {fn}(")
        line_end = text.index("\n", start)
        assert expected_return in text[start:line_end], text[start:line_end]


def test_compound_return_type_overrides_dont_break_import_syntax(generated_typings):
    """A RETURN_OVERRIDES value can be a compound expression (a tuple of
    two proxies), not just a bare class name -- the import-collection
    logic must extract the individual *Proxy identifiers from it, not
    emit the whole expression string as a literal (invalid) import
    name. Covered structurally by the syntax-validity test elsewhere,
    but this pins down the exact mechanism so a future regression here
    fails with a clear message instead of a generic SyntaxError."""
    text = (generated_typings / "cesdm" / "domain" / "model" / "core.pyi").read_text(encoding="utf-8")
    assert "tuple[ReservoirStorageUnitProxy, HydroGenerationUnitProxy]," not in text.split("import (")[1].split(")")[0]
    assert "    ReservoirStorageUnitProxy,\n" in text
    assert "    HydroGenerationUnitProxy,\n" in text
