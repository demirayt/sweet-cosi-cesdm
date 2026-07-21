"""
resolve_inheritance() used to propagate abstract=True from a parent to
every descendant, no matter how many inheritance levels down — so
*every* class in the schema tree resolved to abstract=True (since
essentially everything traces back to an abstract root like
SemanticEntity or EnergyAssetInstance). Being a subclass of an
abstract base does not make the subclass abstract; that's the entire
point of an abstract base class.

This silently broke build_pydantic_models(), which only registers a
class in self.py_models when `not c.abstract` — so self.py_models was
always empty, for every class, including plain concrete leaf classes
like GenerationUnit. Found via a schema-audit tool built specifically
to surface this kind of issue; see CHANGELOG.md and
tools/schema_audit.py.
"""

from cesdm_toolbox import build_model_from_yaml
import pytest


def test_concrete_subclass_of_abstract_base_is_not_abstract():
    model = build_model_from_yaml("schemas")
    # EnergyAssetInstance is a genuine abstract base; GenerationUnit is a
    # concrete subclass of it and must not inherit abstract=True.
    assert model.classes["EnergyAssetInstance"].abstract is True
    assert model.classes["GenerationUnit"].abstract is False
    assert model.classes["ElectricalBus"].abstract is False
    assert model.classes["TransmissionLine"].abstract is False


def test_own_declared_abstract_flag_is_respected():
    model = build_model_from_yaml("schemas")
    # Classes that ARE declared abstract in their own schema file must
    # still resolve as abstract.
    assert model.classes["ResultView"].abstract is True
    assert model.classes["RunRecord"].abstract is True
    assert model.classes["DispatchResultView"].abstract is True
    # ...but their concrete leaf descendants must not be.
    assert model.classes["GenerationUnit.DispatchResultView"].abstract is False


def test_build_pydantic_models_is_not_empty():
    pytest.importorskip("pydantic")
    model = build_model_from_yaml("schemas")
    model.build_pydantic_models()
    assert len(model.py_models) > 50  # most of the ~103 classes are concrete
    assert "GenerationUnit" in model.py_models
    assert "EnergyAssetInstance" not in model.py_models  # abstract, correctly excluded
