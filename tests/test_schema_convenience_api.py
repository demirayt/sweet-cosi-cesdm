import inspect
import pytest

from cesdm_toolbox import build_model_from_yaml
from cesdm.proxy import AssetProxy


def test_every_concrete_entity_has_add_convenience_method():
    model = build_model_from_yaml("schemas")
    methods = model.available_add_methods()
    assert methods
    for method_name, class_name in methods.items():
        assert callable(getattr(model, method_name)), (method_name, class_name)


def test_required_attributes_are_required_signature_arguments():
    model = build_model_from_yaml("schemas")
    sig = inspect.signature(model.add_timestamp_series)
    for name in ("start_datetime", "resolution", "length"):
        assert name in sig.parameters
        assert sig.parameters[name].default is inspect.Parameter.empty


def test_generated_add_sets_attributes_and_returns_proxy():
    model = build_model_from_yaml("schemas")
    series = model.add_timestamp_series(
        "series.1", start_datetime="2025-01-01T00:00:00Z", resolution="PT1H", length=24
    )
    assert isinstance(series, AssetProxy)
    assert model.entity_class(series) == "TimestampSeries"
    assert model.get_attribute_value(series, "length") == 24


def test_missing_required_argument_fails_before_creation():
    model = build_model_from_yaml("schemas")
    with pytest.raises(TypeError, match="length"):
        model.add_timestamp_series("series.1", start_datetime="2025-01-01", resolution="PT1H")
    assert not model.has_entity("series.1")


def test_required_relations_are_in_signature():
    model = build_model_from_yaml("schemas")
    sig = inspect.signature(model.add_conversion_port)
    for name in ("belongsToUnit", "atNode", "hasCarrier"):
        assert sig.parameters[name].default is inspect.Parameter.empty


def test_generated_add_method_returns_entity_specific_proxy():
    from cesdm.generated_proxies import TimestampSeriesProxy

    model = build_model_from_yaml("schemas")
    result = model.add_timestamp_series(
        "series.generated.proxy",
        start_datetime="2026-01-01T00:00:00",
        resolution="PT1H",
        length=24,
    )

    assert isinstance(result, TimestampSeriesProxy)
    assert result.entity_class == "TimestampSeries"
